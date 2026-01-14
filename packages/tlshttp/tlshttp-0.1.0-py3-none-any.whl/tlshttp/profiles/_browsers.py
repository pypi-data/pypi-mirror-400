"""Browser fingerprint profiles for tls-client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# Supported browser profile identifiers
# These match the tls-client Go library identifiers
ProfileIdentifier = Literal[
    # Chrome
    "chrome_103",
    "chrome_104",
    "chrome_105",
    "chrome_106",
    "chrome_107",
    "chrome_108",
    "chrome_109",
    "chrome_110",
    "chrome_111",
    "chrome_112",
    "chrome_116_PSK",
    "chrome_116_PSK_PQ",
    "chrome_117",
    "chrome_120",
    "chrome_124",
    "chrome_130_PSK",
    "chrome_131",
    "chrome_131_PSK",
    "chrome_133",
    "chrome_133_PSK",
    # Firefox
    "firefox_102",
    "firefox_104",
    "firefox_105",
    "firefox_106",
    "firefox_108",
    "firefox_110",
    "firefox_117",
    "firefox_120",
    "firefox_123",
    "firefox_132",
    "firefox_133",
    # Safari
    "safari_15_6_1",
    "safari_16_0",
    # Safari iOS
    "safari_ios_15_5",
    "safari_ios_15_6",
    "safari_ios_16_0",
    "safari_ios_17_0",
    "safari_ios_18_0",
    "safari_ios_18_5",
    # Safari iPad
    "safari_ipad_15_6",
    # Opera
    "opera_89",
    "opera_90",
    "opera_91",
    # OkHttp (Android)
    "okhttp4_android_7",
    "okhttp4_android_8",
    "okhttp4_android_9",
    "okhttp4_android_10",
    "okhttp4_android_11",
    "okhttp4_android_12",
    "okhttp4_android_13",
    # Custom clients
    "zalando_ios_mobile",
    "zalando_android_mobile",
    "nike_ios_mobile",
    "nike_android_mobile",
    "mms_ios",
    "mms_ios_1",
    "mms_ios_2",
    "mms_ios_3",
    "mesh_ios",
    "mesh_ios_1",
    "mesh_ios_2",
    "mesh_android",
    "mesh_android_1",
    "mesh_android_2",
    "confirmed_ios",
    "confirmed_android",
]


@dataclass(frozen=True)
class Profile:
    """Browser profile for TLS fingerprinting.

    Attributes:
        identifier: The tls-client profile identifier.
        description: Human-readable description.
    """

    identifier: str
    description: str = ""

    def __str__(self) -> str:
        return self.identifier


# Pre-defined profile constants for convenience
class Chrome:
    """Chrome browser profiles."""

    V103 = Profile("chrome_103", "Chrome 103")
    V104 = Profile("chrome_104", "Chrome 104")
    V105 = Profile("chrome_105", "Chrome 105")
    V106 = Profile("chrome_106", "Chrome 106")
    V107 = Profile("chrome_107", "Chrome 107")
    V108 = Profile("chrome_108", "Chrome 108")
    V109 = Profile("chrome_109", "Chrome 109")
    V110 = Profile("chrome_110", "Chrome 110")
    V111 = Profile("chrome_111", "Chrome 111")
    V112 = Profile("chrome_112", "Chrome 112")
    V116_PSK = Profile("chrome_116_PSK", "Chrome 116 with PSK")
    V117 = Profile("chrome_117", "Chrome 117")
    V120 = Profile("chrome_120", "Chrome 120")
    V124 = Profile("chrome_124", "Chrome 124")
    V130_PSK = Profile("chrome_130_PSK", "Chrome 130 with PSK")
    V131 = Profile("chrome_131", "Chrome 131")
    V131_PSK = Profile("chrome_131_PSK", "Chrome 131 with PSK")
    V133 = Profile("chrome_133", "Chrome 133")
    V133_PSK = Profile("chrome_133_PSK", "Chrome 133 with PSK")

    # Aliases
    LATEST = V133
    DEFAULT = V120


class Firefox:
    """Firefox browser profiles."""

    V102 = Profile("firefox_102", "Firefox 102")
    V104 = Profile("firefox_104", "Firefox 104")
    V105 = Profile("firefox_105", "Firefox 105")
    V106 = Profile("firefox_106", "Firefox 106")
    V108 = Profile("firefox_108", "Firefox 108")
    V110 = Profile("firefox_110", "Firefox 110")
    V117 = Profile("firefox_117", "Firefox 117")
    V120 = Profile("firefox_120", "Firefox 120")
    V123 = Profile("firefox_123", "Firefox 123")
    V132 = Profile("firefox_132", "Firefox 132")
    V133 = Profile("firefox_133", "Firefox 133")

    # Aliases
    LATEST = V133
    DEFAULT = V120


class Safari:
    """Safari browser profiles."""

    V15_6_1 = Profile("safari_15_6_1", "Safari 15.6.1")
    V16_0 = Profile("safari_16_0", "Safari 16.0")

    # iOS Safari
    IOS_15_5 = Profile("safari_ios_15_5", "Safari iOS 15.5")
    IOS_15_6 = Profile("safari_ios_15_6", "Safari iOS 15.6")
    IOS_16_0 = Profile("safari_ios_16_0", "Safari iOS 16.0")
    IOS_17_0 = Profile("safari_ios_17_0", "Safari iOS 17.0")
    IOS_18_0 = Profile("safari_ios_18_0", "Safari iOS 18.0")
    IOS_18_5 = Profile("safari_ios_18_5", "Safari iOS 18.5")

    # iPad Safari
    IPAD_15_6 = Profile("safari_ipad_15_6", "Safari iPad 15.6")

    # Aliases
    LATEST = V16_0
    DEFAULT = V16_0
    IOS_LATEST = IOS_18_5


class Opera:
    """Opera browser profiles."""

    V89 = Profile("opera_89", "Opera 89")
    V90 = Profile("opera_90", "Opera 90")
    V91 = Profile("opera_91", "Opera 91")

    # Aliases
    LATEST = V91
    DEFAULT = V90


class Android:
    """Android OkHttp profiles."""

    V7 = Profile("okhttp4_android_7", "OkHttp4 Android 7")
    V8 = Profile("okhttp4_android_8", "OkHttp4 Android 8")
    V9 = Profile("okhttp4_android_9", "OkHttp4 Android 9")
    V10 = Profile("okhttp4_android_10", "OkHttp4 Android 10")
    V11 = Profile("okhttp4_android_11", "OkHttp4 Android 11")
    V12 = Profile("okhttp4_android_12", "OkHttp4 Android 12")
    V13 = Profile("okhttp4_android_13", "OkHttp4 Android 13")

    # Aliases
    LATEST = V13
    DEFAULT = V13


# Default profile
DEFAULT_PROFILE = Chrome.DEFAULT


def get_profile(identifier: str | Profile | None) -> str | None:
    """Get the profile identifier string.

    Args:
        identifier: Profile identifier, Profile object, or None.

    Returns:
        Profile identifier string or None.
    """
    if identifier is None:
        return None
    if isinstance(identifier, Profile):
        return identifier.identifier
    return identifier


# List of all available profiles for iteration
ALL_PROFILES: list[str] = [
    # Chrome
    "chrome_103", "chrome_104", "chrome_105", "chrome_106", "chrome_107",
    "chrome_108", "chrome_109", "chrome_110", "chrome_111", "chrome_112",
    "chrome_116_PSK", "chrome_116_PSK_PQ", "chrome_117", "chrome_120",
    "chrome_124", "chrome_130_PSK", "chrome_131", "chrome_131_PSK",
    "chrome_133", "chrome_133_PSK",
    # Firefox
    "firefox_102", "firefox_104", "firefox_105", "firefox_106", "firefox_108",
    "firefox_110", "firefox_117", "firefox_120", "firefox_123", "firefox_132",
    "firefox_133",
    # Safari
    "safari_15_6_1", "safari_16_0",
    "safari_ios_15_5", "safari_ios_15_6", "safari_ios_16_0", "safari_ios_17_0",
    "safari_ios_18_0", "safari_ios_18_5", "safari_ipad_15_6",
    # Opera
    "opera_89", "opera_90", "opera_91",
    # Android
    "okhttp4_android_7", "okhttp4_android_8", "okhttp4_android_9",
    "okhttp4_android_10", "okhttp4_android_11", "okhttp4_android_12",
    "okhttp4_android_13",
]
