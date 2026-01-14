# Copyright 2024-2025 Geoffrey R. Scheller
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

from pythonic_fp.circulararray.fixed import caf as caf, CAF as CAF


class TestCapacityFixed:
    """Functionality testing"""
    def test_capacity_original(self) -> None:
        """Functionality test"""
        ca0: CAF[int] = CAF()
        assert ca0.capacity() == 2

        ca0 = caf(1, 2, cap=8)
        assert ca0.fraction_filled() == 2 / 8

        ca0.pushl(0)
        assert ca0.fraction_filled() == 3 / 8

        ca0.pushr(3)
        assert ca0.fraction_filled() == 4 / 8

        ca0.pushr(4)
        assert ca0.fraction_filled() == 5 / 8

        ca0.pushl(5)
        assert ca0.fraction_filled() == 6 / 8

        assert len(ca0) == 6
        assert ca0.capacity() == 8
        assert ca0.fraction_filled() == 6 / 8

        ca0.popld(0)
        ca0.poprd(0)
        ca0.popld(0)
        ca0.poprd(0)
        assert ca0.fraction_filled() == 2 / 8

    def test_empty(self) -> None:
        """Functionality test"""
        c: CAF[int] = caf(cap=401)
        assert c == caf()
        assert len(c) == 0
        for ii in 1, 2, 3, 4, 5:
            c.pushl(ii)
        assert len(c) == 5
        assert c.poplt(2) == (5, 4)
        assert len(c) == 3
        for kk in range(800):
            if not c:
                break
            c.pushl(kk)
        assert c.capacity() == 401
        c.empty()
        c.pushr(0)
        for kk in range(1, 800):
            if not c:
                break
            c.pushl(kk)
        assert c[0] == 400
        assert c[-1] == 0

    def test_one(self) -> None:
        """Functionality test"""
        c = caf(42, cap=5)
        assert c.capacity() == 5
        assert len(c) == 1
        popped = c.popld(0)
        assert popped == 42
        assert len(c) == 0
        assert c.capacity() == 5

        try:
            c.popl()
        except ValueError as ve:
            assert str(ve) == 'Method popl called on an empty CAF'
        else:
            assert False

        try:
            c.popr()
        except ValueError as ve:
            assert str(ve) == 'Method popr called on an empty CAF'
        else:
            assert False

        c.pushr(popped)
        assert len(c) == 1
        assert c.capacity() == 5
        assert len(c) == 1
