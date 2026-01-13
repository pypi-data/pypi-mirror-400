"""
Online reconstruction tasks for real-time tomography processing.

This module provides tasks and utilities for performing tomographic
reconstruction in real-time as data is acquired from the beamline.
"""

import logging
import numpy as np
import time
import warnings
from typing import Any
from pathlib import Path
import h5py
from ewokscore import Task
from nabu.cuda.utils import __has_cupy__

if __has_cupy__:
    from nabu.reconstruction.fbp import CudaBackprojector as Backprojector
else:
    from nabu.reconstruction.fbp_opencl import OpenCLBackprojector as Backprojector
from blissdata.redis_engine.store import DataStore
from blissdata.beacon.data import BeaconData
from blissdata.redis_engine.scan import ScanState
from ewokstomo.tasks.utils import wait_for_scan_state
from ewokstomo.tasks.online.preprocessing import FlatFieldCorrection
from ewokstomo.tasks.online.preprocessing import apply_phase_retrieval

logger = logging.getLogger(__name__)
if __has_cupy__:
    logger.info("Using CUDA for reconstruction")
else:
    logger.info("Using OpenCL for reconstruction")
STREAM_TIMEOUT = 5  # seconds to wait for new data after scan stops
WAITING_INTERVAL = 1  # seconds between checks for new data


def get_slice_index(slice_index: int | str, n_z: int) -> int:
    """Get the slice index based on input."""
    if isinstance(slice_index, int):
        return slice_index
    elif isinstance(slice_index, str) and slice_index.lower() == "middle":
        return n_z // 2
    elif isinstance(slice_index, str) and slice_index.lower() == "last":
        return n_z - 1
    elif isinstance(slice_index, str) and slice_index.lower() == "first":
        return 0
    else:
        raise ValueError(f"Invalid slice index: {slice_index}")


def fbp_reconstruction_slice(
    projections: np.ndarray,
    angles: np.ndarray,
    rotation_center: float,
    slice_index: int | str | None = None,
    halftomo: bool = False,
    padding_mode: str = "edges",
    extra_options: dict[str, Any] | None = None,
):
    """Perform FBP reconstruction on a single slice.

    Reconstructs only one horizontal slice from the projection stack,
    useful for quick preview or center of rotation determination.

    Parameters
    ----------
    projections : np.ndarray
        Array of projections with shape (n_angles, n_z, n_x)
    angles : np.ndarray
        Rotation angles in radians
    rotation_center : float
        Rotation axis position
    slice_index : int, optional
        Index of the slice to reconstruct. If None, uses the middle slice.
        Default is None.
    halftomo : bool, optional
        If True, assumes half-tomography acquisition. Default is False.
    padding_mode : str, optional
        Padding mode for sinogram extension. Default is 'edges'.
    extra_options : dict, optional
        Additional options for the backprojector.
        Default is {'centered_axis': True}.
    """

    n_a, n_z, n_x = projections.shape
    logger.info(f"Reconstructing {n_a} projections with CoR={rotation_center:.3f}")

    # Use middle slice if not specified
    if slice_index is None:
        slice_index = get_slice_index(slice_index="middle", n_z=n_z)
    else:
        slice_index = get_slice_index(slice_index, n_z=n_z)

    logger.info(
        f"Reconstructing slice {slice_index}/{n_z} from {n_a} projections "
        f"with CoR={rotation_center:.3f}"
    )

    sino_shape = (n_a, n_x)
    sino = np.ascontiguousarray(projections[:, slice_index, :])
    options: dict[str, Any] = {"centered_axis": True}
    if extra_options:
        options.update(extra_options)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        fbp = Backprojector(
            sino_shape,
            angles=angles,
            rot_center=rotation_center,
            halftomo=halftomo,
            padding_mode=padding_mode,
            extra_options=options,
        )

    reconstructed_slice = fbp.fbp(sino)

    logger.info(f"Reconstruction completed. Output shape: {reconstructed_slice.shape}")
    return reconstructed_slice


class OnlineReconstructSlice(  # type: ignore[call-arg]
    Task,
    input_names=[
        "scan_key",
        "output_path",
        "rotation_motor",
        "total_nb_projection",
        "center_of_rotation",
        "batch_size",
        "reduced_dark_path",
        "reduced_flat_path",
        "pixel_size_m",
        "distance_m",
        "energy_keV",
    ],
    optional_input_names=[
        "delta_beta",
        "halftomo",
        "padding_mode",
        "extra_options",
        "slice_index",
    ],
    output_names=["reconstructed_slices_directory"],
):
    """
    (ESRF-only) Perform real-time tomography reconstruction on streaming data.

    This task connects to a live scan stream and performs incremental
    reconstruction by processing projections in batches. It includes
    flat field correction, phase retrieval, and FBP reconstruction.

    The reconstruction is performed on a single slice (middle by default) to minimize
    computational cost while providing real-time feedback.

    Required Inputs
    ---------------
    scan_key : str
        Blissdata scan key for accessing the live stream
    output_path : str
        Directory path where reconstructed slice files will be saved.
        Individual batch results are saved as reconstructed_slice_{start}_{end}.h5
    rotation_motor : str
        Name of the rotation axis motor in the scan
    total_nb_projection : int
        Total expected number of projections in the scan
    center_of_rotation : float
        Center of rotation position
    batch_size : int
        Number of projections to process in each batch, default is 100
    reduced_dark_path : str
        Path to HDF5 file containing reduced dark frames
    reduced_flat_path : str
        Path to HDF5 file containing reduced flat frames
    distance_m:
        Effective propagation distance (m)
    energy_keV:
        Energy (keV)
    pixel_size_m:
        detector pixel size (m)

    Optional Inputs
    ---------------
    delta_beta : float
        Delta/beta ratio for Paganin phase retrieval. Default is 100.
    halftomo : bool
        Whether the scan is a half-tomography (180°). Default is False.
    padding_mode : str
        Sinogram padding mode. Default is 'edges'.
    extra_options : dict
        Additional backprojector options. Default is {'centered_axis': True}.
    slice_index : int or str
        Slice index to reconstruct. Can be an integer index or
        'middle', 'first', 'last'. Default is 'middle'.

    Outputs
    -------
    reconstructed_slices_directory : str
        Path to the saved reconstructed slice files
    """

    def run(self):
        """Execute the online reconstruction pipeline."""
        # Get required inputs
        scan_key = self.get_input_value("scan_key")
        output_path = self.get_input_value("output_path")
        rotation_motor = self.get_input_value("rotation_motor")
        batch_size = int(self.get_input_value("batch_size", 100))
        total_nb_projection = int(self.get_input_value("total_nb_projection"))
        center_of_rotation = float(self.get_input_value("center_of_rotation"))
        reduced_dark_path = self.get_input_value("reduced_dark_path")
        reduced_flat_path = self.get_input_value("reduced_flat_path")
        pixel_size_m = float(self.get_input_value("pixel_size_m"))
        distance_m = float(self.get_input_value("distance_m"))
        energy_keV = float(self.get_input_value("energy_keV"))

        # Get optional parameters
        delta_beta = float(self.get_input_value("delta_beta", 100))
        halftomo = bool(self.get_input_value("halftomo", False))
        padding_mode = self.get_input_value("padding_mode", "edges")
        extra_options = self.get_input_value("extra_options", {"centered_axis": True})
        slice_index = self.get_input_value("slice_index", "middle")

        # Connect to beacon and load scan
        logger.info(f"Connecting to scan: {scan_key}")
        beacon_client = BeaconData()
        redis_url = beacon_client.get_redis_data_db()
        data_store = DataStore(redis_url)
        scan = data_store.load_scan(scan_key)

        # Wait for scan to start
        wait_for_scan_state(scan, ScanState.STARTED)

        # Prepare output directory
        self.outputs.reconstructed_slices_directory = output_path
        Path(output_path).mkdir(parents=True, exist_ok=True)

        # Load reduced darks and flats
        logger.info("Loading flat field correction data")
        self.flatfield_processor = FlatFieldCorrection()
        self.flatfield_processor.load_reduced_data_from_file(
            reduced_dark_path, reduced_flat_path
        )

        # Process batches
        proj_idx = 0
        while proj_idx < total_nb_projection:
            end_idx = min(proj_idx + batch_size, total_nb_projection)
            projections_indices = list(range(proj_idx, end_idx))
            logger.info(
                f"Processing batch {proj_idx//batch_size + 1}/"
                f"{(total_nb_projection + batch_size - 1)//batch_size}"
            )
            try:
                output_slice_path = (
                    Path(output_path) / f"reconstructed_slice_{proj_idx}_{end_idx-1}.h5"
                )
                self.reconstruct_batch(
                    scan=scan,
                    output_path=output_slice_path,
                    center_of_rotation=center_of_rotation,
                    projections_indices=projections_indices,
                    distance_m=distance_m,
                    energy_keV=energy_keV,
                    pixel_size_m=pixel_size_m,
                    rotation_motor=rotation_motor,
                    slice_index=slice_index,
                    delta_beta=delta_beta,
                    halftomo=halftomo,
                    padding_mode=padding_mode,
                    extra_options=extra_options,
                )
                proj_idx = end_idx
            except RuntimeError as e:
                logger.error(f"Stopping reconstruction due to error: {e}")
                break
        logger.info("Online reconstruction completed")

    def reconstruct_batch(
        self,
        scan,
        output_path: str,
        center_of_rotation: float,
        projections_indices: list[int],
        distance_m: float,
        energy_keV: float,
        pixel_size_m: float,
        rotation_motor: str,
        slice_index: int | str = "middle",
        delta_beta: float = 100.0,
        halftomo: bool = False,
        padding_mode: str = "edges",
        extra_options: dict[str, Any] | None = None,
    ) -> None:
        """
        Reconstruct a batch of projections and accumulate the result.

        Parameters
        ----------
        scan : Scan
            Blissdata scan object
        output_path : str
            Path to save the reconstructed slice
        center_of_rotation : float
            Center of rotation
        projections_indices : list of int
            Indices of projections to process in this batch
        distance_m : float
            Effective propagation distance (m)
        energy_keV : float
            Energy (keV)
        pixel_size_m : float
            Detector pixel size (m)
        rotation_motor : str
            Name of the rotation motor
        slice_index : int or str, optional
            Slice index to reconstruct. Default is 'middle'.
        delta_beta : float, optional
            Phase retrieval parameter. Default is 100.
        halftomo : bool, optional
            Half-tomography flag. Default is False.
        padding_mode : str, optional
            Sinogram padding mode. Default is 'edges'.
        extra_options : dict, optional
            Additional backprojector options
        """
        # Step 1: Load projections and angles from streams

        logger.info(
            f"Reconstructing batch {projections_indices[0]}-{projections_indices[-1]}"
        )
        try:
            projections = self._get_projections_from_stream(
                scan, projections_indices, output_dtype=np.float32
            )
            angles = self._get_angles_from_stream(
                scan, rotation_motor, projections_indices, output_dtype=np.float32
            )
        except RuntimeError as e:
            logger.error(f"Error getting data from streams: {e}")
            raise

        # Step 2: Flat field correction using normal class
        logger.info(f"Applying flat field correction to {len(projections)} projections")
        self.flatfield_processor.apply_correction(projections, projections_indices)

        # Step 3: Phase retrieval
        logger.info(f"Applying Paganin phase retrieval with delta/beta={delta_beta}")

        try:
            projections = apply_phase_retrieval(
                projections,
                distance_m=distance_m,
                energy_keV=energy_keV,
                pixel_size_m=pixel_size_m,
                delta_beta=delta_beta,
            )
            logger.info("Paganin phase retrieval completed")

        except Exception as e:
            logger.error(f"Error in Paganin phase retrieval: {e}")
            raise

        # Step 4: FBP Reconstruction
        logger.info(f"Starting FBP reconstruction with CoR={center_of_rotation:.3f}")

        options: dict[str, Any] = {"centered_axis": True}
        if extra_options:
            options.update(extra_options)

        try:
            reconstructed_slice = fbp_reconstruction_slice(
                projections,
                angles,
                center_of_rotation,
                slice_index=slice_index,
                halftomo=halftomo,
                padding_mode=padding_mode,
                extra_options=options,
            )
        except Exception as e:
            logger.error(f"Error creating backprojector: {e}")
            raise

        logger.info(
            f"Batch reconstruction completed. Output shape: {reconstructed_slice.shape}"
        )

        # Step 5: Save reconstructed slice to output path
        self.save_reconstructed_slice(output_path, reconstructed_slice)

    def save_reconstructed_slice(
        self, output_path: str, reconstructed_slice: np.ndarray
    ):
        """Save the reconstructed slice to an HDF5 file.

        Parameters
        ----------
        output_path : str
            Path to save the reconstructed slice
        reconstructed_slice : np.ndarray
            The reconstructed slice data
        """
        try:
            with h5py.File(output_path, "w") as h5f:
                h5f.create_dataset("reconstructed_slice", data=reconstructed_slice)
            logger.info(f"Reconstructed slice saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving reconstructed slice: {e}")
            raise

    def _get_image_stream_name(self, scan) -> str:
        """Get the image stream name from the scan."""
        for name in scan.streams:
            if ":image" in name:
                return name
        raise ValueError("No image stream found in scan")

    def _get_motor_stream_name(self, scan, motor_name: str) -> str:
        """Get the motor stream name from the scan."""
        for name in scan.streams:
            if motor_name in name and "axis:" in name:
                return name
        raise ValueError(f"No motor stream found for {motor_name} in scan")

    def _get_projections_from_stream(
        self, scan, projections_indices, output_dtype=np.float32
    ) -> np.ndarray:
        """Get projections from the image stream."""
        stream_name = self._get_image_stream_name(scan)
        detector_stream = scan.streams[stream_name]
        idx_start, idx_end = projections_indices[0], projections_indices[-1] + 1

        # Wait for frames to become available
        waited_time = 0

        while len(detector_stream) < idx_end:
            logger.debug(
                f"Waiting for frames in stream {stream_name} "
                f"({len(detector_stream)}/{idx_end})..."
            )
            time.sleep(WAITING_INTERVAL)
            scan.update(block=False)
            # Only start timeout counter after scan has stopped
            if scan.state >= ScanState.STOPPED:
                waited_time += 1
                if waited_time > STREAM_TIMEOUT:
                    raise TimeoutError(
                        f"Not enough frames received before scan stopped. "
                        f"Got {len(detector_stream)}, needed {idx_end}"
                    )

        return np.array(detector_stream[idx_start:idx_end], dtype=output_dtype)

    def _get_angles_from_stream(
        self, scan, rotation_motor: str, projections_indices, output_dtype=np.float32
    ) -> np.ndarray:
        """Get angles from the motor stream."""
        motor_stream_name = self._get_motor_stream_name(scan, rotation_motor)
        motor_stream = scan.streams[motor_stream_name]
        idx_start, idx_end = projections_indices[0], projections_indices[-1] + 1
        while len(motor_stream) < idx_end:
            logger.info(
                f"Waiting for more motor positions in stream {motor_stream_name}..."
            )
            time.sleep(WAITING_INTERVAL)
        angles_deg = np.array(motor_stream[idx_start:idx_end], dtype=output_dtype)
        angles_rad = np.deg2rad(angles_deg)
        return angles_rad
