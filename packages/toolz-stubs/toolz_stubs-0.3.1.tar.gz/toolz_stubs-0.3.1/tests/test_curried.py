"""Tests for toolz.curried to verify stubs work correctly."""

from collections.abc import Iterable, Iterator
from typing import Any, Callable, assert_type

import toolz.curried as curr


class TestMapcat:
    """Tests for curried mapcat function."""

    def test_can_expand(self) -> None:
        """mapcat should work with functions that expand elements."""

        def possibly_expands(item: int | list[int]) -> list[int]:
            if isinstance(item, int):
                return [item, item]
            return item

        result = curr.mapcat(possibly_expands, [1, [2, 3], 4])

        _ = assert_type(result, Iterator[int])
        assert list(result) == [1, 1, 2, 3, 4, 4]


def test_basic_curry_func() -> None:
    """Curried pipe should correctly infer list[str] output type."""

    def add_one(i: int) -> int:
        return i + 1

    a_result = curr.pipe(range(5), curr.map(add_one), curr.map(str), list)

    _ = assert_type(a_result, list[str])
    assert a_result == ["1", "2", "3", "4", "5"]


class TestSorted:
    def test_can_type_comparable(self) -> None:
        """From https://github.com/mgrinshpon/toolz-stubs/issues/34"""

        def mod_3(x: int) -> int:
            return x % 3

        result = curr.pipe(range(10), curr.sorted(key=mod_3), list)
        _ = assert_type(result, list[int])
        assert result == [0, 3, 6, 9, 1, 4, 7, 2, 5, 8]


class TestMergeWith:
    """Tests for curried merge_with function."""

    def test_with_list_typed_function(self) -> None:
        """merge_with should accept functions typed as taking list[V].

        This tests the contravariance fix: the runtime passes a list,
        so functions expecting list[V] should be accepted.
        """
        # Explicitly typed as taking list[int], not Iterable[int]
        sum_list: Callable[[list[int]], int] = sum

        result = curr.merge_with(sum_list, {1: 1, 2: 2}, {1: 10, 2: 20})

        _ = assert_type(result, dict[int, int])
        assert result == {1: 11, 2: 22}

    def test_with_iterable_typed_function(self) -> None:
        """merge_with should also accept functions typed as taking Iterable[V].

        Due to contravariance, Callable[[Iterable[V]], V] is a subtype of
        Callable[[list[V]], V], so this should also work.
        """
        # Explicitly typed as taking Iterable[int]
        sum_iter: Callable[[Iterable[int]], int] = sum

        result = curr.merge_with(sum_iter, {"a": 1, "b": 2}, {"a": 10, "b": 20})

        _ = assert_type(result, dict[str, int])
        assert result == {"a": 11, "b": 22}


class TestJoin:
    """Tests for curried join function."""

    def test_partial_application_in_pipe(self) -> None:
        """join can be partially applied for use in pipes.

        Common pattern: pre-configure join with keys and left sequence,
        then pipe the right sequence through.
        """
        friends = [
            ("Alice", "Edith"),
            ("Bob", "Alice"),
        ]
        cities = [
            ("Alice", "NYC"),
            ("Edith", "Paris"),
        ]

        # Partially apply: "find cities where my friends live"
        # join(second, friends, first) returns a callable waiting for rightseq
        find_friend_cities = curr.join(curr.second, friends, curr.first)

        result = curr.pipe(
            cities,
            find_friend_cities,
            list,
        )

        # Note: The right side is Any because U can't be inferred in partial application
        # (rightseq isn't provided yet when join(leftkey, leftseq, rightkey) is called)
        _ = assert_type(result, list[tuple[tuple[str, str], Any]])  # pyright: ignore[reportExplicitAny]
        assert (("Alice", "Edith"), ("Edith", "Paris")) in result

    def test_outer_join_with_defaults(self) -> None:
        """join with defaults for outer join behavior."""

        def identity(x: int) -> int:
            return x

        left = [1, 2, 3]
        right = [2, 3, 4]

        # Full outer join - unmatched items paired with None
        result = curr.pipe(
            right,
            curr.join(identity, left, identity, left_default=None, right_default=None),
            list,
        )

        _ = assert_type(result, list[tuple[int | None, int | None]])
        assert (2, 2) in result
        assert (None, 4) in result  # 4 not in left
        assert (1, None) in result  # 1 not in right
