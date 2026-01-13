import time
import uuid

import pytest

from hlid import HLID


def test_time_based_uniqueness():
    secret = uuid.uuid4().hex
    value1 = HLID(secret=secret)
    time.sleep(0.01)
    value2 = HLID(secret=secret)
    assert value1.hex != value2.hex


def test_invalid_user_data_case():
    user_data = "AA"
    with pytest.raises(ValueError) as e_info:
        _ = HLID(user_data=user_data)
    assert "must be lowercase" in str(e_info.value)


def test_invalid_user_data_chars():
    user_data = "xx"
    with pytest.raises(ValueError) as e_info:
        _ = HLID(user_data=user_data)
    assert "must contain only hex characters" in str(e_info.value)


def test_invalid_secret_length():
    secret = uuid.uuid4().hex[0:8]  # too short
    with pytest.raises(ValueError) as e_info:
        _ = HLID(secret=secret)
    assert "HLID secret too short" in str(e_info.value)


def test_hmac_validation_failure():
    secret = uuid.uuid4().hex
    value = HLID(secret=secret)
    with pytest.raises(ValueError) as e_info:
        _ = HLID(value.hex, secret=uuid.uuid4().hex)
    assert "HLID fails HMAC check" in str(e_info.value)


def test_invalid_value_random():
    value = uuid.uuid4().hex
    with pytest.raises(ValueError) as e_info:
        _ = HLID(value)
    assert "HLID invalid value" in str(e_info.value)


def test_invalid_value_malformed():
    value = uuid.uuid4().hex + "-" + uuid.uuid4().hex
    with pytest.raises(ValueError) as e_info:
        _ = HLID(value)
    assert "HLID invalid value" in str(e_info.value)


def test_invalid_value_case():
    value = str(HLID()).upper()
    with pytest.raises(ValueError) as e_info:
        _ = HLID(value)
    assert "lowercase hex chars only" in str(e_info.value)
