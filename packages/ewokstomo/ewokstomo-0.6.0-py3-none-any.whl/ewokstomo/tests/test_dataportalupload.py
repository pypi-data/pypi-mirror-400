import re
import pytest
from ewokstomo.tasks import dataportalupload

PROCESSED = "/data/visitor/ma0000/id00/20250101/PROCESSED_DATA/sample/sample_dataset"
RAW = "/data/visitor/ma0000/id00/20250101/RAW_DATA/sample/sample_dataset"


def make_task(inputs: dict):
    return dataportalupload.DataPortalUpload(inputs=inputs)


def _last_dryrun_message(caplog) -> str | None:
    msgs = [r.message for r in caplog.records if r.levelname == "INFO"]
    for m in reversed(msgs):
        if "Dry-run: would store_processed_data" in m:
            return m
    return None


def test_dry_run_happy_case_logs_basic_fields(caplog):
    t = make_task(
        {
            "process_folder_path": PROCESSED,
            "metadata": {"Sample_name": "override_sample", "extra": 42},
            "dry_run": True,
        }
    )
    with caplog.at_level("INFO"):
        t.execute()

    msg = _last_dryrun_message(caplog)
    assert msg, "Expected dry-run log line not found"
    assert "proposal=ma0000" in msg
    assert "beamline=id00" in msg
    assert "dataset=dataset" in msg
    assert f"path={PROCESSED}" in msg
    assert f"raw=['{RAW}']" in msg


def test_dry_run_infers_sample_name_is_mentioned(caplog):
    t = make_task(
        {
            "process_folder_path": PROCESSED,
            "metadata": None,
            "dry_run": True,
        }
    )
    with caplog.at_level("INFO"):
        t.execute()

    msg = _last_dryrun_message(caplog)
    assert msg, "Expected dry-run log line not found"
    assert "Sample_name" in msg
    assert "sample" in msg


def test_dry_run_adds_missing_sample_key_is_mentioned(caplog):
    t = make_task(
        {
            "process_folder_path": PROCESSED,
            "metadata": {"foo": "bar"},
            "dry_run": True,
        }
    )
    with caplog.at_level("INFO"):
        t.execute()

    msg = _last_dryrun_message(caplog)
    assert msg, "Expected dry-run log line not found"
    assert "foo" in msg and "bar" in msg
    assert "Sample_name" in msg and "sample" in msg


STRUCTURE_REGEX = re.compile(
    r"Expected\s+PROCESSED_DATA/<sample>/<(?:sample_)?dataset>(?:\s+path\s+structure\.)?",
    re.I,
)
FALLBACK_PATTERNS = [
    re.compile(r"Field has no value:\s*'(dataset|collection)'", re.I),
    re.compile(r"missing\s+value.*(dataset|collection)", re.I),
    re.compile(r"\b(dataset|collection)\b.*(missing|none|null|empty)", re.I),
    re.compile(r"(missing|required).*(dataset|collection)", re.I),
]


@pytest.mark.parametrize(
    "bad_path, preferred_pattern",
    [
        (
            "/data/visitor/ma0000/id00/20250101/RAW_DATA/sample/sample_dataset",
            re.compile(r"Not a\s+PROCESSED_DATA\s+path", re.I),
        ),
        (
            "/data/visitor/ma0000/id00/20250101/PROCESSED_DATA",
            STRUCTURE_REGEX,
        ),
        (
            "/data/visitor/ma0000/id00/20250101/PROCESSED_DATA/sample_only",
            STRUCTURE_REGEX,
        ),
    ],
)
def test_validation_errors_log_warning_and_no_dryrun(
    caplog, bad_path, preferred_pattern
):
    t = make_task(
        {
            "process_folder_path": bad_path,
            "metadata": None,
            "dry_run": True,
        }
    )
    with caplog.at_level("WARNING"):
        t.execute()

    warnings = [r.message or "" for r in caplog.records if r.levelname == "WARNING"]

    matched = any(preferred_pattern.search(m) for m in warnings) or any(
        p.search(m) for p in FALLBACK_PATTERNS for m in warnings
    )

    assert matched, (
        "No WARNING matched preferred or fallback patterns.\n"
        f"Preferred: {preferred_pattern.pattern}\n"
        "Warnings were:\n- " + "\n- ".join(warnings)
    )

    assert _last_dryrun_message(caplog) is None


@pytest.mark.parametrize(
    "subdir,dataset,expected",
    [
        ("slices", "slices", "slices"),
        ("projections", "projections", "projections"),
    ],
)
def test_build_payload_adds_workflow_type(subdir, dataset, expected):
    payload = dataportalupload._build_icat_payload(f"{PROCESSED}/{subdir}", {}, dataset)
    assert payload["metadata"]["workflow_type"] == expected
    assert "Sample_name" in payload["metadata"]


def test_build_payload_overrides_workflow_type_to_match_dataset():
    payload = dataportalupload._build_icat_payload(
        f"{PROCESSED}/projections", {"workflow_type": "slices"}, "projections"
    )
    assert payload["metadata"]["workflow_type"] == "projections"


def test_build_dataportal_metadata_transforms_and_filters():
    processing_options = {
        "reconstruction": {
            "method": "FBP",
            "rotation_axis_position": 1011.6686,
            "cor_options": "side=1011.6686114352402",
            "angle_offset": 0.0,
            "fbp_filter_type": "ramlak",
            "fbp_filter_cutoff": 1.0,
            "padding_type": "edge",
            "enable_halftomo": False,
            "clip_outer_circle": False,
            "centered_axis": True,
            "start_x": 0,
            "end_x": -1,
            "start_y": 0,
            "end_y": -1,
            "start_z": 0,
            "end_z": -1,
            # exclusions and empty-ish values
            "crop_filtered_data": "yes",
            "hbp_legs": 3,
            "hbp_reduction_steps": None,
            "iterations": "",
            "outer_circle_value": 0,
        },
        "phase": {
            "method": "Paganin",
            "delta_beta": "100",
            "unsharp_coeff": "0",
            "unsharp_sigma": "0",
            "unsharp_method": "gaussian",
            "padding_type": "edge",
            "ctf_geometry": "z1_v=None; z1_h=None; detec_pixel_size=None; magnification=True",
            "ctf_advanced_params": "length_scale=1e-5; lim1=1e-5; lim2=0.2; normalize_by_mean=True",
        },
    }

    expected = {
        "TOMOReconstruction_method": "FBP",
        "TOMOReconstruction_rotation_axis_position": 1011.6686,
        "TOMOReconstruction_cor_options": "side=1011.6686114352402",
        "TOMOReconstruction_angle_offset": 0.0,
        "TOMOReconstruction_fbp_filter_type": "ramlak",
        "TOMOReconstruction_fbp_filter_cutoff": 1.0,
        "TOMOReconstruction_padding_type": "edge",
        "TOMOReconstruction_enable_halftomo": False,
        "TOMOReconstruction_clip_outer_circle": False,
        "TOMOReconstruction_centered_axis": True,
        "TOMOReconstruction_start_x": 0,
        "TOMOReconstruction_end_x": -1,
        "TOMOReconstruction_start_y": 0,
        "TOMOReconstruction_end_y": -1,
        "TOMOReconstruction_start_z": 0,
        "TOMOReconstruction_end_z": -1,
        "TOMOReconstructionPhase_method": "Paganin",
        "TOMOReconstructionPhase_delta_beta": "100",
        "TOMOReconstructionPhase_unsharp_coeff": "0",
        "TOMOReconstructionPhase_unsharp_sigma": "0",
        "TOMOReconstructionPhase_unsharp_method": "gaussian",
        "TOMOReconstructionPhase_padding_type": "edge",
        "TOMOReconstructionPhase_ctf_geometry": "z1_v=None; z1_h=None; detec_pixel_size=None; magnification=True",
        "TOMOReconstructionPhase_ctf_advanced_params": "length_scale=1e-5; lim1=1e-5; lim2=0.2; normalize_by_mean=True",
        "workflow_type": "slices",
        "technique_pid": "http://purl.org/pan-science/ESRFET#XPCT",
        "definition": "XPCT",
    }

    result = dataportalupload._build_dataportal_metadata(processing_options)
    assert result == expected


def test_build_dataportal_metadata_with_string_none_method_skips_dataset_metadata():
    processing_options = {"phase": {"delta_beta": "100", "method": "None"}}
    result = dataportalupload._build_dataportal_metadata(processing_options)
    assert "TOMOReconstructionPhase_delta_beta" in result
    assert "definition" not in result
    assert "technique_pid" not in result
    assert result["workflow_type"] == "slices"


def test_build_dataportal_metadata_prefers_processing_options_for_recon():
    processing_options = {
        "reconstruction": {
            "start_z": 25,
            "rotation_axis_position": 1011.5,
            "fbp_filter_type": "ramlak",
        }
    }

    result = dataportalupload._build_dataportal_metadata(processing_options)
    assert result["TOMOReconstruction_start_z"] == 25
    assert result["TOMOReconstruction_rotation_axis_position"] == 1011.5
    assert result["TOMOReconstruction_fbp_filter_type"] == "ramlak"


def test_build_dataportal_metadata_task_handles_missing_and_invalid(caplog):
    task_missing = dataportalupload.BuildDataPortalMetadata(
        inputs={"processing_options": None}
    )
    task_missing.execute()
    assert task_missing.outputs.dataportal_metadata == {"workflow_type": "slices"}

    with pytest.raises(RuntimeError, match="Input should be a valid dictionary"):
        task_invalid = dataportalupload.BuildDataPortalMetadata(
            inputs={"processing_options": "not-a-dict"}
        )
        task_invalid.execute()
