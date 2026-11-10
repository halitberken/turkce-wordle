import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from wordle_tr.feedback import feedback  # noqa: E402
from wordle_tr.words import load_answers, load_guesses  # noqa: E402


@pytest.fixture(scope="session")
def guesses():
    return load_guesses()


@pytest.fixture(scope="session")
def answers():
    return load_answers()


@pytest.fixture(scope="session")
def random_histories(guesses, answers):
    """Rastgele oyun durumları: (gizli kelime, [(tahmin, desen), ...])."""
    rng = random.Random(1234)
    states = []
    for _ in range(300):
        answer = rng.choice(answers)
        history = [(g, feedback(g, answer)) for g in rng.sample(guesses, rng.randint(1, 4))]
        states.append((answer, history))
    return states
