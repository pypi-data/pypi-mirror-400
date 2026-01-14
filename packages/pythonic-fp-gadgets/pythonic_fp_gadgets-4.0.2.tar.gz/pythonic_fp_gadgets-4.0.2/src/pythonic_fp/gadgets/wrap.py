# Copyright 2023-2025 Geoffrey R. Scheller
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__all__ = ['Wrap', 'HWrap']

from collections.abc import Callable, Iterator, Hashable


class Wrap[T]():
    """Immutablely wrap exactly one value of a given type.

    .. tip::

        ``Wrap`` objects can be used in Python match statements.

    """
    __slots__ = ('_item',)
    __match_args__ = ('_item',)

    def __init__(self, item: T) -> None:
        self._item = item

    def __bool__(self) -> bool:
        return bool(self._item)

    def __iter__(self) -> Iterator[T]:
        if self:
            yield self._item

    def __repr__(self) -> str:
        return 'Wrap(' + repr(self._item) + ')'

    def __eq__(self, other: object) -> bool:
        """
        Efficiently compare to another object.

        :param other: The object to be compared with,
        :returns: ``True`` if ``other`` is of type Wrap and wraps
                  an object which compares as equal to the wrapped
                  object, otherwise ``False``.
        """
        if not isinstance(other, type(self)):
            return False

        if self._item is other._item:
            return True
        return self._item == other._item

    def map[U](self, f: Callable[[T], U]) -> 'Wrap[U]':
        """Map function ``f`` over contents.

        :param f: Mapping function.
        :returns: A new instance.

        """
        return Wrap(f(self._item))

    def bind[U](self, f: Callable[[T], 'Wrap[U]']) -> 'Wrap[U]':
        """Flatmap the ``Wrap`` with function ``f``.

        :param f: Binding function.
        :returns: A new instance.

        """
        return f(self._item)


class HWrap[T: Hashable](Hashable):
    """Immutablely wrap exactly one hashable value of a given type.

    .. tip::

        ``HWrap`` objects can be used in Python match statements.

    .. tip::

        ``HWrap`` objects are hashable..

    """
    __slots__ = ('_item', '_hash')
    __match_args__ = ('_item',)

    def __init__(self, item: T) -> None:
        self._item, self._hash = item, hash(item)

    def __hash__(self) -> int:
        return self._hash

    def __bool__(self) -> bool:
        return bool(self._item)

    def __iter__(self) -> Iterator[T]:
        if self:
            yield self._item

    def __repr__(self) -> str:
        return 'Wrap(' + repr(self._item) + ')'

    def __eq__(self, other: object) -> bool:
        """
        Efficiently compare to another object.

        :param other: The object to be compared with,
        :returns: ``True`` if ``other`` is of type HWrap and wraps
                  an object which compares as equal to the wrapped
                  object, otherwise ``False``.
        """
        if not isinstance(other, type(self)):
            return False

        if self._hash != other._hash:
            return False
        if self._item is other._item:
            return True
        return self._item == other._item

    def map[U](self, f: Callable[[T], U]) -> 'HWrap[U]':
        """Map function ``f`` over contents.

        :param f: Mapping function.
        :returns: A new instance.

        """
        return HWrap(f(self._item))

    def bind[U](self, f: Callable[[T], 'HWrap[U]']) -> 'HWrap[U]':
        """Flatmap the ``Wrap`` with function ``f``.

        :param f: Binding function.
        :returns: A new instance.

        """
        return f(self._item)
