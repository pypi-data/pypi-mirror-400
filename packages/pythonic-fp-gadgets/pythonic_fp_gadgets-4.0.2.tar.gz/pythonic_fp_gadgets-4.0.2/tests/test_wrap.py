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

from pythonic_fp.gadgets.wrap import Wrap


class TestGadgetWrapBuiltins:
    def test_wrap_simple(self) -> None:
        w0 = Wrap(0)
        w1 = Wrap(1)
        x1 = Wrap(1)

        assert w0 != w1
        assert w1 == x1
        assert w1 is w1
        assert w1 is not x1

    def test_map(self) -> None:
        def cat(s: str) -> str:
            return s + s

        wa = Wrap('a')
        waa = Wrap('aa')
        waaaa = Wrap('aaaa')

        xaa = wa.map(cat)
        xaaaa = xaa.map(cat)

        assert xaa == waa
        assert xaa != waaaa
        assert xaaaa == waaaa
        assert waaaa == xaaaa

    def test_bind(self) -> None:
        type LS = list[str]
        type WLS = Wrap[LS]
        type LI = list[int]
        type WLI = Wrap[LI]

        def cnt(ls: LS) -> WLI:
            li: LI = []
            for s in ls:
                li.append(len(s))
            return Wrap(li)

        hw: LS = ['hello', 'world', '!']
        fb: LS = ['foobar',]
        nil: LS = []

        wt_hw: WLS = Wrap(hw)
        wt_fb: WLS = Wrap(fb)
        wt_nil: WLS = Wrap(nil)

        wi_hw: WLI = Wrap([5, 5, 1])
        wi_fb: WLI = Wrap([6,])
        wi_nil: WLI = Wrap([])

        assert wi_hw == wt_hw.bind(cnt)
        assert wi_fb == wt_fb.bind(cnt)
        assert wi_nil == wt_nil.bind(cnt)
