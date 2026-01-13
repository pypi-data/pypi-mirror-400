from pathlib import Path
import warnings
from typing import Any, Literal

from ewokscore import Task
from ewokscore.model import BaseInputModel
from ewokscore.model import BaseOutputModel
from pydantic import Field


class ReconstructSliceInputModel(BaseInputModel):
    nx_path: str = Field(..., description="Path to the input NX file.")
    config_dict: dict[str, Any] = Field(
        ...,
        description=(
            "Configuration dictionary for Nabu. Must include at least "
            '"dataset" -> "location", pointing to the input NX file.'
            "(see https://www.silx.org/pub/nabu/doc/nabu_config_items.html)"
        ),
    )
    slice_index: int | Literal["first", "middle", "last"] = Field(
        "middle",
        description=(
            "Index of the slice to reconstruct. Accepts an integer or one of the fixed strings: "
            '"first", "middle", "last".'
        ),
    )


class ReconstructSliceOutputModel(BaseOutputModel):
    reconstructed_slice_path: str = Field(
        ..., description="Path to the saved reconstructed slice."
    )
    slice_index: int = Field(..., description="Index of the reconstructed slice.")
    nabu_dict: dict = Field(
        ..., description="Nabu configuration dictionary used for reconstruction."
    )
    processing_options: dict = Field(
        ..., description="Resolved Nabu processing options used by ProcessConfig."
    )


class ReconstructSlice(  # type: ignore[call-arg]
    Task,
    input_model=ReconstructSliceInputModel,
    output_model=ReconstructSliceOutputModel,
):
    def run(self):
        """
        Task that reconstructs a single slice from full-field tomography data using Nabu:

        - Accepts a configuration dictionary for Nabu and a slice index.
        - Generates a Nabu configuration file with adjusted start and end z indices to reconstruct only one slice.
        - Runs Nabu to perform the reconstruction.
        - Saves the resulting slice to disk in a subfolder named "slices" located at the scan root (sibling of the `projections` directory).
        - Outputs both the path to the saved reconstructed slice and the in-memory numpy array of the slice.
        """
        warnings.filterwarnings(
            "ignore",
            message="invalid value encountered in divide",
            category=RuntimeWarning,
            module="nabu\\.preproc\\.flatfield",
        )
        from nabu.pipeline.fullfield.reconstruction import FullFieldReconstructor
        from nabu.pipeline.fullfield.processconfig import ProcessConfig

        overwritten_config_fields = self.get_input_value("config_dict")
        input_slice_index = self.get_input_value("slice_index", "middle")
        nx_path = Path(self.get_input_value("nx_path"))

        if not nx_path.exists():
            raise FileNotFoundError(f"NX file not found: {nx_path}")

        output_dir = nx_path.parent.parent / "slices"
        output_dir.mkdir(exist_ok=True)

        technique = _get_technique_from_nabu_config(overwritten_config_fields)

        # Prepare the configuration for nabu
        overwritten_config_fields["dataset"]["location"] = str(nx_path)
        overwritten_config_fields["reconstruction"]["start_z"] = input_slice_index
        overwritten_config_fields["reconstruction"]["end_z"] = input_slice_index
        overwritten_config_fields["output"]["location"] = str(output_dir)

        proc = ProcessConfig(conf_dict=overwritten_config_fields)

        slice_index = proc.processing_options["reconstruction"]["start_z"]
        file_prefix = f"{nx_path.stem}_{technique}_xy_{slice_index:05d}"
        proc.processing_options["save"]["file_prefix"] = file_prefix
        proc.nabu_config["output"]["file_prefix"] = file_prefix
        overwritten_config_fields["output"]["file_prefix"] = file_prefix

        reconstructor = FullFieldReconstructor(proc)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            reconstructor.reconstruct()
        reconstructor.finalize_files_saving()
        save_options = proc.processing_options["save"]
        self.outputs.reconstructed_slice_path = str(
            Path(save_options["location"])
            / f"{save_options['file_prefix']}.{save_options['file_format']}"
        )
        self.outputs.slice_index = slice_index
        self.outputs.nabu_dict = overwritten_config_fields
        self.outputs.processing_options = proc.processing_options


def _get_technique_from_nabu_config(nabu_config: dict[str, dict[str, str]]) -> str:
    """Extract the technique from the Nabu configuration dictionary."""
    method = nabu_config.get("method")
    technique = "absorption"
    if isinstance(method, str):
        if method in ("Paganin", "CTF"):
            technique = "phase"
    return technique
