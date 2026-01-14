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
.. admonition:: Fixed storage capacity circular array.**

    - O(1) pops and pushes either end
    - O(1) indexing, does not support slicing
    - fixed total storage capacity
    - iterable, safely mutates while iterators iterating over previous state
    - comparisons compare identity before equality, like builtins
    - in boolean context, falsy when either empty or full, otherwise truthy
    - function ``caf`` produces fixed capacity circular array from arguments

"""

from collections.abc import Callable, Iterable, Iterator
from typing import cast, Final, overload
from pythonic_fp.gadgets.sentinels.novalue import NoValue

__all__ = ['CAF', 'caf']

nada: Final[NoValue] = NoValue()


class CAF[I]:
    __slots__ = '_items', '_cnt', '_cap', '_front', '_rear'

    def __init__(self, *items: Iterable[I], cap: int = 2) -> None:
        """
        :param items: Optionally takes a single iterable to
                      initially populate the circular array.
        :param cap: Minimum fixed storage capacity of circular array.
        :raises TypeError: When ``items[0]`` not iterable,
        :raises ValueError: If more than 1 iterable is given.
        """
        cap = max(2, cap)
        if (size := len(items)) > 1:
            msg = f'CAF expects at most 1 argument, got {size}'
            raise ValueError(msg)
        if size:
            values: list[I | NoValue] = list(cast(Iterable[I | NoValue], items[0]))
            cnt = len(values)
            cap = max(cnt, cap)
            self._items = values + [nada] * (cap - cnt)
        else:
            self._items = [nada] * cap
            cnt = 0
        self._cap: Final[int] = cap
        self._cnt = cnt
        if cnt == 0:
            self._front = 0
            self._rear = cap - 1
        else:
            self._front = 0
            self._rear = cnt - 1

    def __iter__(self) -> Iterator[I]:
        if self._cnt > 0:
            (
                cap,
                rear,
                position,
                current_state,
            ) = (
                self._cap,
                self._rear,
                self._front,
                self._items.copy(),
            )

            while position != rear:
                yield cast(I, current_state[position])
                position = (position + 1) % cap
            yield cast(I, current_state[position])

    def __reversed__(self) -> Iterator[I]:
        if self._cnt > 0:
            (
                cap,
                front,
                position,
                current_state,
            ) = (
                self._cap,
                self._front,
                self._rear,
                self._items.copy(),
            )

            while position != front:
                yield cast(I, current_state[position])
                position = (position - 1) % cap
            yield cast(I, current_state[position])

    def __repr__(self) -> str:
        return 'caf(' + ', '.join(map(repr, self)) + ')'

    def __str__(self) -> str:
        return '(|' + ', '.join(map(str, self)) + '|)'

    def __bool__(self) -> bool:
        return 0 < self._cnt < self._cap

    def __len__(self) -> int:
        return self._cnt

    def __getitem__(self, idx: int) -> I:
        cnt = self._cnt
        if 0 <= idx < cnt:
            return cast(I, self._items[(self._front + idx) % self._cap])

        if -cnt <= idx < 0:
            return cast(I, self._items[(self._front + cnt + idx) % self._cap])

        if cnt == 0:
            msg0 = 'Trying to get a value from an empty CAF.'
            raise IndexError(msg0)

        msg1 = 'Out of bounds: '
        msg2 = f'index = {idx} not between {-cnt} and {cnt - 1} '
        msg3 = 'while getting value from a CAF.'
        raise IndexError(msg1 + msg2 + msg3)

    def __setitem__(self, idx: int, val: I) -> None:
        cnt = self._cnt
        if 0 <= idx < cnt:
            self._items[(self._front + idx) % self._cap] = val
        elif -cnt <= idx < 0:
            self._items[(self._front + cnt + idx) % self._cap] = val
        else:
            if cnt < 1:
                msg0 = 'Trying to index into an empty CAF.'
                raise IndexError(msg0)
            msg1 = 'Out of bounds: '
            msg2 = f'index = {idx} not between {-cnt} and {cnt - 1} '
            msg3 = 'while setting value from a CAF.'
            raise IndexError(msg1 + msg2 + msg3)

    def __delitem__(self, idx: int) -> None:
        item_list = list(self)
        del item_list[idx]
        _ca = CAF(item_list, cap = self._cap)
        (
            self._items,
            self._cnt,
            self._front,
            self._rear,
        ) = (
            _ca._items,
            _ca._cnt,
            _ca._front,
            _ca._rear,
        )
        del _ca

    def __eq__(self, other: object) -> bool:
        """
        :param other: The object to be compared to.
        :returns: ``True`` if object is another CAF whose items compare
                  as equal to the corresponding items in the CAF,
                  otherwise ``False``.
        """
        if self is other:
            return True
        if not isinstance(other, type(self)):
            return False

        (
            front1,
            cnt1,
            cap1,
            front2,
            cnt2,
            cap2,
        ) = (
            self._front,
            self._cnt,
            self._cap,
            other._front,
            other._cnt,
            other._cap,
        )

        if cnt1 != cnt2:
            return False

        for nn in range(cnt1):
            if (
                self._items[(front1 + nn) % cap1]
                is other._items[(front2 + nn) % cap2]
            ):
                continue
            if (
                self._items[(front1 + nn) % cap1]
                != other._items[(front2 + nn) % cap2]
            ):
                return False
        return True

    def pushl(self, item: I) -> None:
        """Push ``item`` on from left.

        :param item: Single item pushed onto circular array from left (front).
        :raises ValueError: When called on a full ``CAF``.
        """
        if self._cnt == self._cap:
            msg = 'Method pushl called on a full CAF'
            raise ValueError(msg)

        (
            self._front,
            self._items[self._front],
            self._cnt,
        ) = (
            (self._front - 1) % self._cap,
            item,
            self._cnt + 1,
        )

    def pushr(self, item: I) -> None:
        """Push ``item`` on from Right.

        :param item: Single ``item`` pushed onto circular array from right (rear).
        :raises ValueError: When called on a full fixed storage capacity circular array.
        """
        if self._cnt == self._cap:
            msg = 'Method pushr called on a full CAF'
            raise ValueError(msg)

        (
            self._rear,
            self._items[self._rear],
            self._cnt,
        ) = (
            (self._rear + 1) % self._cap,
            item,
            self._cnt + 1,
        )

    def popl(self) -> I:
        """Pop single item off from left side.

        :returns: Item popped from left side (front) of circular array.
        :raises ValueError: When called on an empty circular array.
        """
        if self._cnt > 1:
            (
                d,
                self._items[self._front],
                self._front,
                self._cnt,
            ) = (
                self._items[self._front],
                nada,
                (self._front + 1) % self._cap,
                self._cnt - 1,
            )
        elif self._cnt == 1:
            (
                d,
                self._items[self._front],
                self._cnt,
                self._front,
                self._rear,
            ) = (
                self._items[self._front],
                nada,
                0,
                0,
                self._cap - 1,
            )
        else:
            msg = 'Method popl called on an empty CAF'
            raise ValueError(msg)
        return cast(I, d)

    def popr(self) -> I:
        """Pop single item off from right side.

        :returns: Item popped from right side (rear) of circular array.
        :raises ValueError: When called on an empty circular array.
        """
        if self._cnt > 1:
            (
                d,
                self._items[self._rear],
                self._rear,
                self._cnt,
            ) = (
                self._items[self._rear],
                nada,
                (self._rear - 1) % self._cap,
                self._cnt - 1,
            )
        elif self._cnt == 1:
            (
                d,
                self._items[self._front],
                self._cnt,
                self._front,
                self._rear,
            ) = (
                self._items[self._front],
                nada,
                0,
                0,
                self._cap - 1,
            )
        else:
            msg = 'Method popr called on an empty CAF'
            raise ValueError(msg)
        return cast(I, d)

    def popld(self, default: I) -> I:
        """Pop one item from left side of the circular array, provide
        a mandatory default value. "Safe" version of popl.

        :param default: Item returned if circular array is empty.
        :returns: Item popped from left side or default item if empty.
        """
        try:
            return self.popl()
        except ValueError:
            return default

    def poprd(self, default: I) -> I:
        """Pop one item from right side of the circular array, provide
        a mandatory default value. "Safe" version of popr.

        :param default: Item returned if circular array is empty.
        :returns: Item popped from right side or default item if empty.
        """
        try:
            return self.popr()
        except ValueError:
            return default

    def poplt(self, maximum: int) -> tuple[I, ...]:
        """Pop multiple items from left side of circular array.

        :param maximum: Maximum number of items to pop, may pop less
                        if not enough items.
        :returns: Tuple of items in the order popped, left to right.
        """
        item_list: list[I] = []

        while maximum > 0:
            try:
                item_list.append(self.popl())
            except ValueError:
                break
            else:
                maximum -= 1

        return tuple(item_list)

    def poprt(self, maximum: int) -> tuple[I, ...]:
        """Pop multiple items from right side of circular array.

        :param maximum: Maximum number of items to pop, may pop less
                        if not enough items.
        :returns: Tuple of items in the order popped, right to left.
        """
        item_list: list[I] = []
        while maximum > 0:
            try:
                item_list.append(self.popr())
            except ValueError:
                break
            else:
                maximum -= 1
        return tuple(item_list)

    def rotl(self, n: int = 1) -> None:
        """Rotate items to the left.

        :param n: Number of times to shift elements to the left.
        """
        if self._cnt < 2:
            return
        for _ in range(n, 0, -1):
            self.pushr(self.popl())

    def rotr(self, n: int = 1) -> None:
        """Rotate items to the right.

        :param n: Number of times to shift elements to the right.
        """
        if self._cnt < 2:
            return
        for _ in range(n, 0, -1):
            self.pushl(self.popr())

    def map[U](self, f: Callable[[I], U]) -> 'CAF[U]':
        """Apply function ``f`` over the circular array's contents,

        :param f: Callable from type ``I`` to type ``U``.
        :returns: New fixed capacity circular array instance.
        """
        return CAF(map(f, self), cap = self._cap)

    @overload
    def foldl[L](self, f: Callable[[I, I], I]) -> I: ...
    @overload
    def foldl[L](self, f: Callable[[L, I], L], start: L) -> L: ...

    def foldl[L](self, f: Callable[[L, I], L], start: L | NoValue = nada) -> L:
        """Fold left with a function and optional stating item.

        :param f: Folding function, first argument to ``f`` is for
                  the accumulator.
        :param start: Optional starting item.
        :returns: Reduced value produced by the left fold.
        :raises ValueError: When circular array empty and no starting
                            item given.
        """
        if self._cnt == 0:
            if start is nada:
                msg = 'Method foldl called on an empty CAF without a start item.'
                raise ValueError(msg)
            return cast(L, start)

        if start is nada:
            acc = cast(L, self[0])  # in this case D = L
            for idx in range(1, self._cnt):
                acc = f(acc, self[idx])
            return acc

        acc = cast(L, start)
        for d in self:
            acc = f(acc, d)
        return acc

    @overload
    def foldr[R](self, f: Callable[[I, I], I]) -> I: ...
    @overload
    def foldr[R](self, f: Callable[[I, R], R], start: R) -> R: ...

    def foldr[R](self, f: Callable[[I, R], R], start: R | NoValue = nada) -> R:
        """Fold right with a function and an optional starting item.

        :param f: Folding function, second argument to ``f`` is for
                  the accumulator.
        :param start: Optional starting item.
        :returns: Reduced value produced by the right fold.
        :raises ValueError: When circular array empty and no starting
                            item given.
        """
        if self._cnt == 0:
            if start is nada:
                msg = 'Method foldr called on empty CAF without initial value.'
                raise ValueError(msg)
            return cast(R, start)

        if start is nada:
            acc = cast(R, self[-1])  # in this case D = R
            for idx in range(self._cnt - 2, -1, -1):
                acc = f(self[idx], acc)
            return acc

        acc = cast(R, start)
        for d in reversed(self):
            acc = f(d, acc)
        return acc

    def capacity(self) -> int:
        """Return fixed storage capacity of the circular array.

        :returns: Fixed storage capacity.
        """
        return self._cap

    def empty(self) -> None:
        """Empty the circular array."""
        (
            self._items,
            self._front,
            self._rear,
            self._cnt,
        ) = (
            [nada] * self._cap,
            0,
            self._cap - 1,
            0,
        )

    def fraction_filled(self) -> float:
        """Find fraction of the storage capacity which is filled.

        :returns: The ratio count/capacity.
        """
        return self._cnt / self._cap


def caf[T](*items: T, cap: int = 2) -> CAF[T]:
    """Produce a circular array from a variable number of arguments.

    :param items: Initial items for a new fixed capacity :circular array.
    :param cap: The minimum storage capacity to set.
    :returns: New fixed storage capacity circular array.
    """
    return CAF(items, cap=cap)
