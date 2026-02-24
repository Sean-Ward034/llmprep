"""Open-core licensing extension points."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class LicenseContext:
    provider: str = "noop"
    pro_enabled: bool = False
    metadata: dict[str, Any] | None = None


class LicenseProvider:
    def check_feature(self, feature_name: str, ctx: LicenseContext) -> bool:
        raise NotImplementedError


class NoopLicenseProvider(LicenseProvider):
    def check_feature(self, feature_name: str, ctx: LicenseContext) -> bool:
        return not ctx.pro_enabled or ctx.provider == "noop"


def get_license_provider(name: str) -> LicenseProvider:
    if name == "noop":
        return NoopLicenseProvider()
    return NoopLicenseProvider()

