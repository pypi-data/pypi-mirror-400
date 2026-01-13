import numpy as np
import h5py
from unittest.mock import MagicMock, patch

from ewokstomo.tasks.online.preprocessing import (
    FlatFieldCorrection,
    apply_phase_retrieval,
)


def test_apply_flat_field_correction_calls_normalize():
    projections = np.ones((3, 4, 5), dtype=np.float32)
    indices = np.array([0, 1, 2])

    ffc = FlatFieldCorrection()
    ffc.reduced_darks = {0: np.zeros((4, 5))}
    ffc.reduced_flats = {1: np.ones((4, 5))}

    with patch("ewokstomo.tasks.online.preprocessing.FlatField") as MockFlatField:
        mock_instance = MagicMock()
        MockFlatField.return_value = mock_instance

        result = ffc.apply_correction(projections, indices)

        # Ensure FlatField was constructed correctly
        MockFlatField.assert_called_once()
        mock_instance.normalize_radios.assert_called_once_with(projections)

        # The operation is in-place
        assert result is projections


def test_load_reduced_data_from_hdf5(tmp_path):
    file_path = tmp_path / "reduced_dark.h5"

    with h5py.File(file_path, "w") as h5f:
        grp = h5f.create_group("entry0000")
        data = np.ones((4, 5), dtype=np.float32)
        grp.create_dataset("darks", data=data)

    ffc = FlatFieldCorrection()
    reduced = ffc._load_reduced_data(
        file_path=str(file_path),
        data_type="dark",
        idx=0,
    )

    assert isinstance(reduced, dict)
    assert 0 in reduced
    assert np.array_equal(reduced[0], data)


def test_apply_phase_retrieval_basic_flow():
    projections = np.ones((3, 4, 5), dtype=np.float32)

    with patch(
        "ewokstomo.tasks.online.preprocessing.PaganinPhaseRetrieval"
    ) as MockPaganin:
        mock_instance = MagicMock()
        MockPaganin.return_value = mock_instance

        result = apply_phase_retrieval(
            projections=projections,
            distance_m=0.1,
            energy_keV=20.0,
            pixel_size_m=1e-6,
            delta_beta=100.0,
        )

        # Called once per projection
        assert mock_instance.retrieve_phase.call_count == projections.shape[0]

        # Shape preserved
        assert result.shape == projections.shape
