import warnings

from .our_url import OurUrl  # noqa: backward compatibility

warnings.warn(
    "Deprecated: Please use 'from url_remote.our_url import OurUrl' instead of "
    "'from url_remote.url_circlez import OurUrl'",
    DeprecationWarning,
)
