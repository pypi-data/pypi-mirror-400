"""Tests for halea exception hierarchy."""

import pytest

from halea.exceptions import BackendNotAvailableError
from halea.exceptions import DeviceConnectionError
from halea.exceptions import DeviceNotFoundError
from halea.exceptions import DeviceReadError
from halea.exceptions import HaleaError


class TestExceptionHierarchy:
    """Test that all exceptions have correct inheritance."""

    def test_halea_error_inherits_from_exception(self) -> None:
        """HaleaError should inherit from Exception."""
        assert issubclass(HaleaError, Exception)

    def test_device_not_found_inherits_from_halea_error(self) -> None:
        """DeviceNotFoundError should inherit from HaleaError."""
        assert issubclass(DeviceNotFoundError, HaleaError)

    def test_device_connection_error_inherits_from_halea_error(self) -> None:
        """DeviceConnectionError should inherit from HaleaError."""
        assert issubclass(DeviceConnectionError, HaleaError)

    def test_device_read_error_inherits_from_halea_error(self) -> None:
        """DeviceReadError should inherit from HaleaError."""
        assert issubclass(DeviceReadError, HaleaError)

    def test_backend_not_available_inherits_from_halea_error(self) -> None:
        """BackendNotAvailableError should inherit from HaleaError."""
        assert issubclass(BackendNotAvailableError, HaleaError)


class TestExceptionRaising:
    """Test that exceptions can be raised and caught properly."""

    def test_halea_error_can_be_raised_with_message(self) -> None:
        """HaleaError should accept and preserve message."""
        msg = "Test error message"
        with pytest.raises(HaleaError) as exc_info:
            raise HaleaError(msg)
        assert str(exc_info.value) == msg

    def test_device_not_found_can_be_raised_with_message(self) -> None:
        """DeviceNotFoundError should accept and preserve message."""
        msg = "No device found"
        with pytest.raises(DeviceNotFoundError) as exc_info:
            raise DeviceNotFoundError(msg)
        assert str(exc_info.value) == msg

    def test_device_connection_error_can_be_raised_with_message(self) -> None:
        """DeviceConnectionError should accept and preserve message."""
        msg = "Connection failed"
        with pytest.raises(DeviceConnectionError) as exc_info:
            raise DeviceConnectionError(msg)
        assert str(exc_info.value) == msg

    def test_device_read_error_can_be_raised_with_message(self) -> None:
        """DeviceReadError should accept and preserve message."""
        msg = "Read failed"
        with pytest.raises(DeviceReadError) as exc_info:
            raise DeviceReadError(msg)
        assert str(exc_info.value) == msg

    def test_backend_not_available_can_be_raised_with_message(self) -> None:
        """BackendNotAvailableError should accept and preserve message."""
        msg = "Backend not available"
        with pytest.raises(BackendNotAvailableError) as exc_info:
            raise BackendNotAvailableError(msg)
        assert str(exc_info.value) == msg


class TestExceptionCatching:
    """Test that base exception catches all specific exceptions."""

    def test_catching_halea_error_catches_device_not_found(self) -> None:
        """Catching HaleaError should catch DeviceNotFoundError."""
        with pytest.raises(HaleaError):
            raise DeviceNotFoundError("test")

    def test_catching_halea_error_catches_device_connection_error(self) -> None:
        """Catching HaleaError should catch DeviceConnectionError."""
        with pytest.raises(HaleaError):
            raise DeviceConnectionError("test")

    def test_catching_halea_error_catches_device_read_error(self) -> None:
        """Catching HaleaError should catch DeviceReadError."""
        with pytest.raises(HaleaError):
            raise DeviceReadError("test")

    def test_catching_halea_error_catches_backend_not_available(self) -> None:
        """Catching HaleaError should catch BackendNotAvailableError."""
        with pytest.raises(HaleaError):
            raise BackendNotAvailableError("test")

    def test_catching_specific_exception_works(self) -> None:
        """Specific exceptions should be catchable individually."""
        try:
            raise DeviceNotFoundError("test")
        except DeviceNotFoundError:
            pass  # Expected
        except HaleaError:
            pytest.fail("DeviceNotFoundError should be caught by specific handler first")

    def test_catching_wrong_specific_does_not_catch(self) -> None:
        """Wrong specific exception should not catch."""
        with pytest.raises(DeviceNotFoundError):
            try:
                raise DeviceNotFoundError("test")
            except DeviceConnectionError:
                pytest.fail("DeviceConnectionError should not catch DeviceNotFoundError")


class TestExceptionInstances:
    """Test exception instance properties."""

    def test_exception_is_instance_of_exception(self) -> None:
        """All halea exceptions should be instances of Exception."""
        exceptions = [
            HaleaError("test"),
            DeviceNotFoundError("test"),
            DeviceConnectionError("test"),
            DeviceReadError("test"),
            BackendNotAvailableError("test"),
        ]
        for exc in exceptions:
            assert isinstance(exc, Exception)

    def test_exception_is_instance_of_halea_error(self) -> None:
        """All specific exceptions should be instances of HaleaError."""
        exceptions = [
            DeviceNotFoundError("test"),
            DeviceConnectionError("test"),
            DeviceReadError("test"),
            BackendNotAvailableError("test"),
        ]
        for exc in exceptions:
            assert isinstance(exc, HaleaError)

    def test_exceptions_are_distinct_types(self) -> None:
        """Each exception should be a distinct type."""
        exception_types = [
            HaleaError,
            DeviceNotFoundError,
            DeviceConnectionError,
            DeviceReadError,
            BackendNotAvailableError,
        ]
        # All types should be unique
        assert len(exception_types) == len(set(exception_types))
