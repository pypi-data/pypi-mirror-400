from typing import TypeVar
import random


def calculate_match_sizes(
    player_count: int, preferred_match_size: int = 4
) -> list[int]:
    if player_count < 3:
        raise ValueError("At least 3 players required.")

    if preferred_match_size < 3:
        raise ValueError("At least 3 players per match required.")

    if player_count <= preferred_match_size:
        return [player_count]

    div, mod = divmod(player_count, preferred_match_size)

    if mod == 0:
        return [preferred_match_size] * div

    match_count = div + 1
    matches = [preferred_match_size] * match_count

    i = 1
    last_diff = 0
    while diff := sum(matches) - player_count:
        if diff == last_diff:
            match_count -= 1
            matches = [preferred_match_size] * match_count
            i = 1
            continue

        if i > len(matches):
            i = 1

        matches[-i] += -1 if diff > 0 else 1

        if matches[-i] < 3:
            matches[-i] = 3

        i += 1
        last_diff = diff

    return matches


T = TypeVar("T")


def shuffle_players_to_matches(
    players: list[T], preferred_match_size: int = 4
) -> list[list[T]]:
    match_sizes = calculate_match_sizes(len(players), preferred_match_size)
    players = list(players)

    def _yield_matches():
        for match_size in match_sizes:
            for i in range(match_size):
                yield

    return list(
        [
            [
                players.pop(random.randint(0, len(players) - 1))
                for _ in range(match_size)
            ]
            for match_size in match_sizes
        ]
    )
