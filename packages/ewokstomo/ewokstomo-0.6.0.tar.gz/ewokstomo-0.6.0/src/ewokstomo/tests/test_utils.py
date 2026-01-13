from unittest.mock import Mock
from blissdata.redis_engine.scan import ScanState
from ewokstomo.tasks.utils import wait_for_scan_state


def test_wait_for_scan_state_reaches_desired_state():
    scan = Mock()
    states = [
        ScanState.CREATED.value,
        ScanState.PREPARED.value,
        ScanState.STARTED.value,
        ScanState.STOPPED.value,
    ]
    scan.state = states[0]

    def update_state():
        scan.state = states[scan.update.call_count]

    scan.update.side_effect = update_state

    wait_for_scan_state(scan, ScanState.STOPPED)

    assert scan.update.call_count == 3


def test_wait_for_scan_state_higher_state():
    scan = Mock()
    scan.state = ScanState.CREATED.value

    def update_state():
        scan.state = ScanState.STARTED.value

    scan.update.side_effect = update_state

    wait_for_scan_state(scan, ScanState.PREPARED)

    assert scan.update.call_count == 1
