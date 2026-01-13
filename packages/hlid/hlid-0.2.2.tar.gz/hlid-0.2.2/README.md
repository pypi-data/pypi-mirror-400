# HLID: a Human Lexicographically (sortable) Identifier

[![pypi](https://img.shields.io/pypi/v/hlid.svg)](https://pypi.python.org/pypi/hlid/)
[![python](https://img.shields.io/pypi/pyversions/hlid.svg)](https://github.com/threatpatrols/hlid/)
[![build tests](https://github.com/threatpatrols/hlid/actions/workflows/build-tests.yml/badge.svg)](https://github.com/threatpatrols/hlid/actions/workflows/build-tests.yml)
[![license](https://img.shields.io/github/license/threatpatrols/hlid.svg)](https://github.com/threatpatrols/hlid)

The HLID is a human-readable lexicographically sortable identifier that borrows 
similar concepts from -

 * ULID (Universally-Unique, Lexicographically-Sortable Identifier) - [github.com/ulid](https://github.com/ulid/spec)
 * UUID7 (Time-ordered UUID with millisecond precision) - [ietf.org](https://www.ietf.org/archive/id/draft-peabody-dispatch-new-uuid-format-04.html#name-uuid-version-7)

HLIDs have the following properties -

 * Time sortable
 * Human readable in UTC timezone
 * 10^4 seconds time resolution (tenth of milliseconds)
 * 8 bits of user-data (two hex chars)
 * 48 bits of nonce; optionally derived from a truncated hmac-sha256 (12x hex chars)
 * Can be swapped with UUID-type or ULID-type values

With all good things there are tradeoffs -

 * These values are not cryptographically secure for inputs into to strong 
   crypto routines.
 * HLID can provide at best tenth-of-millisecond time resolution, whereas UUID7
   provides 50 nanosecond resolution.
 * Because the HMAC is truncated, a larger secret value is enforced (128 bits).

For example a HLID value -

```text
    20241105-1108-5200-00ff-8fa646f09a7e
    ^        ^    ^ ^  ^ ^  ^
    |        |    | |  | |  |- 12x hex: nonce-value -or- hmac-value
    |        |    | |  | |- 2x hex: one byte of user-data; 2x hex chars
    |        |    | |+ |- 4x digits: -10^4 seconds; tenth of millisecond
    |        |    |- 2x digits: seconds
    |        |- 4x digits: hours and minutes
    |- 8x digits: year and month and day
    
    All values are zero-padded when required.
```

# Install
```commandline
pipx install hlid
```

# Usage

### Example: HLID attributes
```python
>>> from hlid import HLID
>>> hlid = HLID()

>>> print(str(hlid))
20250213-1615-0320-9000-723da4092594

>>> print(f"{hlid.hex=}")
hlid.hex='20250213161503209000723da4092594'

>>> print(f"{hlid.age=}")
hlid.age=0.000799

>>> print(f"{hlid.time=}")
hlid.time=1739463303.209

>>> print(f"{hlid.datetime=}")
hlid.datetime=datetime.datetime(2025, 2, 13, 16, 15, 3, 209000, tzinfo=datetime.timezone.utc)
```


### Example: Handle existing HLID values
```python
>>> from hlid import HLID

>>> hlid1 = HLID()
>>> hlid2 = HLID(hlid1.hex)
>>> assert hlid1.hex == hlid2.hex
```


### Example: HMAC signed HLIDs
```python
>>> from hlid import hlid, HLID
>>> from uuid import uuid4

>>> secret = uuid4().hex
>>> hlid_signed = hlid(secret=secret)

>>> print(hlid_signed)
20250213-1613-0211-8000-c199fc3695c5

>>> hlid_test = HLID(hlid_signed.hex, secret=secret)
>>> print(hlid_test)
20250213-1613-0211-8000-c199fc3695c5

>>> bad_secret = uuid4().hex
>>> HLID(hlid_signed.hex, secret=bad_secret)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/ndejong/.local/venvs/hlid/lib/python3.12/site-packages/hlid/__init__.py", line 65, in __init__
    raise ValueError("HLID fails HMAC check.")
ValueError: HLID fails HMAC check.

```

### Example: User data byte
```python
>>> from hlid import HLID

>>> # Create HLID with custom user data
>>> hlid = HLID(user_data="ff")
>>> print(f"{hlid.user_data=}")
hlid.user_data='ff'

>>> # Extract user data from existing HLID
>>> existing = HLID("20250213-1615-0320-90ff-723da4092594")
>>> print(f"{existing.user_data=}")
existing.user_data='ff'
```

### Example: Sorting and comparison
```python
>>> from hlid import HLID

>>> # HLIDs are lexicographically sortable
>>> hlid1 = HLID()
>>> hlid2 = HLID()
>>> hlid3 = HLID()

>>> assert hlid1 < hlid2 < hlid3
>>> sorted_hlids = sorted([hlid3, hlid1, hlid2])
>>> assert sorted_hlids == [hlid1, hlid2, hlid3]
```

### Example: Creating HLIDs from specific datetimes
```python
>>> from hlid import HLID
>>> from datetime import datetime, timezone

>>> # Create HLID for a specific point in time
>>> dt = datetime(2024, 11, 5, 11, 8, 52, 520000, tzinfo=timezone.utc)
>>> hlid = HLID.from_datetime(dt)
>>> print(hlid)
20241105-1108-5252-0000-c8f3a1b2d4e5

>>> print(f"{hlid.datetime=}")
hlid.datetime=datetime.datetime(2024, 11, 5, 11, 8, 52, 520000, tzinfo=datetime.timezone.utc)
```
