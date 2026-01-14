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

from pythonic_fp.circulararray.fixed import CAF, caf


class TestFoldingWithNone:
    def test_tuple_no_none(self) -> None:
        def tuple_no_none_left[T](left: tuple[T, ...], right: T | None) -> tuple[T, ...]:
            if right is None:
                return left
            return left + (right,)

        def tuple_no_none_right[T](left: T | None, right: tuple[T, ...]) -> tuple[T, ...]:
            if left is None:
                return right
            return (left,) + right

        ca1: CAF[int | None]
        ca2: CAF[int | None]
        tup:  tuple[float, ...]
        tup0: tuple[float, ...]
        tup1: tuple[float, ...]
        tup2: tuple[float, ...]

        ca1 = caf(1, 2, 3, 4, 5, 6, 7)
        ca2 = caf(1, None, 3, 4, 5, None, 7)
        tup = tuple([-1, 0])                     # = -1, 0
        tup0 = tuple()                           # = ()
        tup1 = 1, 2, 3, 4, 5, 6, 7
        tup2 = -1, 0, 1, 3, 4, 5, 7
        assert ca1.foldl(tuple_no_none_left, tup0) == tup1
        assert ca2.foldl(tuple_no_none_left, tup) == tup2

        ca1_f: CAF[float | None]
        ca2_f: CAF[float | None]
        tup_f:  tuple[float, ...]
        tup0_f: tuple[float, ...]
        tup1_f: tuple[float, ...]
        tup2_f: tuple[float, ...]

        ca1_f = caf(1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0)
        ca2_f = caf(None, 2.0, None, 4.0, 5.0, 6.0, None, None)
        tup_f = tuple([9, 10, 11])
        tup0_f = tuple()
        tup1_f = tuple((1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0))
        tup2_f = 2.0, 4.0, 5.0, 6.0, 9.0, 10.0, 11.0
        assert ca1_f.foldr(tuple_no_none_right, tup0_f) == tup1_f
        assert ca2_f.foldr(tuple_no_none_right, tup_f) == tup2_f

    def test_foldl(self) -> None:
        def lt20(n: int | None, m: int | None) -> int | None:
            if n is None or m is None:
                return None
            if (sum := n + m) < 20:
                return sum
            return None

        # Edge cases
        c0: CAF[int | None] = caf()

        try:
            c0.foldl(lt20)
        except ValueError:
            assert True
        else:
            assert False
        assert c0.foldl(lt20, 0) == 0
        assert c0.foldl(lt20, 42) == 42
        assert c0.foldl(lt20, None) is None

        c1_5: CAF[int | None] = caf(5)
        c1_42: CAF[int | None] = caf(42)
        c1_none: CAF[int | None] = caf(None)

        assert c1_5.foldl(lt20) == 5
        assert c1_42.foldl(lt20) == 42
        assert c1_none.foldl(lt20) is None

        assert c1_5.foldl(lt20, 4) == 9
        assert c1_42.foldl(lt20, 0) is None
        assert c1_none.foldl(lt20, 5) is None

        # typical cases
        c4: CAF[int | None] = caf(1, 2, 3, 4)
        c5_none = caf(1, 1, None, 1, 1)
        c7: CAF[int | None] = caf(1, 2, 3, 4, 5, 6, 7)

        assert c4.foldl(lt20) == 10
        assert c4.foldl(lt20, -1) == 9
        assert c5_none.foldl(lt20) is None
        assert c5_none.foldl(lt20, 1) is None
        assert c7.foldl(lt20) is None
        assert c7.foldl(lt20, -10) == 18
        assert c7.foldl(lt20, -5) is None
