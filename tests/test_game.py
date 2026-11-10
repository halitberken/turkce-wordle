import pytest

from wordle_tr.feedback import ALL_GREEN
from wordle_tr.game import InvalidGuessError, WordleGame


def test_win_in_two_guesses(guesses):
    game = WordleGame("kalem", set(guesses))
    assert game.play("kapak") != ALL_GREEN
    assert not game.over
    assert game.play("KALEM") == ALL_GREEN  # büyük harf de kabul edilir
    assert game.won and game.over and game.guesses_used == 2


def test_game_ends_after_six_guesses(guesses):
    game = WordleGame("kalem", set(guesses))
    for word in ["kapak", "lamba", "akrep", "ekmek", "kasap", "tatlı"]:
        game.play(word)
    assert game.over and not game.won
    with pytest.raises(InvalidGuessError):
        game.play("kalem")


def test_invalid_guesses_are_rejected_without_using_a_turn(guesses):
    game = WordleGame("kalem", set(guesses))
    for word in ["kale", "kalemm", "qwert", "aaaaa"]:
        with pytest.raises(InvalidGuessError):
            game.play(word)
    assert game.guesses_used == 0


def test_unlimited_game_for_experiments():
    game = WordleGame("kalem", max_guesses=None)
    for _ in range(10):
        game.play("kapak")
    assert not game.over
