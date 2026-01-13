from __future__ import annotations
from typing import Any
import logging

from ewokscore import Task
from ewokscore.model import BaseInputModel
from ewokscore.model import BaseOutputModel
from pydantic import Field
from esrf_pathlib import ESRFPath
from pyicat_plus.client.main import IcatClient
from pyicat_plus.client import defaults
from esrf_ontologies import technique

logger = logging.getLogger(__name__)


def _build_icat_payload(
    folder_path: str,
    metadata_in: dict[str, Any] | None,
    dataset_in: str | None = None,
) -> dict[str, Any]:
    """Parse the path, normalize metadata, and return the ICAT call payload."""
    processed_path = ESRFPath(folder_path)

    if processed_path.schema_name is None:
        raise ValueError(f"Unknown ESRF path schema: {folder_path}")
    if processed_path.data_type != "PROCESSED_DATA":
        raise ValueError(f"Not a PROCESSED_DATA path: {folder_path}")

    dataset = processed_path.dataset if dataset_in is None else dataset_in

    if metadata_in is None:
        metadata = {"Sample_name": processed_path.collection}
    else:
        metadata = dict(metadata_in)
        metadata.setdefault("Sample_name", processed_path.collection)

    dataset_lower = str(dataset).lower()
    if dataset_lower in {"slices", "projections"}:
        metadata["workflow_type"] = dataset_lower

    return {
        "beamline": processed_path.beamline,
        "proposal": processed_path.proposal,
        "dataset": dataset,
        "path": str(processed_path),
        "raw": [str(processed_path.raw_dataset_path)],
        "metadata": metadata,
    }


def _build_dataportal_metadata(
    processing_options: dict[str, Any] | None,
) -> dict[str, Any]:
    """Convert processing options into Data Portal metadata."""
    if not isinstance(processing_options, dict):
        processing_options = {}

    metadata: dict[str, Any] = {"workflow_type": "slices"}

    reconstruction_values = processing_options.get("reconstruction", {})
    excluded_recon_keys = {
        "crop_filtered_data",
        "hbp_legs",
        "hbp_reduction_steps",
        "iterations",
        "outer_circle_value",
    }
    if isinstance(reconstruction_values, dict):

        for key, value in reconstruction_values.items():
            if key in excluded_recon_keys:
                continue
            if isinstance(value, str):
                value = value.strip()
            if value is None:
                continue
            if isinstance(value, str) and value == "":
                continue
            metadata[f"TOMOReconstruction_{key}"] = value

    phase_values = processing_options.get("phase", {})

    phase_method = None
    if isinstance(phase_values, dict):
        phase_method = phase_values.get("method")
        if isinstance(phase_method, str):
            phase_method = phase_method.strip()
            if phase_method.lower() == "none":
                phase_method = ""

        for key, value in phase_values.items():
            if isinstance(value, str):
                value = value.strip()
            if value is None:
                continue
            if isinstance(value, str) and value == "":
                continue
            metadata[f"TOMOReconstructionPhase_{key}"] = value

    if phase_method not in (None, ""):
        technique_metadata = technique.get_technique_metadata("XPCT")
        metadata.update(technique_metadata.get_dataset_metadata())

    return metadata


class BuildDataPortalMetadataInputModel(BaseInputModel):
    processing_options: dict[str, Any] | None = Field(
        default=None,
        description="Nabu processing options dictionary to convert into Data Portal metadata.",
    )


class BuildDataPortalMetadataOutputModel(BaseOutputModel):
    dataportal_metadata: dict[str, Any] = Field(
        ...,
        description="Generated Data Portal metadata dictionary.",
    )


class DataPortalUploadInputModel(BaseInputModel):
    process_folder_path: str = Field(
        ...,
        description="Path to the processed dataset folder to upload.",
    )
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Optional metadata dictionary to include in the upload.",
    )
    dry_run: bool = Field(
        default=False,
        description="If True, simulate the upload without performing it.",
    )
    dataset: str | None = Field(
        default=None,
        description="Optional dataset name to use for the upload.",
    )


class BuildDataPortalMetadata(  # type: ignore[call-arg]
    Task,
    input_model=BuildDataPortalMetadataInputModel,
    output_model=BuildDataPortalMetadataOutputModel,
):
    """(ESRF-only) Convert Nabu processing options into Data Portal metadata."""

    def run(self):
        processing_options = self.inputs.processing_options
        if not isinstance(processing_options, dict):
            logger.warning("Invalid processing_options provided; using empty metadata")
            processing_options = None

        self.outputs.dataportal_metadata = _build_dataportal_metadata(
            processing_options
        )


class DataPortalUpload(  # type: ignore[call-arg]
    Task,
    input_model=DataPortalUploadInputModel,
):
    """(ESRF-only) Upload a processed dataset folder to the Data Portal using pyicat_plus."""

    icat_client_factory = staticmethod(
        lambda: IcatClient(metadata_urls=defaults.METADATA_BROKERS)
    )

    def run(self):
        folder_path = self.inputs.process_folder_path
        metadata_in = self.inputs.metadata
        dataset_in = self.inputs.dataset
        dry_run = self.inputs.dry_run

        try:
            payload = _build_icat_payload(folder_path, metadata_in, dataset_in)

            if dry_run:
                logger.info(
                    "Dry-run: would store_processed_data "
                    "proposal=%s beamline=%s dataset=%s path=%s raw=%s metadata=%s",
                    payload["proposal"],
                    payload["beamline"],
                    payload["dataset"],
                    payload["path"],
                    payload["raw"],
                    payload["metadata"],
                    extra={"dp_payload": payload},
                )
                return

            client = self.icat_client_factory()
            try:
                client.store_processed_data(**payload)
                self.icat_status = "stored"
            finally:
                try:
                    client.disconnect()
                except Exception:
                    logger.warning("Failed to disconnect ICAT client")

        except ValueError as e:
            logger.warning("DataPortalUpload skipped: %s", e)
        except Exception as e:
            logger.warning("Error in DataPortalUpload: %s", e)
