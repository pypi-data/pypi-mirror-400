import shutil
from pathlib import Path

import pytest
from ewokstomo.tasks.reconstruct_slice import ReconstructSlice
from ewoks import execute_graph
from importlib.resources import files


DATA_ROOT = Path(__file__).resolve().parent / "data"
RAW_COLLECTION = "TestEwoksTomo"
ROTATION_AXIS_POSITION = 8.0


def get_json_file(file_name: str) -> Path:
    return Path(str(files("ewokstomo.workflows").joinpath(file_name)))


def get_data_file(file_name):
    return str(DATA_ROOT / "RAW_DATA" / RAW_COLLECTION / file_name / f"{file_name}.h5")


def get_data_dir(scan_name: str) -> Path:
    return DATA_ROOT / "PROCESSED_DATA" / RAW_COLLECTION / scan_name


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


@pytest.mark.order(5)
@pytest.mark.parametrize("Task", [ReconstructSlice])
def test_reconstructslice_task_outputs(Task, tmp_dataset_path):
    nx = tmp_dataset_path / "projections" / "TestEwoksTomo_0010.nx"

    nx_path = "dontexist.nx"
    nabu_conf = {
        "dataset": {"location": None},
        "reconstruction": {
            "start_z": "middle",
            "end_z": "middle",
            "rotation_axis_position": ROTATION_AXIS_POSITION,
        },
        "output": {"location": ""},
    }
    with pytest.raises(FileNotFoundError):
        Task(
            inputs={
                "config_dict": nabu_conf,
                "slice_index": "middle",
                "nx_path": nx_path,
            }
        ).run()

    nx_path = str(nx)
    task = Task(
        inputs={"config_dict": nabu_conf, "slice_index": "middle", "nx_path": nx_path}
    )
    task.execute()

    rec_path = Path(task.outputs.reconstructed_slice_path)
    assert rec_path.exists(), "Reconstructed slices directory does not exist"
    assert rec_path.is_file(), "Reconstructed slices path is not a file"
    assert rec_path.parent == tmp_dataset_path / "slices"
    expected_prefix = f"{Path(nx_path).stem}_absorption_xy_"
    assert rec_path.name.startswith(expected_prefix)
    assert rec_path.name.endswith(".hdf5")
    slice_suffix = rec_path.stem.split("_")[-1]
    assert slice_suffix.isdigit() and len(slice_suffix) == 5
    nabu_dict = task.outputs.nabu_dict
    assert isinstance(nabu_dict, dict)
    assert nabu_dict["dataset"]["location"] == str(nx_path)
    assert (
        nabu_dict["reconstruction"]["rotation_axis_position"] == ROTATION_AXIS_POSITION
    )
    assert nabu_dict["reconstruction"]["start_z"] == "middle"
    assert nabu_dict["reconstruction"]["end_z"] == "middle"
    assert nabu_dict["output"]["location"] == str(tmp_dataset_path / "slices")
    assert nabu_dict["output"]["file_prefix"] == rec_path.stem


@pytest.mark.parametrize("workflow", ["reconstruction.json"])
def test_reconstructslice_workflow_outputs(workflow, tmp_dataset_path):
    h5_file_path = get_data_file("TestEwoksTomo_0010")
    nx_path = tmp_dataset_path / "projections" / "TestEwoksTomo_0010.nx"
    nx = str(nx_path)
    workflow_file_path = get_json_file(workflow)
    nabu_conf = {
        "dataset": {"location": None},
        "reconstruction": {
            "start_z": "middle",
            "end_z": "middle",
            "rotation_axis_position": ROTATION_AXIS_POSITION,
        },
        "output": {"location": ""},
    }

    reconstructed = execute_graph(
        workflow_file_path,
        inputs=[
            {
                "task_identifier": "ewokstomo.tasks.nxtomomill.H5ToNx",
                "name": "bliss_hdf5_path",
                "value": h5_file_path,
            },
            {
                "task_identifier": "ewokstomo.tasks.reconstruct_slice.ReconstructSlice",
                "name": "config_dict",
                "value": nabu_conf,
            },
            {
                "task_identifier": "ewokstomo.tasks.reconstruct_slice.ReconstructSlice",
                "name": "slice_index",
                "value": "middle",
            },
            {
                "task_identifier": "ewokstomo.tasks.nxtomomill.H5ToNx",
                "name": "nx_path",
                "value": nx,
            },
            {
                "task_identifier": "ewokstomo.tasks.reconstruct_slice.ReconstructSlice",
                "name": "nx_path",
                "value": nx,
            },
        ],
        outputs=[{"all": True}],
    )

    rec_path = Path(reconstructed["reconstructed_slice_path"])
    assert rec_path.exists(), "Reconstructed slices directory does not exist"
    assert rec_path.is_file(), "Reconstructed slices path is not a file"
    assert rec_path.parent == tmp_dataset_path / "slices"
    expected_prefix = f"{nx_path.stem}_absorption_xy_"
    assert rec_path.name.startswith(expected_prefix)
    assert rec_path.name.endswith(".hdf5")
    slice_suffix = rec_path.stem.split("_")[-1]
    assert slice_suffix.isdigit() and len(slice_suffix) == 5
    nabu_dict = reconstructed["nabu_dict"]
    assert isinstance(nabu_dict, dict)
    assert nabu_dict["dataset"]["location"] == str(nx_path)
    assert (
        nabu_dict["reconstruction"]["rotation_axis_position"] == ROTATION_AXIS_POSITION
    )
    assert nabu_dict["reconstruction"]["start_z"] == "middle"
    assert nabu_dict["reconstruction"]["end_z"] == "middle"
    assert nabu_dict["output"]["location"] == str(tmp_dataset_path / "slices")
    assert nabu_dict["output"]["file_prefix"] == rec_path.stem
    slices_gallery = rec_path.parent / "gallery"
    assert slices_gallery.exists(), "Slices gallery directory does not exist"
    assert slices_gallery.is_dir(), "Slices gallery path is not a directory"
    slice_images = sorted(
        p for p in slices_gallery.glob("*.jpg") if not p.name.endswith("_large.jpg")
    )
    large_slice_images = sorted(slices_gallery.glob("*_large.jpg"))
    assert len(slice_images) == 1, f"Expected 1 slice image, found {len(slice_images)}"
    assert (
        len(large_slice_images) == 1
    ), f"Expected 1 large slice image, found {len(large_slice_images)}"

    projection_gallery = nx_path.parent / "gallery"
    assert projection_gallery.exists(), "Projections gallery directory does not exist"
    assert projection_gallery.is_dir(), "Projections gallery path is not a directory"
    projection_images = sorted(
        p for p in projection_gallery.glob("*.jpg") if not p.name.endswith("_large.jpg")
    )
    large_projection_images = sorted(projection_gallery.glob("*_large.jpg"))
    assert (
        len(projection_images) == 5
    ), f"Expected 5 projection images, found {len(projection_images)}"
    assert (
        len(large_projection_images) == 5
    ), f"Expected 5 large projection images, found {len(large_projection_images)}"
    gif_path = projection_gallery / f"{nx_path.stem}.gif"
    assert gif_path.exists(), "Projections GIF does not exist"

    references_dir = tmp_dataset_path / "references"
    assert references_dir.exists(), "References directory does not exist"
    assert references_dir.is_dir(), "References path is not a directory"
    dataset_name = nx_path.stem
    dark_field = references_dir / f"{dataset_name}_darks.hdf5"
    flat_field = references_dir / f"{dataset_name}_flats.hdf5"
    assert dark_field.is_file(), "Reduced dark field file is missing"
    assert flat_field.is_file(), "Reduced flat field file is missing"
