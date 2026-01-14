from typing import Optional
from pint import Quantity


class QuantityWithAttrs(Quantity):
    def __new__(cls, value, units=None, attrs=Optional[dict]):
        obj = super().__new__(cls, value, units)
        setattr(obj, '_attrs', attrs)
        return obj

    @property
    def attrs(self):
        return self._attrs

    @attrs.setter
    def attrs(self, value):
        self._attrs = dict(value)

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self._attrs = getattr(obj, '_attrs', {}).copy()
