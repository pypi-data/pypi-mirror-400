import time
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from hlid import HLID


def test_user_data_property():
    """Test that user_data property extracts the correct value"""
    hlid = HLID(user_data="ff")
    assert hlid.user_data == "ff"

    hlid2 = HLID(user_data="a5")
    assert hlid2.user_data == "a5"

    hlid3 = HLID(user_data="00")
    assert hlid3.user_data == "00"


def test_user_data_property_from_existing():
    """Test extracting user_data from existing HLID string"""
    test_value = "20250101-1234-5678-00ff-1234567890ab"
    hlid = HLID(test_value)
    assert hlid.user_data == "ff"


def test_comparison_operators_sorting():
    """Test that HLIDs can be sorted chronologically"""
    time.sleep(0.001)
    hlid1 = HLID()
    time.sleep(0.001)
    hlid2 = HLID()
    time.sleep(0.001)
    hlid3 = HLID()

    # Test less than
    assert hlid1 < hlid2
    assert hlid2 < hlid3
    assert hlid1 < hlid3

    # Test greater than
    assert hlid3 > hlid2
    assert hlid2 > hlid1
    assert hlid3 > hlid1

    # Test less than or equal
    assert hlid1 <= hlid2
    assert hlid1 <= hlid1

    # Test greater than or equal
    assert hlid3 >= hlid2
    assert hlid3 >= hlid3


def test_comparison_operators_with_list_sort():
    """Test that HLIDs can be sorted in a list"""
    time.sleep(0.001)
    hlid1 = HLID()
    time.sleep(0.001)
    hlid2 = HLID()
    time.sleep(0.001)
    hlid3 = HLID()

    # Shuffle the list
    hlids = [hlid3, hlid1, hlid2]

    # Sort the list
    sorted_hlids = sorted(hlids)

    # Verify chronological order
    assert sorted_hlids[0] == hlid1
    assert sorted_hlids[1] == hlid2
    assert sorted_hlids[2] == hlid3


def test_comparison_with_non_hlid():
    """Test that comparison with non-HLID returns NotImplemented"""
    hlid = HLID()

    # These should raise TypeError
    with pytest.raises(TypeError):
        _ = hlid < "string"

    with pytest.raises(TypeError):
        _ = hlid > 123

    with pytest.raises(TypeError):
        _ = hlid <= None


def test_from_datetime_basic():
    """Test creating HLID from a specific datetime"""
    dt = datetime(2024, 11, 5, 11, 8, 52, 0, tzinfo=timezone.utc)
    hlid = HLID.from_datetime(dt)

    assert hlid.datetime == dt
    assert hlid.datetime.year == 2024
    assert hlid.datetime.month == 11
    assert hlid.datetime.day == 5
    assert hlid.datetime.hour == 11
    assert hlid.datetime.minute == 8
    assert hlid.datetime.second == 52


def test_from_datetime_with_microseconds():
    """Test creating HLID from datetime with microseconds"""
    # 520000 microseconds = 5200 tenths of milliseconds
    dt = datetime(2024, 11, 5, 11, 8, 52, 520000, tzinfo=timezone.utc)
    hlid = HLID.from_datetime(dt)

    assert hlid.datetime.microsecond == 520000


def test_from_datetime_with_user_data():
    """Test creating HLID from datetime with custom user_data"""
    dt = datetime(2024, 11, 5, 11, 8, 52, 0, tzinfo=timezone.utc)
    hlid = HLID.from_datetime(dt, user_data="ff")

    assert hlid.user_data == "ff"
    assert hlid.datetime == dt


def test_from_datetime_with_secret():
    """Test creating signed HLID from datetime"""
    dt = datetime(2024, 11, 5, 11, 8, 52, 0, tzinfo=timezone.utc)
    secret = uuid.uuid4().hex

    hlid = HLID.from_datetime(dt, secret=secret)

    # Verify it can be reconstructed with the same secret
    hlid2 = HLID(hlid.hex, secret=secret)
    assert hlid.hex == hlid2.hex


def test_from_datetime_no_timezone():
    """Test that from_datetime requires timezone info"""
    dt = datetime(2024, 11, 5, 11, 8, 52, 0)  # No timezone

    with pytest.raises(ValueError) as e_info:
        _ = HLID.from_datetime(dt)

    assert "timezone information" in str(e_info.value)


def test_from_datetime_converts_to_utc():
    """Test that non-UTC timezones are converted to UTC"""
    # Create datetime in UTC+5
    from datetime import timezone as tz

    utc_plus_5 = tz(timedelta(hours=5))
    dt_plus_5 = datetime(2024, 11, 5, 16, 8, 52, 0, tzinfo=utc_plus_5)

    hlid = HLID.from_datetime(dt_plus_5)

    # Should be stored as UTC (16:08 in UTC+5 is 11:08 in UTC)
    assert hlid.datetime.hour == 11
    assert hlid.datetime.minute == 8
    assert hlid.datetime.tzinfo == timezone.utc


def test_from_datetime_roundtrip():
    """Test that datetime roundtrips correctly through from_datetime"""
    original_dt = datetime(2024, 11, 5, 11, 8, 52, 520000, tzinfo=timezone.utc)

    hlid = HLID.from_datetime(original_dt)
    extracted_dt = hlid.datetime

    assert extracted_dt == original_dt


def test_from_datetime_ordering():
    """Test that HLIDs created from_datetime maintain chronological order"""
    dt1 = datetime(2024, 11, 5, 11, 0, 0, 0, tzinfo=timezone.utc)
    dt2 = datetime(2024, 11, 5, 12, 0, 0, 0, tzinfo=timezone.utc)
    dt3 = datetime(2024, 11, 5, 13, 0, 0, 0, tzinfo=timezone.utc)

    hlid1 = HLID.from_datetime(dt1)
    hlid2 = HLID.from_datetime(dt2)
    hlid3 = HLID.from_datetime(dt3)

    assert hlid1 < hlid2 < hlid3
    assert sorted([hlid3, hlid1, hlid2]) == [hlid1, hlid2, hlid3]


def test_comparison_mixed_signed_unsigned():
    """Test comparing signed and unsigned HLIDs (should work based on string value)"""
    secret = uuid.uuid4().hex
    hlid_unsigned = HLID()
    time.sleep(0.001)
    hlid_signed = HLID(secret=secret)

    # Should be comparable (unsigned came first chronologically)
    assert hlid_unsigned < hlid_signed
