from pathlib import Path

import numpy
from ewokscore import Task
from silx.io.url import DataUrl
from tomoscan.esrf.scan.nxtomoscan import NXtomoScan

from ewokscore.model import BaseInputModel
from ewokscore.model import BaseOutputModel
from pydantic import Field


class ReduceDarkFlatInputModel(BaseInputModel):
    nx_path: str = Field(
        ...,
        description="Path to the input NX file.",
    )
    dark_reduction_method: str = Field(
        "mean",
        description="Method to reduce dark frames ('mean' or 'median').",
    )
    flat_reduction_method: str = Field(
        "median",
        description="Method to reduce flat frames ('mean' or 'median').",
    )
    overwrite: bool = Field(
        True,
        description="Whether to overwrite existing reduced files.",
    )
    output_dtype: type = Field(
        numpy.float32,
        description="Data type for the output reduced frames.",
    )
    return_info: bool = Field(
        False,
        description="Whether to return additional info from reduction.",
    )
    reference_dir_to_soft_link: str = Field(
        None,
        description="Directory from which the reduced darks and flats will be linked. If provided, reduction is skipped.",
    )


class ReduceDarkFlatOutputModel(BaseOutputModel):
    reduced_darks_path: str = Field(
        ...,
        description="Path to the reduced dark frames file.",
    )
    reduced_flats_path: str = Field(
        ...,
        description="Path to the reduced flat frames file.",
    )


class ReduceDarkFlat(  # type: ignore[call-arg]
    Task,
    input_model=ReduceDarkFlatInputModel,
    output_model=ReduceDarkFlatOutputModel,
):
    def run(self):
        """
        Reduce the dark and flat frames of the input NX file.
        """

        nx_path = Path(self.inputs.nx_path).resolve()
        base_name = nx_path.stem
        reference_dir_to_soft_link = self.inputs.reference_dir_to_soft_link
        overwrite = self.inputs.overwrite

        references_dir = nx_path.parent.parent / "references"
        references_dir.mkdir(parents=True, exist_ok=True)

        dark_file = references_dir / f"{base_name}_darks.hdf5"
        flat_file = references_dir / f"{base_name}_flats.hdf5"

        if reference_dir_to_soft_link is not None:
            darks_in_dir = list(Path(reference_dir_to_soft_link).glob("*_darks.hdf5"))
            flats_in_dir = list(Path(reference_dir_to_soft_link).glob("*_flats.hdf5"))
            if len(darks_in_dir) == 0 or len(flats_in_dir) == 0:
                raise FileNotFoundError(
                    f"No reduced darks or flats found in the specified directory: {reference_dir_to_soft_link}"
                )
            for target, source in (
                (dark_file, darks_in_dir[0]),
                (flat_file, flats_in_dir[0]),
            ):
                if target.exists():
                    if overwrite:
                        target.unlink()
                    else:
                        raise FileExistsError(
                            f"File {target} already exists and overwrite is False"
                        )
                target.symlink_to(Path(source).resolve())

            self.outputs.reduced_darks_path = str(dark_file)
            self.outputs.reduced_flats_path = str(flat_file)
            return

        d_reduction_method = self.inputs.dark_reduction_method
        f_reduction_method = self.inputs.flat_reduction_method
        output_dtype = self.inputs.output_dtype
        return_info = self.inputs.return_info

        scan = NXtomoScan(str(nx_path), entry="entry0000")

        reduced_dark = scan.compute_reduced_darks(
            reduced_method=d_reduction_method,
            overwrite=overwrite,
            output_dtype=output_dtype,
            return_info=return_info,
        )
        reduced_flat = scan.compute_reduced_flats(
            reduced_method=f_reduction_method,
            overwrite=overwrite,
            output_dtype=output_dtype,
            return_info=return_info,
        )

        dark_urls = (
            DataUrl(
                file_path=str(dark_file),
                data_path="{entry}/darks/{index}",
                scheme=NXtomoScan.SCHEME,
            ),
        )
        dark_metadata_urls = (
            DataUrl(
                file_path=str(dark_file),
                data_path="{entry}/darks/",
                scheme=NXtomoScan.SCHEME,
            ),
        )
        flat_urls = (
            DataUrl(
                file_path=str(flat_file),
                data_path="{entry}/flats/{index}",
                scheme=NXtomoScan.SCHEME,
            ),
        )
        flat_metadata_urls = (
            DataUrl(
                file_path=str(flat_file),
                data_path="{entry}/flats/",
                scheme=NXtomoScan.SCHEME,
            ),
        )

        scan.save_reduced_darks(
            reduced_dark,
            overwrite=overwrite,
            output_urls=dark_urls,
            metadata_output_urls=dark_metadata_urls,
        )
        scan.save_reduced_flats(
            reduced_flat,
            overwrite=overwrite,
            output_urls=flat_urls,
            metadata_output_urls=flat_metadata_urls,
        )

        self.outputs.reduced_darks_path = str(dark_file)
        self.outputs.reduced_flats_path = str(flat_file)
