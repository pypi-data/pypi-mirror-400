"""OptionXRay package exports."""

from importlib.metadata import PackageNotFoundError, version

from .bs import price_bs
from .greeks import greeks_bs
from .instruments import Market, Option
from .iv import implied_vol_bs

try:
    __version__ = version("optionxray")
except PackageNotFoundError:
    __version__ = "0.1.0"

__all__ = [
    "Market",
    "Option",
    "XRay",
    "XRayResult",
    "__version__",
    "price_bs",
    "implied_vol_bs",
    "greeks_bs",
]


def __getattr__(name: str):
    if name in {"XRay", "XRayResult"}:
        from .xray import XRay, XRayResult

        return {"XRay": XRay, "XRayResult": XRayResult}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
