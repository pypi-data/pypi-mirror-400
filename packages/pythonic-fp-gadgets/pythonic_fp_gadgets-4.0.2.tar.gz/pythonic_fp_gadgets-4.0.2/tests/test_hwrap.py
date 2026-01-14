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

from pythonic_fp.gadgets.wrap import HWrap


class TestGadgetHWrapBuiltins:
    def test_hwrap_simple(self) -> None:
        w0 = HWrap(0)
        w1 = HWrap(1)
        x1 = HWrap(1)

        assert w0 != w1
        assert w1 == x1
        assert w1 is w1
        assert w1 is not x1

        assert hash(w0) == hash(w0)
        assert hash(w1) == hash(w1)
        assert hash(w1) == hash(x1)
        assert hash(w1) != hash(w0)

    def test_map(self) -> None:
        def cat(s: str) -> str:
            return s + s

        wa = HWrap('a')
        waa = HWrap('aa')
        waaaa = HWrap('aaaa')

        xaa = wa.map(cat)
        xaaaa = xaa.map(cat)

        assert xaa == waa
        assert xaa != waaaa
        assert xaaaa == waaaa
        assert waaaa == xaaaa

    def test_bind(self) -> None:
        type TS = tuple[str, ...]
        type WLS = HWrap[TS]
        type TI = tuple[int, ...]
        type WTI = HWrap[TI]

        def cnt(ts: TS) -> WTI:
            ti: TI = ()
            for s in ts:
                ti += (len(s),)
            return HWrap(ti)

        hw: TS = ('hello', 'world', '!')
        fb: TS = ('foobar',)
        nil: TS = ()

        wt_hw: WLS = HWrap(hw)
        wt_fb: WLS = HWrap(fb)
        wt_nil: WLS = HWrap(nil)

        wi_hw: WTI = HWrap((5, 5, 1))
        wi_fb: WTI = HWrap((6,))
        wi_nil: WTI = HWrap(())

        assert wi_hw == wt_hw.bind(cnt)
        assert wi_fb == wt_fb.bind(cnt)
        assert wi_nil == wt_nil.bind(cnt)
