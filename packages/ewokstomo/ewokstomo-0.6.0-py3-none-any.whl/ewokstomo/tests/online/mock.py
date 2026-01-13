from blissdata.exceptions import EndOfStream
from blissdata.redis_engine.scan import ScanState
from unittest.mock import MagicMock
import numpy as np


class FakeCursor:
    def __init__(self, arrays):
        self._arrays = arrays
        self._i = 0

    def read(self):
        if self._i >= len(self._arrays):
            raise EndOfStream()
        arr = np.array(self._arrays[self._i])
        self._i += 1
        return MagicMock(get_data=lambda: arr)


class FakeStream:
    def __init__(self, arrays):
        self._arrays = arrays

    def cursor(self):
        return FakeCursor(self._arrays)


class FakeScan:
    def __init__(self, arrays, title):
        self.info = {"title": title}
        self.streams = {f"{title}:image": FakeStream(arrays)}
        self.state = ScanState.CLOSED


class FakeImageStream:
    """Mock image stream that provides projections with length support."""

    def __init__(self, arrays):
        self._arrays = arrays

    def __len__(self):
        return len(self._arrays)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return [np.array(arr) for arr in self._arrays[key]]
        return np.array(self._arrays[key])

    def cursor(self):
        from ewokstomo.tests.online.mock import FakeCursor

        return FakeCursor(self._arrays)


class FakeMotorStream:
    """Mock motor stream that provides rotation angles."""

    def __init__(self, angles):
        self._angles = angles

    def __len__(self):
        return len(self._angles)

    def __getitem__(self, key):
        return self._angles[key]


class FakeScanWithMotor(FakeScan):
    """Extended FakeScan that includes motor stream for angles."""

    def __init__(self, arrays, angles, title, rotation_motor="rot"):
        super().__init__(arrays, title)
        # Replace the FakeStream with FakeImageStream that supports len()
        self.streams[f"{title}:image"] = FakeImageStream(arrays)
        self.streams[f"{rotation_motor}:axis:rx"] = FakeMotorStream(angles)
