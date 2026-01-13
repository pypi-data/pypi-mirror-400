import h5py
import numpy as np
import pytest
from pathlib import Path
from unittest.mock import patch
import shutil
from blissdata.redis_engine.scan import ScanState
from ewokstomo.tasks.online.reconstruct_slice import OnlineReconstructSlice
from ewokstomo.tasks.online.reducedarkflat import OnlineReduceDarkFlat
from ewokstomo.tests.test_reducedarkflat import get_data_dir, get_raw_data_dir
from ewokstomo.tests.online.mock import FakeScan, FakeScanWithMotor
from ewokstomo.tasks.online.reconstruct_slice import get_slice_index
import time


@pytest.fixture
def tmp_dataset_path(tmp_path) -> Path:
    src_dir = get_data_dir("TestEwoksTomo_0010")
    dst_dir = tmp_path / "TestEwoksTomo_0010"
    shutil.copytree(src_dir, dst_dir)
    proj_dir = dst_dir / "projections"

    proj_dir.mkdir(exist_ok=True)
    slices_dir = dst_dir / "slices"
    if slices_dir.exists():
        shutil.rmtree(slices_dir)
    # remove any existing darks/flats and gallery
    for pattern in ("*_darks.hdf5", "*_flats.hdf5", "gallery"):
        for f in proj_dir.glob(pattern):
            if f.is_dir():
                shutil.rmtree(f)
            else:
                f.unlink()
    references_dir = dst_dir / "references"
    if references_dir.exists():
        shutil.rmtree(references_dir)
    return dst_dir


def test_get_slice_index():
    assert get_slice_index(3, n_z=10) == 3
    assert get_slice_index("middle", n_z=11) == 5
    assert get_slice_index("first", n_z=10) == 0
    assert get_slice_index("last", n_z=10) == 9
    with pytest.raises(ValueError, match="Invalid slice index"):
        get_slice_index("banana", n_z=10)


def test_get_image_stream_name_no_image_stream():
    task = OnlineReconstructSlice.__new__(OnlineReconstructSlice)

    fake_scan = type(
        "Scan",
        (),
        {"streams": {"foo": None}},
    )()

    with pytest.raises(ValueError, match="No image stream found"):
        task._get_image_stream_name(fake_scan)


def test_get_motor_stream_name_no_motor():
    task = OnlineReconstructSlice.__new__(OnlineReconstructSlice)

    fake_scan = type(
        "Scan",
        (),
        {"streams": {"det:image": None}},
    )()

    with pytest.raises(ValueError, match="No motor stream found"):
        task._get_motor_stream_name(fake_scan, motor_name="rot")


def test_get_projections_stream_timeout(monkeypatch):
    task = OnlineReconstructSlice.__new__(OnlineReconstructSlice)

    class FakeScan:
        state = ScanState.STOPPED
        streams = {"det:image": []}

        def update(self, block=False):
            pass

    scan = FakeScan()

    # Avoid real sleeping
    monkeypatch.setattr(time, "sleep", lambda *_: None)

    with pytest.raises(TimeoutError, match="Not enough frames received"):
        task._get_projections_from_stream(
            scan=scan,
            projections_indices=[0, 1, 2],
        )


@pytest.fixture
def TestEwoksTomo_0010_dataset(tmp_path) -> Path:
    """Copy the test dataset to a temporary directory."""
    scan = "TestEwoksTomo_0010"
    processed_dir = get_data_dir(scan)
    raw_dir = get_raw_data_dir(scan)
    dst_dir = tmp_path / scan
    shutil.copytree(processed_dir, dst_dir)
    shutil.copy(raw_dir / f"{scan}.h5", dst_dir / f"{scan}.h5")
    return dst_dir


@pytest.fixture
def test_data(TestEwoksTomo_0010_dataset):
    """
    Load raw frames from TestEwoksTomo_0010 dataset.
    Returns raw darks, flats, and projections separately.
    """
    h5py_file = TestEwoksTomo_0010_dataset / "TestEwoksTomo_0010.h5"

    with h5py.File(h5py_file, "r") as f:
        # Load raw frames for each scan
        dark_frames = [
            np.array(frame, dtype=np.float32)
            for frame in f["2.1/measurement/edgetwinmic"]
        ]
        flat_frames = [
            np.array(frame, dtype=np.float32)
            for frame in f["3.1/measurement/edgetwinmic"]
        ]
        projection_frames = [
            np.array(frame, dtype=np.float32)
            for frame in f["4.1/measurement/edgetwinmic"]
        ]

    # Create angles for projections (full 360-degree tomography)
    n_projections = len(projection_frames)
    angles = np.linspace(0, 2 * np.pi, n_projections, endpoint=False, dtype=np.float32)

    # Get dimensions
    n_z, n_x = projection_frames[0].shape

    return {
        "dark_frames": dark_frames,
        "flat_frames": flat_frames,
        "projection_frames": projection_frames,
        "angles": angles,
        "pixel_size_m": 0.0000075,
        "delta_beta": 100.0,
        "distance_m": 500.0,
        "energy_keV": 17.0,
        "n_projections": n_projections,
        "n_z": n_z,
        "n_x": n_x,
        "dataset_dir": TestEwoksTomo_0010_dataset,
    }


def test_full_workflow_online_reconstruction(test_data, tmp_path):
    """
    Test the complete online tomography workflow with multiple batches and phase retrieval:
    1. Mock dark scan and reduce darks
    2. Mock flat scan and reduce flats
    3. Mock projection scan and reconstruct in batches with phase retrieval
    """
    data = test_data
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Step 1: Mock dark scan and reduce darks
    fake_dark_scan = FakeScan(data["dark_frames"], title="dark")

    with (
        patch("ewokstomo.tasks.online.reducedarkflat.BeaconData") as MockBeacon,
        patch("ewokstomo.tasks.online.reducedarkflat.DataStore") as MockStore,
    ):
        MockBeacon.return_value.get_redis_data_db.return_value = "redis://fake"
        MockStore.return_value.load_scan.return_value = fake_dark_scan

        dark_output = output_dir / "reduced_darks.h5"
        dark_task = OnlineReduceDarkFlat(
            inputs={
                "scan_key": "dark_scan",
                "index": 0,
                "reduction_method": "mean",
                "output_file_path": str(dark_output),
            }
        )
        dark_task.execute()

    assert dark_output.is_file(), "Reduced darks file was not created"

    # Verify reduced darks content
    with h5py.File(dark_output, "r") as f:
        # Option 1: Check the nested path properly
        assert "entry0000" in f, "entry0000 group not found"
        assert "darks" in f["entry0000"], "Reduced darks dataset not found"
        reduced_dark = f["entry0000/darks"][()]
        assert reduced_dark.shape == data["dark_frames"][0].shape

    # Step 2: Mock flat scan and reduce flats
    fake_flat_scan = FakeScan(data["flat_frames"], title="flat")

    with (
        patch("ewokstomo.tasks.online.reducedarkflat.BeaconData") as MockBeacon,
        patch("ewokstomo.tasks.online.reducedarkflat.DataStore") as MockStore,
    ):
        MockBeacon.return_value.get_redis_data_db.return_value = "redis://fake"
        MockStore.return_value.load_scan.return_value = fake_flat_scan

        flat_output = output_dir / "reduced_flats.h5"
        flat_task = OnlineReduceDarkFlat(
            inputs={
                "scan_key": "flat_scan",
                "index": len(data["dark_frames"]),  # Offset index for Nabu
                "reduction_method": "median",
                "output_file_path": str(flat_output),
            }
        )
        flat_task.execute()

    assert flat_output.is_file(), "Reduced flats file was not created"

    # Verify reduced flats content
    with h5py.File(flat_output, "r") as f:
        assert "entry0000/flats" in f, "Reduced flats dataset not found"
        reduced_flat = f["entry0000/flats"][()]
        assert reduced_flat.shape == data["flat_frames"][0].shape

    # Step 3: Mock projection scan and reconstruct with multiple batches
    fake_projection_scan = FakeScanWithMotor(
        arrays=data["projection_frames"],
        angles=list(data["angles"]),
        title="projections",
        rotation_motor="rot",
    )

    # Use a batch size that will create multiple batches
    batch_size = max(10, data["n_projections"] // 4)
    expected_batches = (data["n_projections"] + batch_size - 1) // batch_size

    with (
        patch("ewokstomo.tasks.online.reconstruct_slice.BeaconData") as MockBeacon,
        patch("ewokstomo.tasks.online.reconstruct_slice.DataStore") as MockStore,
    ):
        MockBeacon.return_value.get_redis_data_db.return_value = "redis://fake"
        MockStore.return_value.load_scan.return_value = fake_projection_scan

        recon_output = output_dir / "reconstruction"
        task = OnlineReconstructSlice(
            inputs={
                "scan_key": "projection_scan",
                "output_path": str(recon_output),
                "rotation_motor": "rot",
                "total_nb_projection": data["n_projections"],
                "center_of_rotation": data["n_x"] / 2.0,
                "batch_size": batch_size,
                "pixel_size_m": data["pixel_size_m"],
                "distance_m": data["distance_m"],
                "energy_keV": data["energy_keV"],
                "reduced_dark_path": str(dark_output),
                "reduced_flat_path": str(flat_output),
                "delta_beta": data["delta_beta"],
                "halftomo": False,  # Full tomography
                "padding_mode": "edges",
            }
        )
        task.execute()

    # Verify reconstruction output directory exists
    assert (
        recon_output.is_dir()
    ), f"Reconstruction output directory not found: {recon_output}"

    # Verify multiple batch output files were created
    output_files = sorted(recon_output.glob("reconstructed_slice_*.h5"))
    assert (
        len(output_files) == expected_batches
    ), f"Expected {expected_batches} output files, found {len(output_files)}"

    # Verify each batch file contains valid reconstruction data
    for i, output_file in enumerate(output_files):
        with h5py.File(output_file, "r") as f:
            assert (
                "reconstructed_slice" in f
            ), f"Reconstructed slice dataset not found in {output_file.name}"

    print(f"\n✓ Successfully processed {len(output_files)} batches")


def test_run_stops_on_reconstruct_batch_runtime_error(monkeypatch, tmp_path):
    task = OnlineReconstructSlice(
        inputs={
            "scan_key": "scan",
            "output_path": str(tmp_path),
            "rotation_motor": "rot",
            "total_nb_projection": 10,
            "center_of_rotation": 4.0,
            "batch_size": 5,
            "pixel_size_m": 1.0,
            "distance_m": 1.0,
            "energy_keV": 1.0,
            "reduced_dark_path": "dark.h5",
            "reduced_flat_path": "flat.h5",
        }
    )

    fake_scan = type(
        "Scan",
        (),
        {"streams": {}, "state": ScanState.STARTED},
    )()

    # --- infrastructure mocks ---
    monkeypatch.setattr(
        "ewokstomo.tasks.online.reconstruct_slice.wait_for_scan_state",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "ewokstomo.tasks.online.reconstruct_slice.BeaconData",
        lambda: type("B", (), {"get_redis_data_db": lambda self: "redis://fake"})(),
    )
    monkeypatch.setattr(
        "ewokstomo.tasks.online.reconstruct_slice.DataStore",
        lambda *_: type("DS", (), {"load_scan": lambda self, key: fake_scan})(),
    )

    # --- critical mock: bypass flatfield file loading ---
    monkeypatch.setattr(
        "ewokstomo.tasks.online.reconstruct_slice.FlatFieldCorrection.load_reduced_data_from_file",
        lambda *args, **kwargs: None,
    )

    # --- force RuntimeError inside loop ---
    monkeypatch.setattr(
        task,
        "reconstruct_batch",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    # Must NOT raise
    task.execute()


def test_reconstruct_batch_phase_retrieval_failure(monkeypatch, tmp_path):
    task = OnlineReconstructSlice.__new__(OnlineReconstructSlice)

    task.flatfield_processor = type(
        "FF",
        (),
        {"apply_correction": lambda *args, **kwargs: None},
    )()

    monkeypatch.setattr(
        task,
        "_get_projections_from_stream",
        lambda *args, **kwargs: np.ones((3, 4, 8), dtype=np.float32),
    )
    monkeypatch.setattr(
        task,
        "_get_angles_from_stream",
        lambda *args, **kwargs: np.zeros(3, dtype=np.float32),
    )

    # Phase retrieval fails
    monkeypatch.setattr(
        "ewokstomo.tasks.online.reconstruct_slice.apply_phase_retrieval",
        lambda *args, **kwargs: (_ for _ in ()).throw(Exception("phase fail")),
    )

    with pytest.raises(Exception, match="phase fail"):
        task.reconstruct_batch(
            scan=None,
            output_path=tmp_path / "out.h5",
            center_of_rotation=4.0,
            projections_indices=[0, 1, 2],
            distance_m=1.0,
            energy_keV=1.0,
            pixel_size_m=1.0,
            rotation_motor="rot",
        )


def test_reconstruct_batch_fbp_failure(monkeypatch, tmp_path):
    task = OnlineReconstructSlice.__new__(OnlineReconstructSlice)

    task.flatfield_processor = type(
        "FF",
        (),
        {"apply_correction": lambda *args, **kwargs: None},
    )()

    monkeypatch.setattr(
        task,
        "_get_projections_from_stream",
        lambda *args, **kwargs: np.ones((3, 4, 8), dtype=np.float32),
    )
    monkeypatch.setattr(
        task,
        "_get_angles_from_stream",
        lambda *args, **kwargs: np.zeros(3, dtype=np.float32),
    )
    monkeypatch.setattr(
        "ewokstomo.tasks.online.reconstruct_slice.apply_phase_retrieval",
        lambda *args, **kwargs: args[0],
    )

    # FBP fails
    monkeypatch.setattr(
        "ewokstomo.tasks.online.reconstruct_slice.fbp_reconstruction_slice",
        lambda *args, **kwargs: (_ for _ in ()).throw(Exception("fbp fail")),
    )

    with pytest.raises(Exception, match="fbp fail"):
        task.reconstruct_batch(
            scan=None,
            output_path=tmp_path / "out.h5",
            center_of_rotation=4.0,
            projections_indices=[0, 1, 2],
            distance_m=1.0,
            energy_keV=1.0,
            pixel_size_m=1.0,
            rotation_motor="rot",
        )
