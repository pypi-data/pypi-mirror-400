__version__ = '1.0.0'


def __getattr__(name):
    """Lazy import of permission classes to avoid Django AppRegistryNotReady errors."""
    if name in (
        'EdcContractPermission',
        'EdcContractPermissionV3',
        'EdcContractPermissionV3WithFallback',
        'EdcContractPermissionV3WithAutoNegotiation',
        'EdcContractPermissionV3PolicyDiscovery',
    ):
        from djangoldp_edc.permissions import (
            EdcContractPermission,
            EdcContractPermissionV3,
            EdcContractPermissionV3WithFallback,
            EdcContractPermissionV3WithAutoNegotiation,
            EdcContractPermissionV3PolicyDiscovery,
        )
        return locals()[name]
    elif name == 'EdcNegotiationMiddleware':
        from djangoldp_edc.middleware import EdcNegotiationMiddleware
        return EdcNegotiationMiddleware
    elif name == 'NegotiationRequired':
        from djangoldp_edc.exceptions import NegotiationRequired
        return NegotiationRequired
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    'EdcContractPermission',
    'EdcContractPermissionV3',
    'EdcContractPermissionV3WithFallback',
    'EdcContractPermissionV3WithAutoNegotiation',
    'EdcContractPermissionV3PolicyDiscovery',
    'EdcNegotiationMiddleware',
    'NegotiationRequired',
]
