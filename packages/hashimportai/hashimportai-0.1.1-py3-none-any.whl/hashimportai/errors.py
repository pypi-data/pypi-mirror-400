class HashImportError(Exception):
    """
    Base class for all HashImport SDK errors.
    """
    pass


# -------------------------
# Auth / Access
# -------------------------

class AuthenticationError(HashImportError):
    """
    Raised when app_key or workflow access is invalid.
    """
    pass


class AuthorizationError(HashImportError):
    """
    Raised when the app is authenticated but not allowed
    to run this workflow or action.
    """
    pass


# -------------------------
# Validation
# -------------------------

class ValidationError(HashImportError):
    """
    Raised when required inputs are missing or invalid.
    """
    def __init__(self, message: str, fields=None):
        super().__init__(message)
        self.fields = fields or []


class ManifestError(HashImportError):
    """
    Raised when the workflow manifest is malformed
    or incompatible with the SDK version.
    """
    pass


# -------------------------
# Execution
# -------------------------

class WorkflowExecutionError(HashImportError):
    """
    Raised when a workflow step fails during execution.
    """
    def __init__(self, step: str, message: str, details=None):
        super().__init__(f"[{step}] {message}")
        self.step = step
        self.details = details


class ActionExecutionError(WorkflowExecutionError):
    """
    Raised when an individual action fails.
    """
    pass


class LinkResolutionError(WorkflowExecutionError):
    """
    Raised when is_link inputs cannot be resolved
    from previous step outputs.
    """
    pass


# -------------------------
# Network / Runtime
# -------------------------

class NetworkError(HashImportError):
    """
    Raised for connectivity, timeout, or transport issues.
    """
    pass


class TimeoutError(NetworkError):
    """
    Raised when a request times out.
    """
    pass


class RetryableError(HashImportError):
    """
    Marker exception for safe retries.
    """
    pass
