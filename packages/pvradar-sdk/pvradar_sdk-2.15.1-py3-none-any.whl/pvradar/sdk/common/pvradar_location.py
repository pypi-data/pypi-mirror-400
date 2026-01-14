from functools import lru_cache
import re
from typing import Any, Optional, Protocol, cast, override, overload
import warnings
import pandas as pd
from pvlib.location import Location as PvlibLocation
from timezonefinder import TimezoneFinder
import geopy.location
from .singleton import Singleton
from .common_utils import check_package_installed, get_nominatim_client
from ..display.map import display_map


@lru_cache(maxsize=128)
def get_country_tuple_by_coordinates(latitude: float, longitude: float) -> tuple[str, str] | None:
    """
    Uses the cached Nominatim client to perform a reverse geocoding lookup on the
    given latitude and longitude. If a country is found, returns its English name
    and the uppercase ISO 3166-1 alpha-2 country code.

    Returns:
        tuple[str, str] | None: A tuple containing the country name and its
        ISO alpha-2 code (e.g., ("Germany", "DE")). Returns None if the
        country could not be determined.
    """
    geolocator = get_nominatim_client()
    location = geolocator.reverse((latitude, longitude), language='en', exactly_one=True)  # pyright: ignore[reportArgumentType]
    if location and 'country' in location.raw['address']:  # pyright: ignore[reportAttributeAccessIssue]
        country_name = location.raw['address']['country']  # pyright: ignore[reportAttributeAccessIssue]
        alpha2 = str(location.raw['address']['country_code']).upper()  # pyright: ignore[reportAttributeAccessIssue]
        return country_name, alpha2


def get_country_by_coordinates(latitude: float, longitude: float) -> str | None:
    maybe_tuple = get_country_tuple_by_coordinates(latitude, longitude)
    if maybe_tuple is None:
        return None
    return maybe_tuple[0]


def get_alpha2_by_coordinates(latitude: float, longitude: float) -> str | None:
    maybe_tuple = get_country_tuple_by_coordinates(latitude, longitude)
    if maybe_tuple is None:
        return None
    return maybe_tuple[1]


@lru_cache(maxsize=128)
def get_kb_climate_zone_by_coordinates(latitude: float, longitude: float) -> str | None:
    if not check_package_installed('kgcpy'):
        raise ImportError("kgcpy package is not installed. Install it with: pip install 'pvradar-sdk[kgcpy]'")

    from kgcpy import lookupCZ

    return lookupCZ(latitude, longitude)


@lru_cache(maxsize=128)
def get_coordinates_by_address(address: str) -> tuple[float, float] | None:
    geolocator = get_nominatim_client()
    location = geolocator.geocode(address, language='en', exactly_one=True, timeout=10)  # pyright: ignore[reportArgumentType]
    if location:
        location = cast(geopy.location.Location, location)
        return (location.latitude, location.longitude)


class TZFinder(TimezoneFinder, Singleton):
    pass


def get_tz_offset(tz) -> float:
    reference_date = pd.Timestamp('2024-01-01T00:00:00')
    zoneinfo = reference_date.tz_localize(tz).tzinfo
    if zoneinfo is None:
        raise ValueError(f'Could not find zoneinfo for TZ {tz}')
    offset = zoneinfo.utcoffset(reference_date)
    if offset is None:
        raise ValueError(f'Failed getting UTC offset for TZ {tz}')
    return offset.total_seconds() / 3600


def get_int_tz_offset(tz) -> int:
    tz_offset = get_tz_offset(tz)
    if int(tz_offset) != tz_offset:
        warnings.warn(f'tz_offset seems to be a float {tz_offset}. Fractional part will be ignored.')
    return int(tz_offset)


def _maybe_translate_tz(tz):
    if isinstance(tz, str):
        # avoid ambiguity of the same TZ
        if tz == 'UTC' or tz == 'Etc/UTC':
            return 'Etc/GMT'
        match = re.match(r'^UTC([+-])(\d\d):', tz)
        if match:
            sign = match.group(1)
            hours = int(match.group(2))
            if hours == 0:
                tz = 'Etc/GMT'
            elif sign == '+':
                tz = f'Etc/GMT-{hours}'
            else:
                tz = f'Etc/GMT+{hours}'
    return tz


class LocationWithCoordinates(Protocol):
    latitude: float
    longitude: float
    tz: str | None


class PvradarLocationReprMixin:
    @override
    def __str__(self):
        self = cast(LocationWithCoordinates, self)
        return f'{self.__class__.__name__}({self.latitude}, {self.longitude}, tz="{self.tz}")'

    @override
    def __repr__(self):
        return self.__str__()

    @property
    def country(self) -> str:
        self = cast(LocationWithCoordinates, self)
        result = get_country_by_coordinates(self.latitude, self.longitude)
        if result is None:
            raise LookupError(f'Could not determine country for ({self.latitude}, {self.longitude})')
        return result

    @property
    def alpha2(self) -> str:
        self = cast(LocationWithCoordinates, self)
        result = get_alpha2_by_coordinates(self.latitude, self.longitude)
        if result is None:
            raise LookupError(f'Could not determine country for ({self.latitude}, {self.longitude})')
        return result

    @property
    def kg_climate_zone(self) -> str | None:
        self = cast(LocationWithCoordinates, self)
        return get_kb_climate_zone_by_coordinates(self.latitude, self.longitude)

    def display_map(
        self,
        figsize: Optional[tuple[Any, Any]] = None,
    ):
        self = cast(LocationWithCoordinates, self)
        display_map(
            center=(self.latitude, self.longitude),
            center_tooltip=f'{self.latitude}, {self.longitude}',
            figsize=figsize,
        )


if hasattr(PvlibLocation, 'tz') and isinstance(getattr(PvlibLocation, 'tz'), property):
    # implementation for pvlib >= 0.12.0
    class PvradarLocation(PvlibLocation, PvradarLocationReprMixin):  # pyright: ignore [reportRedeclaration]
        @overload
        def __init__(self, latitude: float, longitude: float, *, tz=None, altitude=None, name=None) -> None: ...

        @overload
        def __init__(self, name: str) -> None: ...

        def __init__(self, latitude: float | str, longitude: float | None = None, *, tz=None, altitude=None, name=None):  # type: ignore
            if isinstance(latitude, str) and longitude is None:
                coordinates = get_coordinates_by_address(latitude)
                if coordinates is None:
                    raise LookupError(f'Could not determine coordinates for address "{latitude}"')
                latitude, longitude = coordinates
            if not isinstance(latitude, (float, int)) or not isinstance(longitude, (float, int)):
                raise ValueError('Either provide (latitude: float, longitude: float) or (name: str)')
            tz_offset = 0
            if tz is None:
                detected_tz = TZFinder().timezone_at(lng=longitude, lat=latitude)
                if detected_tz is None:
                    raise ValueError(f'Could not determine timezone for ({latitude}, {longitude})')
                tz_offset = get_int_tz_offset(detected_tz)
            else:
                tz = _maybe_translate_tz(tz)

            super().__init__(
                latitude,
                longitude,
                tz=tz or tz_offset,  # pyright: ignore [reportArgumentType]
                altitude=altitude,
                name=name,
            )

        @property
        @override
        def tz(self):
            return super().tz

        @tz.setter
        def tz(self, tz_):
            tz_ = _maybe_translate_tz(tz_)
            PvlibLocation.tz.fset(self, tz_)  # pyright: ignore
else:
    # implementation for pvlib <= 0.11.2
    class PvradarLocation(PvlibLocation, PvradarLocationReprMixin):  # pyright: ignore [reportRedeclaration]
        @overload
        def __init__(self, latitude: float, longitude: float, *, tz=None, altitude=None, name=None) -> None: ...

        @overload
        def __init__(self, name: str) -> None: ...

        def __init__(self, latitude: float | str, longitude: float | None = None, *, tz=None, altitude=None, name=None):  # type: ignore
            if isinstance(latitude, str) and longitude is None:
                coordinates = get_coordinates_by_address(latitude)
                if coordinates is None:
                    raise LookupError(f'Could not determine coordinates for address "{latitude}"')
                latitude, longitude = coordinates
            if not isinstance(latitude, (float, int)) or not isinstance(longitude, (float, int)):
                raise ValueError('Either provide (latitude: float, longitude: float) or (name: str)')
            if tz is None:
                tz = TZFinder().timezone_at(lng=longitude, lat=latitude)
                if tz is None:
                    raise ValueError(f'Could not determine timezone for ({latitude}, {longitude})')
                hour_offset = get_int_tz_offset(tz)
                tz = f'UTC{hour_offset:+03.0f}:00'
            tz = _maybe_translate_tz(tz)

            # here we can't pass tz directly, because UTC+02:00 format was not supported
            super().__init__(latitude, longitude, tz='Etc/GMT', altitude=altitude, name=name)
            self.tz = tz
