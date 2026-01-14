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

from pythonic_fp.circulararray.auto import ca, CA


class TestReprResizing:
    """Functionality testing"""
    def test_repr(self) -> None:
        """Functionality test"""
        ca0: CA[int] = CA()
        assert repr(ca0) == 'ca()'
        foo: CA[int] = eval('ca()')
        bar: CA[int] = eval(repr(ca0))
        assert foo == bar

        ca1: CA[str|int] = CA()
        assert repr(ca1) == 'ca()'
        ca2: CA[int|str] = eval(repr(ca1))
        assert ca2 == ca1
        assert ca2 is not ca1

        ca1.pushr(1)
        ca1.pushl('foo')
        assert repr(ca1) == "ca('foo', 1)"
        ca2 = eval(repr(ca1))
        assert ca2 == ca1
        assert ca2 is not ca1

        assert ca1.popld('bar') == 'foo'
        ca1.pushr(2)
        ca1.pushr(3)
        ca1.pushr(4)
        ca1.pushr(5)
        assert ca1.popl() == 1
        ca1.pushl(42)
        ca1.popr()
        assert repr(ca1) == 'ca(42, 2, 3, 4)'
        ca2 = eval(repr(ca1))
        assert ca2 == ca1
        assert ca2 is not ca1

        ca3: CA[int] = ca(1, 10, 0, 42)
        ca3.pushr(2, 100, 3)
        assert ca3.popl() == 1
        assert ca3.popr() == 3
        ca3.pushl(9, 8)
        assert ca3.poprt(2) == (100, 2)
        ca3.pushr(1, 2, 3)
        assert repr(ca3) == 'ca(8, 9, 10, 0, 42, 1, 2, 3)'

        ca4: CA[int] = CA([1, 10, 0, 42])
        ca4.pushr(2, 100, 3)
        assert ca4.popl() == 1
        assert ca4.popr() == 3
        ca4.pushl(9, 8)
        assert ca4.poprt(2) == (100, 2)
        ca4.pushr(1, 2, 3)
        assert repr(ca4) == 'ca(8, 9, 10, 0, 42, 1, 2, 3)'
