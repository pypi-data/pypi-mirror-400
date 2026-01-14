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

from pythonic_fp.circulararray.auto import ca, CA


class TestCapacityResizing:
    """Functionality testing"""
    def test_capacity_original(self) -> None:
        """Functionality test"""
        ca0: CA[int] = CA()
        assert ca0.capacity() == 2

        ca0 = ca(1, 2)
        assert ca0.fraction_filled() == 2 / 4

        ca0.pushl(0)
        assert ca0.fraction_filled() == 3 / 4

        ca0.pushr(3)
        assert ca0.fraction_filled() == 4 / 4

        ca0.pushr(4)
        assert ca0.fraction_filled() == 5 / 8

        ca0.pushl(5)
        assert ca0.fraction_filled() == 6 / 8

        assert len(ca0) == 6
        assert ca0.capacity() == 8

        ca0.resize()
        assert ca0.fraction_filled() == 6 / 8

        ca0.resize(30)
        assert ca0.fraction_filled() == 6 / 30

        ca0.resize(3)
        assert ca0.fraction_filled() == 6 / 8

        ca0.popld(0)
        ca0.poprd(0)
        ca0.popld(0)
        ca0.poprd(0)
        assert ca0.fraction_filled() == 2 / 8
        ca0.resize(3)
        assert ca0.fraction_filled() == 2 / 4
        ca0.resize(7)
        assert ca0.fraction_filled() == 2 / 7

    def test_empty(self) -> None:
        """Functionality test"""
        c: CA[int] = ca()
        assert c == ca()
        assert c.capacity() == 2
        c.pushl(1, 2, 3, 4, 5)
        assert c.capacity() == 8
        assert c.poplt(2) == (5, 4)
        c.resize()
        assert c.capacity() == 5
        c.resize(11)
        assert c.capacity() == 11
        assert len(c) == 3
        c.pushl(*range(8))
        assert c.capacity() == 11
        c.pushr(*range(2))
        assert c.capacity() == 22

    def test_one(self) -> None:
        """Functionality test"""
        c = ca(42)
        assert c.capacity() == 3
        c.resize()
        assert c.capacity() == 3
        c.resize(8)
        assert c.capacity() == 8
        assert len(c) == 1
        popped = c.popld(0)
        assert popped == 42
        assert len(c) == 0
        assert c.capacity() == 8

        try:
            c.popl()
        except ValueError as ve:
            assert str(ve) == 'Method popl called on an empty CA'
        else:
            assert False

        try:
            c.popr()
        except ValueError as ve:
            assert str(ve) == 'Method popr called on an empty CA'
        else:
            assert False

        c.pushr(popped)
        assert len(c) == 1
        assert c.capacity() == 8
        c.resize(5)
        assert c.capacity() == 5
        assert len(c) == 1
        c.resize()
        assert c.capacity() == 3
