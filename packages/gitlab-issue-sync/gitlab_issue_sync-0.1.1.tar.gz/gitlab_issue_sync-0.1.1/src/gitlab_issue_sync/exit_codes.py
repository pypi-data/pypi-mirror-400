"""Exit codes for the gl-issue-sync CLI.

This module defines standard exit codes for different error types,
enabling better scripting and automation. Users can handle errors
differently based on the exit code (e.g., retry on network errors,
abort on authentication errors).

Usage:
    from gitlab_issue_sync.exit_codes import (
        EXIT_SUCCESS,
        EXIT_GENERAL_ERROR,
        EXIT_CONFIG_ERROR,
        EXIT_AUTH_ERROR,
        EXIT_API_ERROR,
        EXIT_CONFLICT,
    )

    # In CLI commands
    sys.exit(EXIT_AUTH_ERROR)

Example script using exit codes:
    #!/bin/bash
    gl-issue-sync pull
    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 4 ]; then
        echo "Network error, retrying..."
        sleep 5
        gl-issue-sync pull
    elif [ $EXIT_CODE -eq 3 ]; then
        echo "Authentication failed, check your token"
        exit 1
    fi
"""

# Exit code constants
EXIT_SUCCESS = 0  # Success
EXIT_GENERAL_ERROR = 1  # General error (validation, storage, etc.)
EXIT_CONFIG_ERROR = 2  # Configuration error (missing config, invalid format)
EXIT_AUTH_ERROR = 3  # Authentication error (invalid token, insufficient permissions)
EXIT_API_ERROR = 4  # API error (network failure, GitLab API errors)
EXIT_CONFLICT = 5  # Conflict detected (requires manual resolution)
