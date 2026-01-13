"""
Preprocessing utilities for tomography reconstruction.

This module provides classes and functions for flat field correction
and phase retrieval operations commonly used in tomography.
"""

import h5py
import logging
import numpy as np
import warnings
from nabu.preproc.phase import PaganinPhaseRetrieval
from nabu.preproc.flatfield import FlatField

logger = logging.getLogger(__name__)


class FlatFieldCorrection:
    """
    Applies flat field correction to tomographic projections.

    Flat field correction normalizes projections by removing detector-specific
    artifacts using dark (background) and flat (reference) images. This correction
    is essential for obtaining accurate reconstructions.

    Attributes
    ----------
    reduced_darks : dict[int, np.ndarray]
        Dictionary mapping indices to reduced dark frames
    reduced_flats : dict[int, np.ndarray]
        Dictionary mapping indices to reduced flat frames
    """

    def __init__(self):
        """Initialize the flat field corrector."""
        self.reduced_darks: dict[int, np.ndarray] | None = None
        self.reduced_flats: dict[int, np.ndarray] | None = None

    def apply_correction(
        self, projections: np.ndarray, projections_indices: np.ndarray
    ) -> np.ndarray:
        """
        Apply flat field correction to projections.

        Parameters
        ----------
        projections : np.ndarray
            Array of projections with shape (n_angles, n_z, n_x)
        projections_indices : np.ndarray
            Indices of the projections in the full scan sequence

        Returns
        -------
        np.ndarray
            Corrected projections with the same shape as input
        """

        flatfield = FlatField(
            projections.shape,
            self.reduced_flats,
            self.reduced_darks,
            radios_indices=projections_indices,
        )
        warnings.filterwarnings(
            "ignore",
            message=".*encountered in divide",
            category=RuntimeWarning,
            module="nabu.preproc.flatfield",
        )
        flatfield.normalize_radios(projections)

        return projections

    def load_reduced_data_from_file(
        self,
        reduced_dark_path: str,
        reduced_flat_path: str,
        dark_first: bool = True,
    ) -> None:
        """Load reduced darks and flats from HDF5 files.

        Parameters
        ----------
        reduced_dark_path : str
            Path to the HDF5 file containing reduced dark frames
        reduced_flat_path : str
            Path to the HDF5 file containing reduced flat frames
        dark_first : bool, optional
            If True, assign index 0 to darks and len(darks) to flats.
            If False, assign index 0 to flats and len(flats) to darks.
            Default is True.
        """
        if dark_first:
            self.reduced_darks = self._load_reduced_data(reduced_dark_path, "dark", 0)
            self.reduced_flats = self._load_reduced_data(
                reduced_flat_path, "flat", len(self.reduced_darks)
            )
        else:
            self.reduced_flats = self._load_reduced_data(reduced_flat_path, "flat", 0)
            self.reduced_darks = self._load_reduced_data(
                reduced_dark_path, "dark", len(self.reduced_flats)
            )

    def _load_reduced_data(
        self, file_path: str, data_type: str, idx: int
    ) -> dict[int, np.ndarray]:
        """Load reduced data from HDF5 file.

        Parameters
        ----------
        file_path : str
            Path to the HDF5 file
        data_type : str
            Type of data to load ("dark" or "flat")
        idx : int
            Starting index for the loaded data

        Returns
        -------
        dict[int, np.ndarray]
            Dictionary mapping indices to reduced frames
        """
        reduced_data = {}

        with h5py.File(file_path, "r") as h5f:
            data_path = f"entry0000/{data_type}s"
            reduced_data[idx] = h5f[data_path][()]

        if not reduced_data:
            raise ValueError(f"No reduced {data_type} data found in {file_path}")

        logger.info(f"Loaded {len(reduced_data)} reduced {data_type}")
        return reduced_data


def apply_phase_retrieval(
    projections: np.ndarray,
    distance_m: float,
    energy_keV: float,
    pixel_size_m: float,
    delta_beta: float,
) -> np.ndarray:
    """
    Apply Paganin phase retrieval to projections.

    Parameters
    ----------
    projections : np.ndarray
        Array of projections with shape (n_angles, n_z, n_x).
    distance_m : float
        Effective propagation distance in meters.
    energy_keV : float
        Energy in keV.
    pixel_size_m : float
        Detector pixel size in meters.
    delta_beta : float, optional
        delta/beta ratio, where n = (1 - delta) + i*beta is the complex
        refractive index of the sample.

    Returns
    -------
    np.ndarray
        Phase-retrieved projections with the same shape as input.
    """
    if not isinstance(projections, np.ndarray):
        projections = np.array(projections, dtype=np.float32)

    processed_projections = projections

    paganin = PaganinPhaseRetrieval(
        projections.shape[1:],
        distance=distance_m,
        energy=energy_keV,
        delta_beta=delta_beta,
        pixel_size=pixel_size_m,
    )

    for proj in processed_projections:
        paganin.retrieve_phase(proj, output=proj)

    np.clip(processed_projections, 1e-6, 10, out=processed_projections)
    np.log(processed_projections, out=processed_projections)
    processed_projections[:] *= -1

    return processed_projections
