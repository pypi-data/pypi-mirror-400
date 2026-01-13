import uuid

from hlid import HLID, hlid


def test_generation_defaults():
    value = HLID()
    assert value.age < 1
    assert value.age > 0
    assert len(str(value).split("-")) == 5
    assert str(value).replace("-", "") == value.hex
    assert value.time > 0
    assert value.time < 9999999999


def test_generation_with_secret():
    value = HLID(secret=uuid.uuid4().hex)
    assert value.age < 1
    assert value.age > 0
    assert len(str(value).split("-")) == 5
    assert str(value).replace("-", "") == value.hex
    assert value.time > 0


def test_reconstruction_from_hex():
    value = HLID()
    result = HLID(value.hex)
    assert str(value) == str(result)


def test_uniqueness():
    assert HLID() != HLID()
    assert HLID().hex != HLID().hex


def test_reconstruction_signed():
    secret = uuid.uuid4().hex
    value = HLID(secret=secret)
    result = HLID(value.hex, secret=secret)
    assert value.hex == result.hex


def test_generation_with_user_data():
    user_data = "aa"
    value = HLID(user_data=user_data)
    result = HLID(value.hex)
    assert str(value) == str(result)


def test_generation_with_secret_and_user_data():
    user_data = "aa"
    secret = uuid.uuid4().hex
    value = HLID(secret=secret, user_data=user_data)
    result = HLID(str(value), secret=secret)
    assert value.hex == result.hex


def test_helper_function():
    secret = uuid.uuid4().hex
    value = hlid(secret)
    assert value.hex == HLID(value.hex, secret=secret).hex
