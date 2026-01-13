"""Infrastructure Interface"""

from contextvars import ContextVar
from typing import Callable, Generic, Optional, TypeVar

TypeCredentialProvider = TypeVar("TypeCredentialProvider")
CredentialGetter = Callable[[], TypeCredentialProvider]


class CredentialProvider(Generic[TypeCredentialProvider]):
    """Thread-safe and async-safe credential provider using ContextVar internally.

    Automatically provides thread/async isolation without exposing ContextVar to users.

    Usage:
        >>> provider: CredentialProvider[MyCredentials] = CredentialProvider(get_default_credentials)
        >>> # Setting credentials (automatically thread-safe via ContextVar)
        >>> provider.set_loader_credentials(lambda: new_credentials)
        >>> # Getting credentials (automatically uses current context)
        >>> credentials = provider.get_credentials()
    """

    def __init__(self, get_credentials: CredentialGetter):
        """Initialize with default credentials getter.

        Args:
            get_credentials: Callable that returns default credentials
        """
        self._default_getter: CredentialGetter = get_credentials
        # ContextVar for automatic thread/async-safe credential storage
        self._context_var: ContextVar[Optional[CredentialGetter]] = ContextVar(
            f"credentials_getter_{id(self)}", default=None
        )

    def set_loader_credentials(self, fn: CredentialGetter) -> None:
        """Set credentials from a callable (thread-safe, async-safe).

        Credentials are automatically isolated per thread/async task using ContextVar.

        Args:
            fn: Callable that returns credentials
        """
        self._context_var.set(fn)

    def get_credentials(self) -> TypeCredentialProvider:
        """Get credentials from current context or default.

        Resolution order:
        1. Context-scoped credentials (if set in current thread/task)
        2. Default credentials (from constructor)

        Returns:
            Credentials for current execution context
        """
        # Try context-scoped getter first (thread/async-safe)
        context_getter = self._context_var.get()
        if context_getter is not None:
            return context_getter()

        # Fallback to default getter
        return self._default_getter()
