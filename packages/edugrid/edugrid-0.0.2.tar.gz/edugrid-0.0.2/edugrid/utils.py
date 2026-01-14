from typing import Any
import numpy as np


class ArrayWrapper:
    def __init__(self, array: np.ndarray, val_set=None, val_setitem=None) -> None:
        self._array = array
        self._val_set = val_set
        self._val_setitem = val_setitem

    def __array__(
        self, dtype: str | np.dtype | None = None, copy: bool | None = None
    ) -> np.ndarray:
        if copy is False:
            raise ValueError("`copy=False` isn't supported. A copy is always created.")
        return self._array.astype(dtype=dtype, copy=True)

    def get(self, *key) -> np.ndarray:
        if not key:
            return self._array.copy()
        else:
            if len(key) == 1:
                key = key[0]
            return self.__getitem__(key)

    def set(self, value) -> None:
        value = np.asarray(value)
        if self._val_set is not None:
            self._val_set(value)
        np.copyto(self._array, value)

    def __getitem__(self, key) -> None:
        return self._array[key].copy()

    def __setitem__(self, key, value) -> None:
        value = np.asarray(value)
        if self._val_setitem is not None:
            self._val_setitem(key, value)
        self._array[key] = value

    def __getattr__(self, name) -> Any:
        return getattr(self._array, name)

    def __str__(self) -> str:
        return self._array.__str__()

    def __repr__(self):
        return self._array.__repr__()


class ArrayDescriptor:
    def __set_name__(self, owner, name) -> None:
        self._public_name = name
        self._private_name = "_" + name + "_wrapper"

    def __get__(self, obj, objtype=None) -> np.ndarray:
        return getattr(obj, self._private_name)

    def __set__(self, obj, value) -> None:
        wrapper = getattr(obj, self._private_name)
        wrapper.set(value)
        # setattr(obj, self._private_name, value)
