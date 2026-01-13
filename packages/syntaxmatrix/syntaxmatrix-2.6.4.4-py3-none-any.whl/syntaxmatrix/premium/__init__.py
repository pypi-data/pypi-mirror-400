"""Premium support.

This package contains runtime plumbing for premium features (entitlements +
plugin loading). The actual premium implementations should live in separate,
private distributions.
"""

from .gate import FeatureGate

__all__ = ["FeatureGate"]
