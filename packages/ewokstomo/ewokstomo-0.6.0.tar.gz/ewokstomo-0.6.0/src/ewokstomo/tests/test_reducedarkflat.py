import shutil
from pathlib import Path

import pytest
from importlib.resources import files

from ewokstomo.tasks.reducedarkflat import ReduceDarkFlat
from ewoks import execute_graph


DATA_ROOT = Path(__file__).resolve().parent / "data"
COLLECTION = "TestEwoksTomo"


def get_json_file(file_name: str) -> Path:
    return Path(str(files("ewokstomo.workflows").joinpath(file_name)))


def get_data_dir(sample_dataset: str) -> Path:
    return DATA_ROOT / "PROCESSED_DATA" / COLLECTION / sample_dataset


def get_raw_data_dir(sample_dataset: str) -> Path:
    return DATA_ROOT / "RAW_DATA" / COLLECTION / sample_dataset


@pytest.fixture
def tmp_dataset_path(tmp_path) -> Path:
    sample_dataset = "TestEwoksTomo_0010"
    src_dir = get_data_dir(sample_dataset)
    dst_dir = tmp_path / sample_dataset
    shutil.copytree(src_dir, dst_dir)
    proj_dir = dst_dir / "projections"
    for pattern in ("*_darks.hdf5", "*_flats.hdf5"):
        for f in proj_dir.glob(pattern):
            f.unlink()
    references_dir = dst_dir / "references"
    if references_dir.exists():
        shutil.rmtree(references_dir)
    return dst_dir


@pytest.mark.parametrize("Task", [ReduceDarkFlat])
def test_reducedarkflat_task_outputs(Task, tmp_dataset_path):
    nx_file = tmp_dataset_path / "projections" / "TestEwoksTomo_0010.nx"
    references_dir = tmp_dataset_path / "references"
    dataset_name = nx_file.stem
    expected_darks = references_dir / f"{dataset_name}_darks.hdf5"
    expected_flats = references_dir / f"{dataset_name}_flats.hdf5"
    assert not expected_darks.exists()
    assert not expected_flats.exists()
    task = Task(
        inputs={
            "nx_path": str(nx_file),
            "dark_reduction_method": "mean",
            "flat_reduction_method": "median",
            "overwrite": False,
            "return_info": False,
        },
    )
    task.execute()
    assert Path(task.outputs.reduced_darks_path) == expected_darks
    assert Path(task.outputs.reduced_flats_path) == expected_flats
    assert expected_darks.is_file()
    assert expected_flats.is_file()
    overwrite_time = expected_darks.stat().st_mtime
    # Check overwrite functionality
    task = Task(
        inputs={
            "nx_path": str(nx_file),
            "dark_reduction_method": "mean",
            "flat_reduction_method": "median",
            "overwrite": True,
            "return_info": False,
        },
    )
    task.execute()
    assert expected_darks.stat().st_mtime > overwrite_time


@pytest.mark.parametrize("workflow", ["reducedarkflat.json"])
def test_reducedarkflat_workflow_outputs(workflow, tmp_dataset_path):
    wf = get_json_file(workflow)
    nx_file = tmp_dataset_path / "projections" / "TestEwoksTomo_0010.nx"
    result = execute_graph(
        wf,
        inputs=[{"name": "nx_path", "value": str(nx_file)}],
    )
    references_dir = tmp_dataset_path / "references"
    dataset_name = nx_file.stem
    expected_darks = references_dir / f"{dataset_name}_darks.hdf5"
    expected_flats = references_dir / f"{dataset_name}_flats.hdf5"
    assert Path(result["reduced_darks_path"]) == expected_darks
    assert Path(result["reduced_flats_path"]) == expected_flats
    assert expected_darks.exists()
    assert expected_flats.exists()

    # test with existing files in the provided directory
    provided_dir = tmp_dataset_path / "precomputed_references"
    provided_dir.mkdir()
    existing_darks = provided_dir / expected_darks.name
    existing_flats = provided_dir / expected_flats.name
    shutil.copy(expected_darks, existing_darks)
    shutil.copy(expected_flats, existing_flats)
    task = ReduceDarkFlat(
        inputs={
            "nx_path": str(nx_file),
            "reference_dir_to_soft_link": str(provided_dir),
        },
    )
    task.execute()
    assert Path(task.outputs.reduced_darks_path) == expected_darks
    assert Path(task.outputs.reduced_flats_path) == expected_flats
    assert expected_darks.is_symlink()
    assert expected_flats.is_symlink()
    assert expected_darks.resolve() == existing_darks.resolve()
    assert expected_flats.resolve() == existing_flats.resolve()

    # test with non-existing files in the provided directory
    non_existing_dir = tmp_dataset_path / "non_existing_references"
    non_existing_dir.mkdir()
    task = ReduceDarkFlat(
        inputs={
            "nx_path": str(nx_file),
            "reference_dir_to_soft_link": str(non_existing_dir),
        },
    )
    with pytest.raises(RuntimeError):
        task.execute()
