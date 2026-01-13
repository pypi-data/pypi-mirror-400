from pathlib import Path

from ewokscore import Task
from ewokscore.model import BaseInputModel
from ewokscore.model import BaseOutputModel
from pydantic import Field

from nxtomomill.converter import from_h5_to_nx, from_blissfluo_to_nx
from nxtomomill.models.h52nx import H52nxModel
from nxtomomill.models.blissfluo2nx import BlissFluo2nxModel


class H5ToNxInputModel(BaseInputModel):
    bliss_hdf5_path: str = Field(
        ..., description="Path to the Bliss-produced raw scan (.h5)."
    )
    nx_path: str = Field(
        ..., description="Target path for the generated .nx file (parent dir created)."
    )
    mechanical_ud_flip: bool = Field(
        False,
        description="Whether to add an nx-transformation to declare that the stack of projection needs to be flipped up-down.",
    )
    mechanical_lr_flip: bool = Field(
        False,
        description="Whether to add an nx-transformation to declare that the stack of projection needs to be flipped left-right.",
    )


class H5ToNxOutputModel(BaseOutputModel):
    nx_path: str = Field(..., description="Path to the created .nx file.")


class FluoToNxInputModel(BaseInputModel):
    bliss_hdf5_path: str = Field(
        ..., description="Path to the Bliss-produced raw XRFCT scan (.h5)."
    )
    nx_path: str = Field(
        ..., description="Target path for the generated .nx file (parent dir created)."
    )


class FluoToNxOutputModel(BaseOutputModel):
    nx_path: str = Field(..., description="Path to the created .nx file.")


class H5ToNx(  # type: ignore[call-arg]
    Task, input_model=H5ToNxInputModel, output_model=H5ToNxOutputModel
):
    def run(self):
        """
        (ESRF-only) Convert a Bliss tomography `.h5` scan into a NeXus `.nx` file using nxtomomill.
        """
        hdf5_path = Path(self.inputs.bliss_hdf5_path)
        nx_path_input = Path(self.inputs.nx_path)

        mechanical_ud_flip = self.inputs.mechanical_ud_flip
        mechanical_lr_flip = self.inputs.mechanical_lr_flip

        if not hdf5_path.is_file():
            raise FileNotFoundError(f"Input file not found: {hdf5_path}")

        output_file = nx_path_input
        output_file.parent.mkdir(parents=True, exist_ok=True)

        config = H52nxModel(
            mechanical_ud_flip=mechanical_ud_flip,
            mechanical_lr_flip=mechanical_lr_flip,
        )
        config.input_file = str(hdf5_path)
        config.output_file = str(output_file)
        config.single_file = True
        config.overwrite = True

        from_h5_to_nx(configuration=config)

        self.outputs.nx_path = str(output_file)


class FluoToNx(
    Task, input_model=FluoToNxInputModel, output_model=FluoToNxOutputModel
):  # type: ignore[call-arg]
    def run(self):
        """
        (ESRF-only) Converts a .h5 XRFCT scan into .nx format using the nxtomomill API.
        """
        hdf5_path = Path(self.inputs.bliss_hdf5_path)
        nx_path_input = Path(self.inputs.nx_path)

        if not hdf5_path.is_file():
            raise FileNotFoundError(f"Input file not found: {hdf5_path}")

        output_file = nx_path_input
        output_file.parent.mkdir(parents=True, exist_ok=True)

        config = BlissFluo2nxModel()
        config.general_section.ewoksfluo_filename = str(hdf5_path)
        config.general_section.output_file = str(output_file)
        config.general_section.file_extension = ".nx"

        from_blissfluo_to_nx(configuration=config, progress=None)

        self.outputs.nx_path = str(output_file)
