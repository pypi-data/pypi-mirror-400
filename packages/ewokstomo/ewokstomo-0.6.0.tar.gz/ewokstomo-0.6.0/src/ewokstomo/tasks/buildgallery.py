import logging
import os
import re
from pathlib import Path
import warnings
from typing import Any, Literal

import h5py
import numpy as np
from PIL import Image
from ewokscore import Task
from ewokscore.model import BaseInputModel
from ewokscore.model import BaseOutputModel
from pydantic import Field

from tomoscan.esrf.scan.nxtomoscan import NXtomoScan
from nabu.preproc.flatfield import FlatField


logger = logging.getLogger(__name__)


SAVE_KWARGS: dict[str, dict[str, Any]] = {
    "png": {"compress_level": 6, "optimize": True},
    "jpg": {"quality": 95, "subsampling": 0, "optimize": True},
    "jpeg": {"quality": 95, "subsampling": 0, "optimize": True},
    "webp": {"quality": 95, "method": 6},
}


def _auto_intensity_bounds(
    image: np.ndarray, lower_pct: float = 0.01, upper_pct: float = 99.99
) -> tuple[float, float]:
    """Compute robust lower/upper bounds for scaling to 8-bit."""
    finite = np.asarray(image, dtype=np.float32)
    finite = finite[np.isfinite(finite)]
    if finite.size == 0:
        return 0.0, 255.0

    upper_candidates = finite[finite < 1e9]
    if upper_candidates.size == 0:
        upper_candidates = finite

    lower = float(np.percentile(finite, lower_pct))
    upper = float(np.percentile(upper_candidates, upper_pct))
    if not np.isfinite(lower) or not np.isfinite(upper):
        return 0.0, 255.0
    if lower == upper:
        upper = lower + 1.0
    return lower, upper


def clean_angle_key(angle_key):
    """Convert angle key like '90.00000009(1)' to float, or leave float as is."""
    if isinstance(angle_key, float):
        return angle_key  # already clean
    cleaned = re.sub(r"\(.*?\)", "", angle_key)  # remove '(1)' etc.
    return float(cleaned)


def _save_kwargs_for_format(fmt: str) -> dict[str, Any]:
    """Return Pillow save options for reasonable compression without large quality loss."""
    fmt = fmt.lower().lstrip(".")
    return SAVE_KWARGS.get(fmt, {})


def _resize_preserve_aspect(img: Image.Image, target_size: int) -> Image.Image:
    """Resize to fit within target_size while preserving aspect ratio."""
    if max(img.size) <= target_size:
        return img
    scale = target_size / max(img.size)
    new_size = (
        max(1, int(round(img.size[0] * scale))),
        max(1, int(round(img.size[1] * scale))),
    )
    return img.resize(new_size, resample=Image.Resampling.LANCZOS)


class ProjectionsGalleryInputModel(BaseInputModel):
    nx_path: str = Field(..., description="Path to the input NX file.")
    reduced_darks_path: str = Field(
        ..., description="Path to the reduced dark frames HDF5 file."
    )
    reduced_flats_path: str = Field(
        ..., description="Path to the reduced flat frames HDF5 file."
    )
    bounds: tuple[float, float] = Field(
        None,
        description=(
            "Intensity bounds (min, max) for image normalization. "
            "If not provided, robust defaults are computed automatically."
        ),
    )
    angle_step: float = Field(
        90.0,
        description=(
            "Angular step in degrees for selecting projections to include in the gallery."
        ),
    )
    output_format: Literal["jpg", "png", "jpeg", "webp"] = Field(
        "jpg", description="Image format for gallery images (e.g., 'jpg', 'png')."
    )
    overwrite: bool = Field(
        True, description="Whether to overwrite existing gallery images."
    )
    image_size: int = Field(
        1000,
        description=(
            "Maximum size (in pixels) for the largest dimension of gallery images. "
            "Images larger than this will be downsampled."
        ),
    )


class ProjectionsGalleryOutputModel(BaseOutputModel):
    processed_data_dir: str = Field(
        ..., description="Directory containing the processed data."
    )
    gallery_path: str = Field(..., description="Path to the created gallery directory.")


class SlicesGalleryInputModel(BaseInputModel):
    reconstructed_slice_path: str = Field(
        ..., description="Path to the reconstructed slice file."
    )
    bounds: tuple[float, float] = Field(
        None,
        description=(
            "Intensity bounds (min, max) for image normalization. "
            "If not provided, robust defaults are computed automatically."
        ),
    )
    output_format: Literal["jpg", "png", "jpeg", "webp"] = Field(
        "jpg", description="Image format for gallery images (e.g., 'jpg', 'png')."
    )
    overwrite: bool = Field(
        True, description="Whether to overwrite existing gallery images."
    )
    image_size: int = Field(
        1000,
        description=(
            "Maximum size (in pixels) for the largest dimension of gallery images. "
            "Images larger than this will be downsampled."
        ),
    )


class SlicesGalleryOutputModel(BaseOutputModel):
    processed_data_dir: str = Field(
        ..., description="Directory containing the processed data."
    )
    gallery_path: str = Field(..., description="Path to the created gallery directory.")
    gallery_image_path: str = Field(
        ..., description="Path to the created gallery image."
    )


class BuildProjectionsGallery(  # type: ignore[call-arg]
    Task,
    input_model=ProjectionsGalleryInputModel,
    output_model=ProjectionsGalleryOutputModel,
):
    def run(self):
        """
        Creates a gallery of images from the NXtomoScan object.
        """

        self.gallery_output_format = str(self.inputs.output_format).lower()
        self.gallery_overwrite = self.inputs.overwrite
        self.gallery_image_size = int(self.inputs.image_size)
        bounds = self.inputs.bounds
        angle_step = self.inputs.angle_step

        # Use the directory of the output file as the processed data directory.
        nx_path = Path(self.inputs.nx_path)
        processed_data_dir = nx_path.parent
        gallery_dir = self.get_gallery_dir(processed_data_dir)
        os.makedirs(gallery_dir, exist_ok=True)

        # Open the NXtomoScan object.
        self.nxtomoscan = NXtomoScan(str(nx_path), entry="entry0000")

        angles, slices = self.get_slices_by_angle_step(angle_step)
        corrected_slices = self.flat_field_correction(slices)

        for angle, slice in zip(angles, corrected_slices):
            gallery_file_path = self.get_gallery_file_path(gallery_dir, nx_path, angle)
            Path(gallery_file_path).parent.mkdir(parents=True, exist_ok=True)

            # Process the image and save it in the gallery.
            self._save_to_gallery(gallery_file_path, slice, bounds)

        self._save_projections_gif(gallery_dir, nx_path, bounds)

        self.outputs.processed_data_dir = str(processed_data_dir)
        self.outputs.gallery_path = str(gallery_dir)

    def get_flats_from_h5(
        self, reduced_flat_path: str, data_path: str = "entry0000/flats"
    ) -> dict[int, np.ndarray]:
        """
        Loads the data from an HDF5 file.
        """
        with h5py.File(reduced_flat_path, "r") as h5f:
            for idx in h5f[data_path]:
                data = h5f[data_path][idx]
                flats_idx = int(idx)
                flats_data = data[()]
        return {flats_idx: flats_data}

    def get_darks_from_h5(
        self, reduced_dark_path: str, data_path: str = "entry0000/darks"
    ) -> dict[int, np.ndarray]:
        """
        Loads the data from an HDF5 file.
        """
        with h5py.File(reduced_dark_path, "r") as h5f:
            for idx in h5f[data_path]:
                data = h5f[data_path][idx]
                darks_idx = int(idx)
                darks_data = data[()]
        return {darks_idx: darks_data}

    def flat_field_correction(self, slices):
        """
        Applies flat field correction to the slices.
        """
        slices = np.asarray(slices, dtype=np.float32)
        reduced_darks = self.get_darks_from_h5(self.inputs.reduced_darks_path)
        reduced_flats = self.get_flats_from_h5(self.inputs.reduced_flats_path)
        x, y = slices[0].shape
        radios_shape = (len(slices), x, y)
        flat_field = FlatField(
            radios_shape=radios_shape, flats=reduced_flats, darks=reduced_darks
        )
        warnings.filterwarnings(
            "ignore",
            message=".*encountered in divide",
            category=RuntimeWarning,
            module="nabu.preproc.flatfield",
        )
        normalized_slices = flat_field.normalize_radios(slices)
        return normalized_slices

    def get_gallery_dir(self, processed_data_dir: Path) -> Path:
        return processed_data_dir / "gallery"

    def get_gallery_file_path(self, gallery_dir, nx_path: Path, angle: float) -> str:
        filename = f"{nx_path.stem}_{angle:.2f}deg.{self.gallery_output_format}"
        gallery_path = gallery_dir / filename
        return str(gallery_path)

    def get_proj_from_data_url(self, data_url) -> np.ndarray:
        """Load the data from a DataUrl object."""
        with h5py.File(data_url.file_path(), "r") as h5f:
            data = h5f[data_url.data_path()]
            if data_url.data_slice() is not None:
                return data[data_url.data_slice()].astype(np.float32)
            return data[()].astype(np.float32)

    def get_slices_by_angle_step(
        self, angle_step: float = 90
    ) -> tuple[list[float], list[np.ndarray]]:
        """
        Returns the slices of the image to be processed.
        """
        # Get all angles
        angles_dict = self.nxtomoscan.get_proj_angle_url()
        angles_dict = {clean_angle_key(k): v for k, v in angles_dict.items()}
        all_angles = np.array(list(angles_dict.keys()))

        # Determine all 90° targets within full range
        min_angle = np.min(all_angles)
        max_angle = np.max(all_angles)
        target_angles = np.arange(min_angle, max_angle + angle_step, angle_step)

        # For each target angle, find the closest available
        selected_angles = []
        used_indices = set()
        for target in target_angles:
            diffs = np.abs(all_angles - target)
            idx = np.argmin(diffs)
            if idx not in used_indices:  # avoid duplicates
                used_indices.add(idx)
                selected_angles.append(all_angles[idx])

        selected_slices = [
            self.get_proj_from_data_url(angles_dict[angle]) for angle in selected_angles
        ]
        return selected_angles, selected_slices

    def _save_to_gallery(
        self,
        output_file_name: str,
        image: np.ndarray,
        bounds: tuple[float, float] | None = None,
    ) -> None:
        """
        Processes and saves two images to the gallery folder:
          - If the image is 3D with a singleton first dimension, reshapes it to 2D.
          - Normalizes the image to 8-bit grayscale using the provided bounds if available.
            If no bounds are provided, lower_bound defaults to the 0.01st percentile of finite values and upper_bound to the 99.99th percentile of
            finite values below 1e9. This prevents negative slices from being clipped to zero while still ignoring saturated pixels.
          - Resizes (if needed) so the large image fits within the configured image_size (default 1000 px).
          - Saves the full-size result as `<name>_large` and a 200x200 resized version with the standard name.
        """
        overwrite = getattr(self, "gallery_overwrite", True)
        target_size = getattr(self, "gallery_image_size", 1000)

        output_path = Path(output_file_name)
        img = self._prepare_gallery_image(image, bounds, target_size)

        # Prepare save options (prefer lossless/visually lossless compression).
        fmt = getattr(self, "gallery_output_format", output_path.suffix.lstrip("."))
        if not fmt:
            fmt = "png"
        save_kwargs = _save_kwargs_for_format(fmt)

        # Build both output paths (full-size gets a `_large` suffix).
        large_output_path = output_path.with_name(
            f"{output_path.stem}_large{output_path.suffix}"
        )
        if not overwrite and (output_path.exists() or large_output_path.exists()):
            raise OSError(f"File already exists ({output_path})")

        # Save full-size (`_large`) image.
        img.save(str(large_output_path), **save_kwargs)

        # Save a smaller preview that preserves aspect ratio.
        img_small = _resize_preserve_aspect(img, target_size=200)
        img_small.save(str(output_path), **save_kwargs)

    def _prepare_gallery_image(
        self,
        image: np.ndarray,
        bounds: tuple[float, float] | None,
        target_size: int,
    ) -> Image.Image:
        # Ensure the image is 2D. If it's 3D with a single channel, squeeze it.
        if image.ndim == 3 and image.shape[0] == 1:
            image = image.reshape(image.shape[1:])
        elif image.ndim != 2:
            raise ValueError(f"Only 2D grayscale images are handled. Got {image.shape}")

        # Check if bounds is a valid tuple; otherwise derive robust defaults.
        if not isinstance(bounds, tuple):
            lower_bound, upper_bound = _auto_intensity_bounds(image)
        else:
            lower_bound = float(bounds[0])
            upper_bound = float(bounds[1])

        # Replace non-finite values before clamping to avoid all-black output.
        image = np.nan_to_num(
            image, nan=lower_bound, posinf=upper_bound, neginf=lower_bound
        )
        # Apply clamping and normalization.
        image = np.clip(image, lower_bound, upper_bound)
        image = image - lower_bound
        if upper_bound != lower_bound:
            image = image * (255.0 / (upper_bound - lower_bound))

        # Convert the image to a PIL Image.
        img = Image.fromarray(np.clip(image, 0, 255).astype(np.uint8), mode="L")

        # Resize if larger than target_size while keeping aspect ratio.
        img = _resize_preserve_aspect(img, target_size)

        return img

    def _save_projections_gif(
        self, gallery_dir: Path, nx_path: Path, bounds: tuple[float, float] | None
    ) -> None:
        gif_angle_step = 10.0
        gif_size = 200
        gif_fps = 12
        gif_duration = 1000

        angles, slices = self.get_slices_by_angle_step(gif_angle_step)
        if not angles:
            return
        corrected_slices = self.flat_field_correction(slices)

        frames = [
            self._prepare_gallery_image(slice, bounds, target_size=gif_size)
            for slice in corrected_slices
        ]

        if not frames:
            return

        gif_path = gallery_dir / f"{nx_path.stem}.gif"
        overwrite = getattr(self, "gallery_overwrite", True)
        if not overwrite and gif_path.exists():
            raise OSError(f"File already exists ({gif_path})")

        frames[0].save(
            gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=int(round(gif_duration / gif_fps)),
            loop=0,
        )


class BuildSlicesGallery(  # type: ignore[call-arg]
    Task,
    input_model=SlicesGalleryInputModel,
    output_model=SlicesGalleryOutputModel,
):
    """Create two gallery images from a reconstructed slice (full-size suffixed `_large`, and a 200x200 resized version).
    The large image is downsampled if needed so neither dimension exceeds the configured image_size (default 1000 px).
    """

    def run(self):
        """Read the slice, normalize/downsample, and save to <processed>/gallery."""
        fmt = str(self.inputs.output_format)
        overwrite = bool(self.inputs.overwrite)
        fmt = self.inputs.output_format
        overwrite = self.inputs.overwrite
        image_size = self.inputs.image_size
        bounds = self.inputs.bounds

        slice_path = Path(self.inputs.reconstructed_slice_path)
        if not slice_path.exists():
            raise FileNotFoundError(f"Reconstructed slice not found: {slice_path}")

        processed_data_dir = slice_path.parent
        gallery_dir = Path(processed_data_dir) / "gallery"
        os.makedirs(gallery_dir, exist_ok=True)

        arr = self._load_slice(slice_path)
        out_name = self.get_gallery_file_path(gallery_dir, slice_path, fmt)
        out_path = gallery_dir / out_name
        self._save_to_gallery(out_path, arr, bounds, overwrite, image_size)

        self.outputs.processed_data_dir = str(processed_data_dir)
        self.outputs.gallery_path = str(gallery_dir)
        self.outputs.gallery_image_path = str(out_path)

    def get_gallery_dir(self, processed_data_dir: Path | str) -> str:
        """Return the fixed gallery directory path."""
        return str(Path(processed_data_dir) / "gallery")

    def get_gallery_file_path(self, gallery_dir, reconstructed_slice_path, fmt) -> str:
        filename = f"{reconstructed_slice_path.stem}.{fmt}"
        gallery_path = gallery_dir / filename
        return str(gallery_path)

    @staticmethod
    def _load_slice(img_path: Path) -> np.ndarray:
        """Load a 2D float32 slice (HDF5 at entry0000/reconstruction/results/data, EDF, or image)."""
        ext = img_path.suffix.lower()
        if ext in (".h5", ".hdf5"):
            with h5py.File(img_path, "r") as h5in:
                img = h5in["entry0000/reconstruction/results/data"][:]
            return np.squeeze(img).astype(np.float32)
        if ext == ".edf":
            try:
                import fabio  # type: ignore
            except Exception as exc:
                raise RuntimeError(
                    "EDF support requires 'fabio' (pip install fabio)."
                ) from exc
            return fabio.open(str(img_path)).data.astype(np.float32)
        with Image.open(img_path) as im:
            arr = np.array(im, dtype=np.float32)
        if arr.ndim == 3 and arr.shape[-1] in (3, 4):
            arr = arr[..., :3].mean(axis=-1)
        return arr

    def _save_to_gallery(
        self,
        output_path: Path,
        image: np.ndarray,
        bounds: tuple[float, float] | None,
        overwrite: bool,
        image_size: int,
    ) -> None:
        """Clamp to bounds, scale to 8-bit, resize if larger than the requested size, then save both large_ and resized 200x200 images."""
        if image.ndim != 2:
            raise ValueError(
                f"Only 2D grayscale images are handled. Got shape={image.shape}"
            )
        if not isinstance(bounds, tuple):
            lower, upper = _auto_intensity_bounds(image)
        else:
            lower, upper = float(bounds[0]), float(bounds[1])
        img = np.clip(image, lower, upper) - lower
        scale = 255.0 / (upper - lower) if upper != lower else 1.0
        img = (img * scale).astype(np.float32)
        pil = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), mode="L")

        # Resize if larger than target image_size while keeping aspect ratio.
        if max(pil.size) > image_size:
            scale = image_size / max(pil.size)
            new_size = (
                max(1, int(round(pil.size[0] * scale))),
                max(1, int(round(pil.size[1] * scale))),
            )
            pil = pil.resize(new_size, resample=Image.Resampling.LANCZOS)
        fmt = output_path.suffix.lower().lstrip(".")
        save_kwargs = _save_kwargs_for_format(fmt)

        large_output_path = output_path.with_name(
            f"{output_path.stem}_large{output_path.suffix}"
        )
        if not overwrite and (output_path.exists() or large_output_path.exists()):
            raise OSError(f"File already exists ({output_path})")

        # Save full-size (`_large`) image.
        pil.save(str(large_output_path), **save_kwargs)

        # Save a smaller preview that preserves aspect ratio.
        pil_small = _resize_preserve_aspect(pil, target_size=200)
        pil_small.save(str(output_path), **save_kwargs)
