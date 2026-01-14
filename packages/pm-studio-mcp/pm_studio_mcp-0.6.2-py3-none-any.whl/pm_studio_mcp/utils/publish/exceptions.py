"""Exception classes for GitHub Pages publishing."""


class PublishError(Exception):
    """Base exception for publishing errors."""
    pass


class GitOperationError(PublishError):
    """Raised when a Git operation fails."""
    pass


class FileProcessingError(PublishError):
    """Raised when file processing fails."""
    pass


class ValidationError(PublishError):
    """Raised when validation fails."""
    pass


class UncommittedChangesError(PublishError):
    """Raised when there are uncommitted changes in the repository."""
    pass
