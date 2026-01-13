

import random
from typing import List, Tuple


def get_sample_texts() -> List[str]:

    return [
        "The quick brown fox jumps over the lazy dog.",
        "Typing is a skill that improves with consistent practice and patience.",
        "Practice makes perfect, so keep typing and don't rush accuracy.",
        "Curses provides a basic terminal UI toolkit for character-cell displays.",
        "Short, focused sessions help build speed and reduce errors over time.",
    ]


def choose_text(randomize: bool = True) -> str:

    samples = get_sample_texts()
    return random.choice(samples) if randomize else samples[0]


def calc_wpm(chars_typed: int, elapsed_seconds: float) -> float:

    minutes = max(elapsed_seconds / 60.0, 1e-6)
    words = chars_typed / 5.0
    return words / minutes


def calc_accuracy(correct_chars: int, total_typed: int) -> float:

    if total_typed == 0:
        return 0.0
    return (correct_chars / total_typed) * 100.0


def summary(correct_chars: int, total_typed: int, elapsed_seconds: float) -> Tuple[float, float]:
    return (calc_wpm(total_typed, elapsed_seconds), calc_accuracy(correct_chars, total_typed))
        




