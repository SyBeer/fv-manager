import sys
sys.path.insert(0, "src")
from main import _validate_reading


def test_valid_reading():
    assert _validate_reading("2024.07", 500, 200, 100) is None


def test_sent_exceeds_production():
    err = _validate_reading("2024.07", 200, 300, 100)
    assert err is not None
    assert "przekroczyć" in err


def test_negative_production():
    err = _validate_reading("2024.07", -10, 0, 0)
    assert err is not None


def test_invalid_period_format():
    assert _validate_reading("2024-07", 100, 50, 30) is not None
    assert _validate_reading("24.07", 100, 50, 30) is not None
    assert _validate_reading("2024.13", 100, 50, 30) is not None
    assert _validate_reading("2024.00", 100, 50, 30) is not None


def test_sent_equals_production_is_valid():
    assert _validate_reading("2024.07", 500, 500, 0) is None


def test_zero_production_is_valid():
    assert _validate_reading("2024.12", 0, 0, 150) is None
