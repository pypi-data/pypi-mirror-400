from pyskat.data_model.shuffle_matches import (
    calculate_match_sizes,
    shuffle_players_to_matches,
)
import pytest

cases = (
    ["player_count", "prefer", "expected"],
    [
        (3, 3, [3]),
        (3, 4, [3]),
        (4, 3, [4]),
        (4, 4, [4]),
        (4, 5, [4]),
        (4, 10, [4]),
        (5, 3, [5]),
        (5, 4, [5]),
        (5, 5, [5]),
        (7, 3, [3, 4]),
        (7, 4, [4, 3]),
        (7, 5, [4, 3]),
        (8, 3, [4, 4]),
        (8, 4, [4, 4]),
        (8, 5, [4, 4]),
        (9, 3, [3, 3, 3]),
        (9, 4, [3, 3, 3]),
        (9, 5, [5, 4]),
        (10, 3, [3, 3, 4]),
        (10, 4, [4, 3, 3]),
        (10, 5, [5, 5]),
        (12, 3, [3] * 4),
        (12, 4, [4] * 3),
        (12, 5, [4] * 3),
        (14, 3, [3, 3, 4, 4]),
        (14, 4, [4, 4, 3, 3]),
        (14, 5, [5, 5, 4]),
        (15, 3, [3, 3, 3, 3, 3]),
        (15, 4, [4, 4, 4, 3]),
        (16, 3, [3, 3, 3, 3, 4]),
        (16, 4, [4, 4, 4, 4]),
        (16, 5, [4, 4, 4, 4]),
    ],
)


@pytest.mark.parametrize(*cases)
def test_calculate_match_sizes(player_count: int, prefer: int, expected: list[int]):
    actual = calculate_match_sizes(player_count, prefer)
    assert len(actual) == len(expected), f"{actual} != {expected}"
    assert actual == expected, f"{actual} != {expected}"


@pytest.mark.parametrize(*cases)
def test_shuffle_players_to_matches(
    player_count: int, prefer: int, expected: list[int]
):
    actual = shuffle_players_to_matches(range(player_count), prefer)  # type: ignore
    assert len(actual) == len(expected), f"{actual} != {expected}"
    assert [len(m) for m in actual] == expected, f"{actual} != {expected}"


@pytest.mark.parametrize(
    ["player_count", "prefer", "err"],
    [
        (1, 3, ValueError),
        (2, 3, ValueError),
        (6, 1, ValueError),
        (6, 2, ValueError),
    ],
)
def test_calculate_match_sizes_errors(player_count: int, prefer: int, err: type):
    with pytest.raises(err):
        calculate_match_sizes(player_count, prefer)
