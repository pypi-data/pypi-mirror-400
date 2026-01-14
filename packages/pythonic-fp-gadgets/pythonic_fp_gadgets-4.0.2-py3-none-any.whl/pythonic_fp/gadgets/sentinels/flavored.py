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

"""
.. admonition:: Sentinel values labeled by different (hashable) flavors.

    When different flavors of the truth are needed.

.. note::

    Can be compared using ``==`` and ``!=``. A flavored sentinel
    value always equals itself and never equals anything else,
    especially other flavored sentinel values.

    Useful for union types where ``Sentinel[H]`` is one of the
    types making up the union.

    To ensure that reference equality is used, put the known
    sentinel value first in the comparison.

.. note::

    Threadsafe.

"""

import threading
from typing import ClassVar, final, Hashable

__all__ = ['Sentinel']


@final
class Sentinel[H: Hashable]:
    __slots__ = ('_flavor',)

    _flavors: 'dict[H, Sentinel[H]]' = {}
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __new__(cls, flavor: H) -> 'Sentinel[H]':
        if flavor not in cls._flavors:
            with cls._lock:
                if flavor not in cls._flavors:
                    cls._flavors[flavor] = super().__new__(cls)
        return cls._flavors[flavor]

    def __init__(self, flavor: H) -> None:
        """
        :param flavor: Some Hashable value of generic type ``H``.
        :returns: The ``Sentinel`` singleton instance with flavor ``flavor``.
        :rtype: ``Sentinel[H]`` where ``H`` is a subtype of Hashable.
        """
        if not hasattr(self, '_flavor'):
            self._flavor = flavor

    def __repr__(self) -> str:
        return "Sentinel('" + repr(self._flavor) + "')"

    def flavor(self) -> H:
        """
        :returns: The sentinel's flavor. A ``Hashable`` value of type ``H``.
        """
        return self._flavor
