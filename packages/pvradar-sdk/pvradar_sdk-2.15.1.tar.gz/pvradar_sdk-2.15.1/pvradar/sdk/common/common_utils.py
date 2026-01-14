import re
from functools import cache
import importlib.util
from geopy.geocoders import Nominatim


@cache
def check_package_installed(package_name: str) -> bool:
    return importlib.util.find_spec(package_name) is not None


@cache
def get_nominatim_client() -> Nominatim:
    return Nominatim(user_agent='pvradar-sdk')


def compare_versions(a: str, b: str) -> int:
    """compare semver version strings, i.e. 2.10.3 vs 2.9.3, supports versions like 2.14.0.dev1"""
    pa = [int(x) for x in re.findall(r'\d+', a)]
    pb = [int(x) for x in re.findall(r'\d+', b)]

    # limit pa and pb to just 3 elements (pre-release versions are not considered)
    pa = pa[:3]
    pb = pb[:3]

    # Remove trailing zeros
    while pa and pa[-1] == 0:
        pa.pop()
    while pb and pb[-1] == 0:
        pb.pop()

    for x, y in zip(pa, pb):
        if x < y:
            return -1
        if x > y:
            return 1

    return (len(pa) > len(pb)) - (len(pa) < len(pb))


def pick_dict_keys(d: dict, keys: list[str]) -> dict:
    return {k: d[k] for k in keys if k in d}
