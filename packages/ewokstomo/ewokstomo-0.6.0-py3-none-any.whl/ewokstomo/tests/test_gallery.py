import shutil
from pathlib import Path

import pytest
import numpy as np
from PIL import Image

from ewokstomo.tasks.buildgallery import (
    BuildProjectionsGallery,
    BuildSlicesGallery,
    _auto_intensity_bounds,
)


DATA_ROOT = Path(__file__).resolve().parent / "data"
SCAN_COLLECTION = "TestEwoksTomo"


def get_data_dir(scan_name: str) -> Path:
    return DATA_ROOT / "PROCESSED_DATA" / SCAN_COLLECTION / scan_name


@pytest.fixture
def tmp_dataset_path(tmp_path) -> Path:
    src_dir = get_data_dir("TestEwoksTomo_0010")
    dst_dir = tmp_path / "TestEwoksTomo_0010"
    shutil.copytree(src_dir, dst_dir)
    proj_dir = dst_dir / "projections"
    slices_dir = dst_dir / "slices"
    # remove any existing darks/flats and gallery
    for pattern in ("*_darks.hdf5", "*_flats.hdf5"):
        for f in proj_dir.glob(pattern):
            f.unlink()
    for gallery_parent in (proj_dir, slices_dir):
        gallery = gallery_parent / "gallery"
        if gallery.exists():
            shutil.rmtree(gallery)
    references_dir = dst_dir / "references"
    if references_dir.exists():
        shutil.rmtree(references_dir)
    # generate fresh darks/flats
    from ewokstomo.tasks.reducedarkflat import ReduceDarkFlat

    nx = proj_dir / "TestEwoksTomo_0010.nx"
    rd_task = ReduceDarkFlat(
        inputs={
            "nx_path": str(nx),
            "dark_reduction_method": "mean",
            "flat_reduction_method": "median",
            "overwrite": True,
            "return_info": False,
        },
    )
    rd_task.execute()
    return dst_dir


@pytest.fixture
def simple_image() -> np.ndarray:
    return np.linspace(0, 255, num=100, dtype=float).reshape((10, 10))


def test_auto_bounds_handles_negative_values():
    data = np.linspace(-1000.0, 1000.0, num=10000, dtype=float).reshape((100, 100))
    lower, upper = _auto_intensity_bounds(data)
    assert np.isclose(lower, np.percentile(data, 0.01))
    assert np.isclose(upper, np.percentile(data, 99.99))
    assert lower < 0.0 < upper


@pytest.mark.order(5)
@pytest.mark.parametrize("Task", [BuildProjectionsGallery])
def test_buildgallery_task(Task, tmp_dataset_path):
    proj_dir = tmp_dataset_path / "projections"
    nx = proj_dir / "TestEwoksTomo_0010.nx"
    refs_dir = tmp_dataset_path / "references"
    dataset_name = nx.stem
    darks = refs_dir / f"{dataset_name}_darks.hdf5"
    flats = refs_dir / f"{dataset_name}_flats.hdf5"
    task = Task(
        inputs={
            "nx_path": str(nx),
            "reduced_darks_path": str(darks),
            "reduced_flats_path": str(flats),
            "output_format": "png",
        },
    )
    task.execute()
    gallery_dir = Path(task.outputs.processed_data_dir) / "gallery"
    assert gallery_dir.exists(), "Gallery directory does not exist"
    assert gallery_dir.is_dir(), "Gallery path is not a directory"

    small_images = sorted(
        p for p in gallery_dir.glob("*.png") if not p.name.endswith("_large.png")
    )
    large_images = sorted(gallery_dir.glob("*_large.png"))
    assert len(small_images) == 5, f"Expected 5 small images, found {len(small_images)}"
    assert len(large_images) == 5, f"Expected 5 large images, found {len(large_images)}"

    gif_path = gallery_dir / f"{nx.stem}.gif"
    assert gif_path.exists(), "Projections GIF does not exist"
    with Image.open(gif_path) as gif:
        assert gif.format == "GIF", "Projections GIF is not a valid GIF image"
        assert gif.size == (16, 16), "Projections GIF is not 16x16"
        assert getattr(gif, "n_frames", 1) >= 1, "Projections GIF has too few frames"
        colors = gif.getcolors(maxcolors=256)
        assert colors is not None, "Projections GIF palette is missing"
        assert len(colors) <= 32, "Projections GIF exceeds 32 colors"

    for img_path in small_images:
        with Image.open(img_path) as img:
            assert img.format == "PNG", f"{img_path.name} is not a valid PNG image"
            assert img.mode == "L", f"{img_path.name} is not grayscale"
            assert img.size == (16, 16), f"{img_path.name} not resized to 16x16"

            arr = np.array(img)
            assert arr.dtype == np.uint8, f"{img_path.name} not saved as 8-bit"
            assert (
                arr.max() <= 255 and arr.min() >= 0
            ), f"{img_path.name} has out-of-bound pixel values"

    for img_path in large_images:
        with Image.open(img_path) as img:
            assert img.format == "PNG", f"{img_path.name} is not a valid PNG image"
            assert img.mode == "L", f"{img_path.name} is not grayscale"
            assert (
                img.size[0] > 0 and img.size[1] > 0
            ), f"{img_path.name} has invalid dimensions"
            assert (
                max(img.size) <= 1000
            ), f"{img_path.name} exceeds the maximum expected dimension"


@pytest.mark.order(6)
def test_save_to_gallery_bounds(simple_image, tmp_path, tmp_dataset_path):
    proj_dir = tmp_dataset_path / "projections"
    nx = proj_dir / "TestEwoksTomo_0010.nx"
    output_file = tmp_path / "image_bounds_00000.png"
    refs_dir = tmp_dataset_path / "references"
    dataset_name = nx.stem
    task = BuildProjectionsGallery(
        inputs={
            "nx_path": str(nx),
            "reduced_darks_path": str(refs_dir / f"{dataset_name}_darks.hdf5"),
            "reduced_flats_path": str(refs_dir / f"{dataset_name}_flats.hdf5"),
            "bounds": (50.0, 200.0),
            "output_format": "png",
        },
    )
    task.gallery_overwrite = True
    task._save_to_gallery(output_file, simple_image)
    large_output_file = output_file.with_name(
        f"{output_file.stem}_large{output_file.suffix}"
    )
    assert output_file.exists(), "Resized gallery file was not created"
    assert large_output_file.exists(), "Large gallery file was not created"
    with Image.open(output_file) as im:
        assert im.size == (10, 10)


@pytest.mark.order(7)
@pytest.mark.parametrize("angle_step,expected_count", [(45, 9), (90, 5), (180, 3)])
def test_buildgallery_angles(angle_step, expected_count, tmp_dataset_path):
    proj_dir = tmp_dataset_path / "projections"
    nx = proj_dir / "TestEwoksTomo_0010.nx"
    refs_dir = tmp_dataset_path / "references"
    dataset_name = nx.stem
    darks = refs_dir / f"{dataset_name}_darks.hdf5"
    flats = refs_dir / f"{dataset_name}_flats.hdf5"
    gallery_dir = proj_dir / "gallery"
    if gallery_dir.exists():
        shutil.rmtree(gallery_dir)
    task = BuildProjectionsGallery(
        inputs={
            "nx_path": str(nx),
            "reduced_darks_path": str(darks),
            "reduced_flats_path": str(flats),
            "angle_step": angle_step,
            "output_format": "png",
        },
    )
    task.execute()
    small_images = list(
        p for p in gallery_dir.glob("*.png") if not p.name.endswith("_large.png")
    )
    large_images = list(gallery_dir.glob("*_large.png"))
    assert (
        len(small_images) == expected_count
    ), f"Expected {expected_count} resized images, found {len(small_images)}"
    assert (
        len(large_images) == expected_count
    ), f"Expected {expected_count} large images, found {len(large_images)}"

    gif_path = gallery_dir / f"{nx.stem}.gif"
    assert gif_path.exists(), "Projections GIF does not exist"


def _expected_slice_path(root: Path) -> Path:
    return (
        root
        / "slices"
        / "TestEwoksTomo_0010slice_000008_plane_XY"
        / "TestEwoksTomo_0010slice_000008_plane_XY_00008.hdf5"
    )


@pytest.mark.order(11)
def test_buildslicesgallery_creates_one_image(tmp_dataset_path):
    slices_gallery_dir = tmp_dataset_path / "slices" / "gallery"
    if slices_gallery_dir.exists():
        shutil.rmtree(slices_gallery_dir)

    slice_path = _expected_slice_path(tmp_dataset_path)
    assert slice_path.exists(), f"Missing test input: {slice_path}"

    task = BuildSlicesGallery(
        inputs={
            "reconstructed_slice_path": str(slice_path),
            "output_format": "png",
            "overwrite": True,
            "image_size": 1000,
        }
    )
    task.execute()

    processed_dir = Path(task.outputs.processed_data_dir)
    out_gallery = Path(task.outputs.gallery_path)
    out_image = Path(task.outputs.gallery_image_path)
    large_image = out_image.with_name(f"{out_image.stem}_large{out_image.suffix}")

    assert out_gallery == processed_dir / "gallery"
    assert out_gallery.exists() and out_gallery.is_dir()

    assert out_image.name == f"{slice_path.stem}.png"
    assert out_image.exists()
    assert large_image.exists()

    with Image.open(out_image) as im:
        assert im.format == "PNG"
        assert im.mode == "L"
        assert im.size == (16, 16)
        arr = np.array(im)
        assert arr.dtype == np.uint8
        assert 0 <= arr.min() <= 255 and 0 <= arr.max() <= 255
        assert len(np.unique(arr)) > 1
    with Image.open(large_image) as im_large:
        assert (
            max(im_large.size) <= 1000
        ), "Large gallery image exceeds the maximum expected dimension"


@pytest.mark.order(12)
def test_buildslicesgallery_overwrite_guard(tmp_dataset_path):
    slices_gallery_dir = tmp_dataset_path / "slices" / "gallery"
    if slices_gallery_dir.exists():
        shutil.rmtree(slices_gallery_dir)

    slice_path = _expected_slice_path(tmp_dataset_path)

    # First run creates the image
    BuildSlicesGallery(
        inputs={
            "reconstructed_slice_path": str(slice_path),
            "output_format": "png",
            "overwrite": True,
        }
    ).execute()

    # Second run with overwrite disabled must raise
    task = BuildSlicesGallery(
        inputs={
            "reconstructed_slice_path": str(slice_path),
            "output_format": "png",
            "overwrite": False,
        }
    )
    with pytest.raises(RuntimeError):
        task.execute()


@pytest.mark.order(13)
def test_buildslicesgallery_bounds_and_resize(tmp_dataset_path):
    slices_gallery_dir = tmp_dataset_path / "slices" / "gallery"
    if slices_gallery_dir.exists():
        shutil.rmtree(slices_gallery_dir)

    slice_path = _expected_slice_path(tmp_dataset_path)

    task = BuildSlicesGallery(
        inputs={
            "reconstructed_slice_path": str(slice_path),
            "output_format": "png",
            "overwrite": True,
            "bounds": (50.0, 200.0),
            "image_size": 1000,
        }
    )
    task.execute()

    processed_dir = Path(task.outputs.processed_data_dir)
    assert task.get_gallery_dir(processed_dir) == str(processed_dir / "gallery")

    out_image = Path(task.outputs.gallery_image_path)
    large_image = out_image.with_name(f"{out_image.stem}_large{out_image.suffix}")
    assert out_image.exists()
    assert large_image.exists()
    with Image.open(out_image) as im:
        assert im.format == "PNG"
        assert im.mode == "L"
        assert im.size == (16, 16)
        arr = np.array(im)
        assert arr.min() >= 0 and arr.max() <= 255
        assert len(np.unique(arr)) >= 2
        assert (arr.max() - arr.min()) >= 32
    with Image.open(large_image) as im_large:
        assert (
            max(im_large.size) <= 1000
        ), "Large gallery image exceeds the maximum expected dimension"
