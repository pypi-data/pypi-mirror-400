import pytest
from ewokstomo.tasks.nxtomomill import H5ToNx, FluoToNx
from ewoks import execute_graph
from pathlib import Path
import importlib.resources as pkg_resources


DATA_ROOT = Path(__file__).resolve().parent / "data"
RAW_COLLECTION = "TestEwoksTomo"


def get_json_file(file_name):
    file_path = pkg_resources.files("ewokstomo.workflows").joinpath(file_name)
    return file_path


def get_data_file(file_name):
    return str(DATA_ROOT / "RAW_DATA" / RAW_COLLECTION / file_name / f"{file_name}.h5")


@pytest.mark.order(3)
@pytest.mark.parametrize("Task", [H5ToNx])
def test_nxtomomill_task_outputs(Task, tmp_path):
    output_dir = tmp_path / "projections"
    output_dir.mkdir()
    h5_file_path = get_data_file("TestEwoksTomo_0010")
    expected_output = output_dir / "TestEwoksTomo_0010.nx"

    task = Task(
        inputs={
            "bliss_hdf5_path": h5_file_path,
            "nx_path": str(expected_output),
        }
    )
    task.execute()

    assert str(Path(task.outputs.nx_path).resolve()) == str(expected_output)
    assert expected_output.is_file()


@pytest.mark.order(4)
@pytest.mark.parametrize("workflow", ["nxtomomill.json"])
def test_nxtomomill_workflow_outputs(workflow, tmp_path):
    output_dir = tmp_path / "projections"
    output_dir.mkdir()
    h5_file_path = get_data_file("TestEwoksTomo_0010")
    expected_output = output_dir / "TestEwoksTomo_0010.nx"
    workflow_file_path = get_json_file(workflow)

    output = execute_graph(
        workflow_file_path,
        inputs=[
            {
                "name": "bliss_hdf5_path",
                "value": h5_file_path,
            },
            {"name": "nx_path", "value": str(expected_output)},
        ],
    )

    assert str(Path(output["nx_path"]).resolve()) == str(expected_output)
    assert expected_output.is_file()
    # assert Path(expected_output).is_file()


@pytest.mark.order(5)
@pytest.mark.parametrize("workflow", ["nxtomomill_fluo2nx.json"])
def test_nxtomomill_workflow_fluo2nx(workflow, tmpdir):
    print(type(tmpdir), tmpdir)
    output_dir = tmpdir / "output"
    output_dir.mkdir()
    h5_file_path = get_data_file("SiemensLH_aligned_33keV_0002")
    expected_output = f"{output_dir}/S_wf.nx"
    workflow_file_path = get_json_file(workflow)

    output = execute_graph(
        workflow_file_path,
        inputs=[
            {
                "name": "bliss_hdf5_path",
                "value": h5_file_path,
            },
            {"name": "nx_path", "value": expected_output},
        ],
    )

    assert str(Path(output["nx_path"]).resolve()) == str(expected_output)
    # assert Path(expected_output).is_file()


@pytest.mark.order(6)
@pytest.mark.parametrize("Task", [FluoToNx])
def test_nxtomomill_fluo2nx(Task, tmpdir):
    output_dir = tmpdir / "output"
    output_dir.mkdir()
    h5_file_path = get_data_file("SiemensLH_aligned_33keV_0002")
    expected_output = str(output_dir / "S_task.nx")

    task = Task(
        inputs={
            "bliss_hdf5_path": h5_file_path,
            "nx_path": expected_output,
        }
    )
    task.execute()
    assert str(Path(task.outputs.nx_path).resolve()) == str(expected_output)
    # assert Path(expected_output).is_file()
