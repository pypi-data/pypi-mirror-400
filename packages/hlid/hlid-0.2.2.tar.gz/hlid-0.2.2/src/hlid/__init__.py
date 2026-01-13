import hashlib
import hmac
from datetime import datetime as dt_datetime, timezone
from typing import Optional
from uuid import uuid4

__version__ = "0.2.2"


class HLID:
    """
    A human-readable twist on ULID/UUID values; A unique human-time-lexicographically sortable
    identifier using the same form as a UUID4 which makes it possible to use with existing UUID4
    systems such as database storage and validators.

        20241105-1108-5200-00ff-8fa646f09a7e
        ^        ^    ^ ^  ^ ^  ^
        |        |    | |  | |  |- 12x hex: nonce-value -or- hmac-value
        |        |    | |  | |- 2x hex: one byte of user-data; 2x hex chars
        |        |    | |+ |- 4x digits: -10^4 seconds; tenth of millisecond
        |        |    |- 2x digits: seconds
        |        |- 4x digits: hours and minutes
        |- 8x digits: year and month and day

    HLID example value:     20241105-0153-0041-0874-67961ce919d7
    UUID4 comparison value: 1c21583a-9b17-11ef-99e9-d34117a8d86d

    :return: str
    """

    _value: str
    _is_signed: bool = False

    def __init__(self, value: Optional[str] = None, secret: Optional[str] = None, user_data: str = "00") -> None:
        # Validate user_data
        if not user_data:
            raise ValueError("HLID user-data cannot be empty.")
        if len(user_data) != 2:
            raise ValueError(f"HLID user-data must be exactly 2 characters, got {len(user_data)}.")
        if user_data != user_data.lower():
            raise ValueError(f"HLID user-data must be lowercase, got '{user_data}'.")
        try:
            _ = int(user_data, 16)  # test to make sure user-data is hex
        except ValueError:
            raise ValueError(f"HLID user-data must contain only hex characters, got '{user_data}'.")

        if value:
            if value != value.lower():
                raise ValueError("HLID invalid, be lowercase hex chars only.")
            if len(value) == 32:
                value = f"{value[0:8]}-{value[8:12]}-{value[12:16]}-{value[16:20]}-{value[20:32]}"  # transmorph
            self._value = value
        else:
            ts = dt_datetime.now(timezone.utc)
            ts_subseconds = ts.strftime("%f")[0:4]
            hlid_ts = f"{ts.strftime('%Y%m%d-%H%M-%S')}{ts_subseconds[:2]}-{ts_subseconds[2:]}{user_data}"
            hlid_ts_suffix = self.__trunc_sha256_hmac_else_nonce(value=hlid_ts, secret=secret)
            self._value = f"{hlid_ts}-{hlid_ts_suffix}"

        if secret:
            if len(secret) < 16:
                raise ValueError("HLID secret too short; must be 16 chars or longer.")

            self._is_signed = True

            hlid_ts = "-".join(self._value.split("-")[0:-1])
            hlid_sign = self._value.split("-")[-1]
            if hlid_sign != self.__trunc_sha256_hmac_else_nonce(value=hlid_ts, secret=secret):
                raise ValueError("HLID fails HMAC check.")

        try:
            _ = self.age  # test to make sure the _value is a valid HLID
        except (ValueError, IndexError):
            raise ValueError("HLID invalid value.")

    def __call__(self) -> str:
        return self._value

    def __repr__(self) -> str:
        if self._is_signed:
            return f"HLID({self._value})s"
        return f"HLID({self._value})"

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        """
        Compare two HLID instances for equality based on their string values.

        :param other: Another object to compare with
        :return: True if both HLIDs have the same value, False otherwise
        """
        if not isinstance(other, HLID):
            return False
        return self._value == other._value

    def __hash__(self) -> int:
        """
        Return hash of the HLID value to allow use in sets and as dict keys.

        :return: Hash of the HLID string value
        """
        return hash(self._value)

    def __lt__(self, other: object) -> bool:
        """
        Less than comparison for lexicographic sorting.

        :param other: Another HLID instance to compare with
        :return: True if this HLID is less than the other
        :raises TypeError: If other is not an HLID instance
        """
        if not isinstance(other, HLID):
            return NotImplemented
        return self._value < other._value

    def __le__(self, other: object) -> bool:
        """
        Less than or equal comparison for lexicographic sorting.

        :param other: Another HLID instance to compare with
        :return: True if this HLID is less than or equal to the other
        :raises TypeError: If other is not an HLID instance
        """
        if not isinstance(other, HLID):
            return NotImplemented
        return self._value <= other._value

    def __gt__(self, other: object) -> bool:
        """
        Greater than comparison for lexicographic sorting.

        :param other: Another HLID instance to compare with
        :return: True if this HLID is greater than the other
        :raises TypeError: If other is not an HLID instance
        """
        if not isinstance(other, HLID):
            return NotImplemented
        return self._value > other._value

    def __ge__(self, other: object) -> bool:
        """
        Greater than or equal comparison for lexicographic sorting.

        :param other: Another HLID instance to compare with
        :return: True if this HLID is greater than or equal to the other
        :raises TypeError: If other is not an HLID instance
        """
        if not isinstance(other, HLID):
            return NotImplemented
        return self._value >= other._value

    @property
    def hex(self) -> str:
        """
        Return the HLID as a string with the "-" removed
        :return: str
        """
        return str(self._value).replace("-", "")

    @property
    def user_data(self) -> str:
        """
        Extract and return the user-data byte from the HLID.

        The user-data is stored at positions 21-23 in the formatted HLID string
        (2 hex characters representing one byte).

        :return: Two-character hex string representing the user-data byte
        """
        return self._value[21:23]

    @property
    def age(self) -> float:
        """
        Return the age in seconds of the HLID value
        :return: float
        """
        return (dt_datetime.now(timezone.utc) - self.datetime).total_seconds()

    @property
    def time(self) -> float:
        """
        Return the time-since-epoch time value of the HLID value
        :return: float
        """
        return self.datetime.timestamp()

    @property
    def datetime(self) -> dt_datetime:
        """
        Return the datetime that the HLID value represents.

        The HLID format encodes time with 10^-4 second resolution (tenths of milliseconds).
        This is converted to microseconds by multiplying by 100:
        - HLID subsecond value range: 0000-9999 (represents 0.0000s to 0.9999s)
        - Microsecond range: 0-999900 (0.9999s * 1000000 µs/s = 999900 µs)

        :return: datetime object in UTC timezone
        """
        # Extract subsecond component (4 digits spanning position 16-21 with hyphen at 18)
        subsecond_str = self._value[16:21].replace("-", "")
        subsecond_value = int(subsecond_str)

        # Convert from 10^-4 seconds to microseconds (multiply by 100)
        # Example: "5200" -> 5200 * 100 = 520000 microseconds = 0.52 seconds
        if subsecond_value > 9999:
            raise ValueError(f"HLID subsecond value out of range: {subsecond_value} (max 9999)")

        return dt_datetime(
            year=int(self._value[0:4]),
            month=int(self._value[4:6]),
            day=int(self._value[6:8]),
            hour=int(self._value[9:11]),
            minute=int(self._value[11:13]),
            second=int(self._value[14:16]),
            microsecond=subsecond_value * 100,
            tzinfo=timezone.utc,
        )

    @classmethod
    def from_datetime(cls, dt: dt_datetime, user_data: str = "00", secret: Optional[str] = None) -> "HLID":
        """
        Create an HLID from a specific datetime object.

        This allows generating HLIDs with a specific timestamp instead of the current time.
        Useful for backdating identifiers or creating test data.

        :param dt: datetime object (will be converted to UTC if it has timezone info)
        :param user_data: Two-character lowercase hex string for user data (default "00")
        :param secret: Optional secret for HMAC signing (must be 16+ characters)
        :return: New HLID instance with the specified datetime
        :raises ValueError: If datetime has no timezone info or user_data is invalid
        """
        if dt.tzinfo is None:
            raise ValueError("datetime must have timezone information (use timezone.utc or other tzinfo)")

        # Convert to UTC if not already
        dt_utc = dt.astimezone(timezone.utc)

        # Format timestamp components
        # Get microseconds and convert to 10^-4 seconds (0-9999 range)
        subsecond_value = dt_utc.microsecond // 100  # Convert microseconds to tenths of milliseconds
        subsecond_str = f"{subsecond_value:04d}"  # Zero-pad to 4 digits

        # Validate user_data before embedding it
        if not user_data:
            raise ValueError("HLID user-data cannot be empty.")
        if len(user_data) != 2:
            raise ValueError(f"HLID user-data must be exactly 2 characters, got {len(user_data)}.")
        if user_data != user_data.lower():
            raise ValueError(f"HLID user-data must be lowercase, got '{user_data}'.")
        try:
            _ = int(user_data, 16)
        except ValueError:
            raise ValueError(f"HLID user-data must contain only hex characters, got '{user_data}'.")

        # Build the HLID timestamp part
        hlid_ts = f"{dt_utc.strftime('%Y%m%d-%H%M-%S')}{subsecond_str[:2]}-{subsecond_str[2:]}{user_data}"

        # Generate the nonce or HMAC suffix
        hlid_ts_suffix = _trunc_sha256_hmac_else_nonce(value=hlid_ts, secret=secret)
        hlid_value = f"{hlid_ts}-{hlid_ts_suffix}"

        # Create and return the HLID instance (pass user_data from the constructed value)
        return cls(value=hlid_value, secret=secret)

    def __trunc_sha256_hmac_else_nonce(self, value: str, secret: Optional[str] = None) -> str:
        return _trunc_sha256_hmac_else_nonce(value, secret)


def _trunc_sha256_hmac_else_nonce(value: str, secret: Optional[str] = None) -> str:
    """Helper function to generate nonce or HMAC suffix."""
    if not secret:
        return str(uuid4()).split("-")[-1]  # = 12 random hex chars

    # = first 12 sha256-hmac hex chars
    return hmac.new(secret.encode(), msg=value.encode(), digestmod=hashlib.sha256).hexdigest()[0:12]


def hlid(secret: Optional[str] = None) -> HLID:
    return HLID(secret=secret)
