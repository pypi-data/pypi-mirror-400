"""Security validation utilities for tgwrap."""

import os
import re
import unicodedata


class SecurityValidationError(ValueError):
    """Raised when a security validation check fails."""


class SecurityValidator:
    """Validates user inputs to prevent security vulnerabilities."""


    # Patterns for detecting potentially dangerous characters
    DANGEROUS_PATTERNS : list[str] = [
        r'[;&|`$(){}\\]',  # Command injection characters (allow [] for Terraform selectors)
        r'\$\(',  # Command substitution
        r'`',     # Backticks for command execution
        r'\.\./+',  # Path traversal attempts
    ]

    # Safe patterns for resource identifiers
    SAFE_RESOURCE_PATTERN : str = r'^[a-zA-Z0-9._/-]+$'
    SAFE_MODULE_PATTERN : str = r'^[a-zA-Z0-9._/-]+$'

    @staticmethod
    def validate_command_args(args: list[str]) -> bool:
        """Validate terragrunt arguments for safety."""
        if not args:
            return True

        for index, arg in enumerate(args):
            if not isinstance(arg, str):
                raise SecurityValidationError(
                    f"Argument at position {index} must be a string, got {type(arg).__name__}"
                )

            # Check for dangerous patterns
            for pattern in SecurityValidator.DANGEROUS_PATTERNS:
                if re.search(pattern, arg):
                    raise SecurityValidationError(
                        f"Argument '{arg}' contains forbidden characters matching pattern '{pattern}'"
                    )

            # Ensure reasonable length
            if len(arg) > 1000:
                raise SecurityValidationError(
                    f"Argument '{arg[:50]}...' exceeds maximum length of 1000 characters"
                )

        return True

    @staticmethod
    def validate_working_dir(working_dir: str | None) -> bool:
        """Validate working directory path for safety."""
        if not working_dir:
            return True

        # Resolve and normalize path
        try:
            normalized = os.path.normpath(working_dir)

            # Check for path traversal attempts
            if '..' in normalized:
                raise SecurityValidationError(
                    f"Working directory '{working_dir}' resolves to '{normalized}', which includes path traversal"
                )

            # Ensure it's not trying to access system directories
            system_dirs = ['/etc', '/bin', '/sbin', '/usr/bin', '/usr/sbin']
            if any(normalized.startswith(sys_dir) for sys_dir in system_dirs):
                raise SecurityValidationError(
                    f"Working directory '{working_dir}' resolves to '{normalized}', which targets a restricted system directory"
                )

            return True

        except (OSError, ValueError) as exc:
            raise SecurityValidationError(
                f"Working directory '{working_dir}' could not be normalized: {exc}"
            ) from exc

    @staticmethod
    def validate_resource_identifier(identifier: str) -> bool:
        """Validate resource identifier for safety."""
        if not identifier or not isinstance(identifier, str):
            raise SecurityValidationError("Resource identifier must be a non-empty string")

        # Check length
        if len(identifier) > 255:
            raise SecurityValidationError("Resource identifier exceeds maximum length of 255 characters")

        # Check pattern
        if re.match(SecurityValidator.SAFE_RESOURCE_PATTERN, identifier) is None:
            raise SecurityValidationError(
                f"Resource identifier '{identifier}' contains unsupported characters"
            )

        return True

    @staticmethod
    def validate_module_name(module_name: str | None) -> bool:
        """Validate module name for safety."""
        if not module_name:
            return True

        if not isinstance(module_name, str):
            raise SecurityValidationError("Module name must be a string")

        # Check length
        if len(module_name) > 255:
            raise SecurityValidationError("Module name exceeds maximum length of 255 characters")

        # Check for dangerous patterns
        for pattern in SecurityValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, module_name):
                raise SecurityValidationError(
                    f"Module name '{module_name}' contains forbidden characters matching pattern '{pattern}'"
                )

        # Check pattern
        if re.match(SecurityValidator.SAFE_MODULE_PATTERN, module_name) is None:
            raise SecurityValidationError(
                f"Module name '{module_name}' contains unsupported characters"
            )

        return True

    @staticmethod
    def sanitize_path_string(path: str) -> str:
        """Sanitize a path string by removing problematic Unicode characters.

        This handles various invisible and control characters that can cause issues:
        - Non-breaking spaces (\\xa0, U+00A0)
        - Zero-width spaces (U+200B)
        - Other Unicode whitespace variants
        - Control characters

        Args:
            path: The path string to sanitize

        Returns:
            Sanitized path string with problematic characters removed
        """
        if not path:
            return path

        # Normalize Unicode to composed form (NFC)
        # This handles cases where characters might be decomposed
        normalized = unicodedata.normalize('NFC', path)

        # Remove or replace problematic whitespace characters
        # \xa0 = non-breaking space
        # \u200b = zero-width space
        # \u200c = zero-width non-joiner
        # \u200d = zero-width joiner
        # \ufeff = zero-width no-break space (BOM)
        problematic_chars = {
            '\xa0': '',      # non-breaking space
            '\u200b': '',    # zero-width space
            '\u200c': '',    # zero-width non-joiner
            '\u200d': '',    # zero-width joiner
            '\ufeff': '',    # zero-width no-break space
            '\u2060': '',    # word joiner
        }

        for char, replacement in problematic_chars.items():
            normalized = normalized.replace(char, replacement)

        # Strip leading/trailing whitespace (including tabs, newlines, etc.)
        normalized = normalized.strip()

        # Remove any remaining control characters (except newlines/tabs in middle of string)
        # Control characters are in categories Cc (control) and Cf (format)
        normalized = ''.join(
            c for c in normalized
            if not unicodedata.category(c).startswith('C') or c in ('\n', '\t')
        )

        return normalized

    @staticmethod
    def sanitize_for_logging(text: str) -> str:
        """Sanitize text for safe logging (remove potentially sensitive info)."""
        if not text:
            return text

        # Remove potential secrets/tokens
        sanitized = re.sub(r'(token|password|key|secret)=[^\s&]+', r'\1=***', text, flags=re.IGNORECASE)

        # Limit length for logging
        if len(sanitized) > 500:
            sanitized = sanitized[:497] + "..."

        return sanitized
