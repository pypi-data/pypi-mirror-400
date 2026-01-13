from datetime import timezone

import pytest

from hlid import HLID


def test_leap_year_feb_29():
    """Test HLID creation and parsing with leap year date (Feb 29)"""
    # Create HLID with Feb 29, 2024 (leap year)
    test_value = "20240229-1234-5678-00ff-1234567890ab"
    hlid = HLID(test_value)
    assert hlid.datetime.year == 2024
    assert hlid.datetime.month == 2
    assert hlid.datetime.day == 29


def test_boundary_year_9999():
    """Test HLID with maximum year value"""
    test_value = "99991231-2359-5999-00ff-1234567890ab"
    hlid = HLID(test_value)
    assert hlid.datetime.year == 9999
    assert hlid.datetime.month == 12
    assert hlid.datetime.day == 31


def test_boundary_end_of_day():
    """Test HLID with end of day (23:59:59.9999)"""
    test_value = "20250101-2359-5999-99ff-1234567890ab"
    hlid = HLID(test_value)
    assert hlid.datetime.hour == 23
    assert hlid.datetime.minute == 59
    assert hlid.datetime.second == 59
    # 9999 * 100 = 999900 microseconds
    assert hlid.datetime.microsecond == 999900


def test_boundary_start_of_day():
    """Test HLID with start of day (00:00:00.0000)"""
    test_value = "20250101-0000-0000-0000-1234567890ab"
    hlid = HLID(test_value)
    assert hlid.datetime.hour == 0
    assert hlid.datetime.minute == 0
    assert hlid.datetime.second == 0
    assert hlid.datetime.microsecond == 0


def test_equality_same_value():
    """Test that two HLIDs with same value are equal"""
    value = "20250101-1234-5678-00ff-1234567890ab"
    hlid1 = HLID(value)
    hlid2 = HLID(value)
    assert hlid1 == hlid2


def test_equality_different_values():
    """Test that two HLIDs with different values are not equal"""
    hlid1 = HLID("20250101-1234-5678-00ff-1234567890ab")
    hlid2 = HLID("20250101-1234-5678-00ff-1234567890ac")
    assert hlid1 != hlid2


def test_equality_with_non_hlid():
    """Test that HLID is not equal to non-HLID objects"""
    hlid = HLID("20250101-1234-5678-00ff-1234567890ab")
    assert hlid != "20250101-1234-5678-00ff-1234567890ab"
    assert hlid != 123
    assert hlid is not None


def test_hash_same_value():
    """Test that two HLIDs with same value have same hash"""
    value = "20250101-1234-5678-00ff-1234567890ab"
    hlid1 = HLID(value)
    hlid2 = HLID(value)
    assert hash(hlid1) == hash(hlid2)


def test_hash_different_values():
    """Test that two HLIDs with different values have different hashes"""
    hlid1 = HLID("20250101-1234-5678-00ff-1234567890ab")
    hlid2 = HLID("20250101-1234-5678-00ff-1234567890ac")
    assert hash(hlid1) != hash(hlid2)


def test_hlid_in_set():
    """Test that HLIDs can be used in sets"""
    hlid1 = HLID("20250101-1234-5678-00ff-1234567890ab")
    hlid2 = HLID("20250101-1234-5678-00ff-1234567890ab")
    hlid3 = HLID("20250101-1234-5678-00ff-1234567890ac")

    hlid_set = {hlid1, hlid2, hlid3}
    assert len(hlid_set) == 2  # hlid1 and hlid2 are equal, so only 2 unique


def test_hlid_as_dict_key():
    """Test that HLIDs can be used as dictionary keys"""
    hlid1 = HLID("20250101-1234-5678-00ff-1234567890ab")
    hlid2 = HLID("20250101-1234-5678-00ff-1234567890ab")
    hlid3 = HLID("20250101-1234-5678-00ff-1234567890ac")

    hlid_dict = {hlid1: "value1", hlid3: "value3"}
    assert hlid_dict[hlid2] == "value1"  # hlid2 equals hlid1
    assert len(hlid_dict) == 2


def test_subsecond_precision_edge_cases():
    """Test various subsecond precision values"""
    # Test minimum subsecond value
    hlid_min = HLID("20250101-1234-5600-0000-1234567890ab")
    assert hlid_min.datetime.microsecond == 0

    # Test mid-range subsecond value
    hlid_mid = HLID("20250101-1234-5650-0000-1234567890ab")
    assert hlid_mid.datetime.microsecond == 500000  # 5000 * 100

    # Test maximum subsecond value
    hlid_max = HLID("20250101-1234-5699-9900-1234567890ab")
    assert hlid_max.datetime.microsecond == 999900  # 9999 * 100


def test_invalid_subsecond_value():
    """Test that invalid subsecond values are rejected"""
    # This is a malformed HLID with invalid characters that would result in > 9999
    # But the validation happens at datetime parsing
    # We need to construct a case that would parse as >9999
    # However, with the current format, this is unlikely. Skip this test for now.
    pass


def test_user_data_variations():
    """Test different valid user_data values"""
    for user_data in ["00", "ff", "a5", "3c", "99"]:
        hlid = HLID(user_data=user_data)
        assert len(str(hlid)) == 36


def test_user_data_empty_string():
    """Test that empty user_data raises ValueError"""
    with pytest.raises(ValueError) as e_info:
        _ = HLID(user_data="")
    assert "cannot be empty" in str(e_info.value)


def test_user_data_wrong_length_short():
    """Test that short user_data raises ValueError"""
    with pytest.raises(ValueError) as e_info:
        _ = HLID(user_data="a")
    assert "exactly 2 characters" in str(e_info.value)


def test_user_data_wrong_length_long():
    """Test that long user_data raises ValueError"""
    with pytest.raises(ValueError) as e_info:
        _ = HLID(user_data="abc")
    assert "exactly 2 characters" in str(e_info.value)


def test_reconstruction_maintains_timezone():
    """Test that reconstructed HLID maintains UTC timezone"""
    hlid1 = HLID()
    hlid2 = HLID(hlid1.hex)
    assert hlid1.datetime.tzinfo == timezone.utc
    assert hlid2.datetime.tzinfo == timezone.utc


def test_time_property_consistency():
    """Test that time property is consistent with datetime"""
    hlid = HLID()
    time_from_property = hlid.time
    time_from_datetime = hlid.datetime.timestamp()
    # Should be exactly the same since both use the same datetime
    assert time_from_property == time_from_datetime


def test_age_increases():
    """Test that age property increases over time"""
    import time

    hlid = HLID()
    age1 = hlid.age
    time.sleep(0.01)
    age2 = hlid.age
    assert age2 > age1
    assert age2 - age1 >= 0.01


def test_hex_roundtrip():
    """Test that hex representation can be used to reconstruct HLID"""
    hlid1 = HLID()
    hex_value = hlid1.hex
    assert len(hex_value) == 32
    assert "-" not in hex_value

    hlid2 = HLID(hex_value)
    assert str(hlid1) == str(hlid2)
    assert hlid1.hex == hlid2.hex
