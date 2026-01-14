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

from pythonic_fp.gadgets import first_common_ancestor as fca


class A1():
    pass

class A1B1(A1):
    pass

class A1B1C1(A1B1):
    pass

class A1B1C2(A1B1):
    pass

class A1B2(A1):
    pass

class A1B2C1(A1B2):
    pass

class A1B2C2(A1B2):
    pass

class A2():
    pass

class A2B1(A2):
    pass

class A2B1C1(A2B1):
    pass

class A2B1C2(A2B1):
    pass

class A2B2(A2):
    pass

class A2B2C1(A2B2):
    pass

class A2B2C1D1(A2B2C1):
    pass

class A2B2C1D2(A2B2C1):
    pass

class A2B2C2(A2B2):
    pass

class A2B2C2D1(A2B2C2):
    pass

class A2B2C2D2(A2B2C2):
    pass

class TestLatestCommonAncestor:
    """Functionality testing"""

    def test_self(self) -> None:
        assert fca(A1, A1) is A1
        assert fca(A1B1, A1B1) is A1B1
        assert fca(A1B1C1, A1B1C1) is A1B1C1
        assert fca(int, int) is int
        assert fca(bool, bool) is bool

    def test_linear_descent(self) -> None:
        assert fca(A1, A1B1) is A1
        assert fca(A1B1, A1) is A1
        assert fca(A1B1C1, A1) is A1
        assert fca(A1, A1B1C1) is A1
        assert fca(A1B1C1, A1B1) is A1B1
        assert fca(A1B1, A1B1C1) is A1B1
        assert fca(A1B1C1, A1B1) is A1B1
        assert fca(A1B1, A1B1C1) is A1B1
        assert fca(A1B1C1, A1) is A1
        assert fca(A1, A1B1C1) is A1
        assert fca(A2B2, A2B2C2D2) is A2B2
        assert fca(A2B2C2D2, A2B2) is A2B2
        assert fca(int, object) is object
        assert fca(object, int) is object
        assert fca(int, bool) is int
        assert fca(bool, int) is int

    def test_nonliear_descent(self) -> None:
        assert fca(A1B1, A1B2) is A1
        assert fca(A1B2, A1B1) is A1
        assert fca(A1B2C1, A1B2C2) is A1B2
        assert fca(A1B2C2, A1B2C1) is A1B2
        assert fca(A1B1C1, A1B2C2) is A1
        assert fca(A1B2C2, A1B1C1) is A1
        assert fca(A1B1C1, A1B2C1) is A1
        assert fca(A1B2C1, A1B1C1) is A1
        assert fca(A2B2C1, A2B2C2D2) is A2B2
        assert fca(A2B2C2D2, A2B2C1) is A2B2
        assert fca(A2B1C1, A2B2C2D2) is A2
        assert fca(A2B2C2D2, A2B1C1) is A2
        assert fca(A1, A2) is object
        assert fca(A2B2C2D2, A1B2C2) is object
        assert fca(A1B2C1, A2B1C1) is object
