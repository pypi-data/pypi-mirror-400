"""Tests for test helper utilities.

This module tests the network isolation helpers in test_helpers.py
to ensure they correctly block network access in offline tests.

Testing Philosophy:
- These tests validate that our helper utilities work correctly
- They test REAL behavior (the helpers actually block network calls)
- No over-mocking - we call the real helper functions and verify they work
- Focus: Ensuring offline_mode and @no_network provide network isolation
"""

import socket

import pytest
import requests

from tests.test_helpers import NetworkAccessError, block_network, no_network, offline_mode


class TestNetworkBlocking:
    """Test network isolation utilities.

    These tests verify that offline_mode() and @no_network correctly
    prevent network access by patching external network libraries.
    """

    def test_block_network_raises_error(self):
        """Test that block_network function raises NetworkAccessError.

        This is the core function that raises when network is attempted.
        It's used as the side_effect in patches.
        """
        with pytest.raises(NetworkAccessError) as exc_info:
            block_network()

        assert "Network access attempted in offline test" in str(exc_info.value)

    def test_offline_mode_blocks_socket(self):
        """Test that offline_mode context manager blocks socket creation.

        Verifies that low-level socket access is blocked - this catches
        any network library that uses sockets directly.
        """
        with offline_mode():
            with pytest.raises(NetworkAccessError):
                socket.socket()

    def test_offline_mode_blocks_urllib3(self):
        """Test that offline_mode context manager blocks urllib3.

        Verifies that urllib3 (used by requests and many HTTP libraries)
        is blocked at the connection pool level.
        """
        with offline_mode():
            # Import inside context to ensure patch is active
            import urllib3

            with pytest.raises(NetworkAccessError):
                urllib3.PoolManager()

    def test_offline_mode_blocks_requests(self):
        """Test that offline_mode context manager blocks requests library.

        Verifies that the popular requests library cannot make HTTP calls
        when offline mode is active.
        """
        with offline_mode():
            with pytest.raises(NetworkAccessError):
                requests.get("https://example.com")

    def test_offline_mode_blocks_gitlab_client(self):
        """Test that offline_mode context manager blocks GitLab client creation.

        Verifies that python-gitlab library is blocked at initialization.
        This is critical since our code interacts heavily with GitLab.
        """
        with offline_mode():
            # Import inside context to ensure patch is active
            import gitlab

            with pytest.raises(NetworkAccessError):
                gitlab.Gitlab("https://gitlab.example.com", private_token="test")

    def test_no_network_decorator(self):
        """Test that @no_network decorator blocks network access.

        Verifies the decorator form works correctly - useful for marking
        entire test functions as offline-only.
        """

        @no_network
        def function_that_tries_network():
            # This should raise NetworkAccessError
            socket.socket()

        with pytest.raises(NetworkAccessError):
            function_that_tries_network()

    def test_no_network_decorator_allows_normal_code(self):
        """Test that @no_network decorator allows non-network code to run.

        Verifies that the decorator doesn't break normal Python operations.
        Only network access should be blocked.
        """

        @no_network
        def function_with_normal_code():
            # Normal Python code should work fine
            return 42

        result = function_with_normal_code()
        assert result == 42

    def test_no_network_decorator_with_arguments(self):
        """Test that @no_network decorator works with function arguments.

        Verifies that @wraps() is used correctly so decorated functions
        maintain their signature and can accept arguments.
        """

        @no_network
        def function_with_args(x, y):
            return x + y

        result = function_with_args(10, 20)
        assert result == 30

    def test_offline_mode_is_reentrant(self):
        """Test that offline_mode can be used multiple times.

        Verifies that the context manager properly cleans up patches
        and can be used repeatedly in the same test session.
        """
        # First usage
        with offline_mode():
            with pytest.raises(NetworkAccessError):
                socket.socket()

        # Second usage - should work independently
        with offline_mode():
            with pytest.raises(NetworkAccessError):
                socket.socket()

        # After exiting, patches are removed and context manager exits cleanly


class TestNetworkAccessError:
    """Test the custom NetworkAccessError exception.

    This exception is raised when network access is attempted in offline mode.
    It provides clear error messages to help developers understand the issue.
    """

    def test_exception_is_subclass_of_exception(self):
        """Test that NetworkAccessError is a proper Exception subclass.

        Verifies the exception can be caught with standard exception handling.
        """
        assert issubclass(NetworkAccessError, Exception)

    def test_exception_can_be_raised_and_caught(self):
        """Test that NetworkAccessError can be raised and caught.

        Verifies the exception works with pytest.raises() and standard
        exception handling.
        """
        with pytest.raises(NetworkAccessError) as exc_info:
            raise NetworkAccessError("Test message")

        assert "Test message" in str(exc_info.value)

    def test_exception_message_from_block_network(self):
        """Test the default error message from block_network.

        Verifies the error message is helpful and guides developers to
        use @no_network decorator or proper mocking.
        """
        with pytest.raises(NetworkAccessError) as exc_info:
            block_network()

        expected_message = (
            "Network access attempted in offline test. "
            "Use @no_network decorator or mock the network call."
        )
        assert str(exc_info.value) == expected_message
