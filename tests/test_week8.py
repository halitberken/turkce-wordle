"""Hafta 8: kısıtlar, CSP çözücü ve desen tablosu referans filtreyle aynı sonucu vermeli."""

import random

import numpy as np
import pytest

from wordle_tr.constraints import Constraints, ContradictionError
from wordle_tr.csp_solver import CSPSolver
from wordle_tr.feedback import feedback, is_consistent, parse_pattern
from wordle_tr.filters import filter_by_constraints, filter_by_feedback
from wordle_tr.pattern_table import PatternTable, compute_pattern_matrix
from wordle_tr.words import encode


@pytest.fixture(scope="module")
def table(guesses, answers):
    return PatternTable.build(guesses, answers)


@pytest.fixture(scope="module")
def solver(answers):
    return CSPSolver(answers)


def test_constraints_match_reference_filter(random_histories, answers):
    for _, history in random_histories:
        constraints = Constraints.from_history(history)
        expected = [w for w in answers if is_consistent(w, history)]
        assert [w for w in answers if constraints.is_satisfied(w)] == expected


def test_constraints_on_every_guess_answer_pair_in_a_sample(guesses, answers):
    """Tek gözlem için kısıt ⇔ desen denkliğini rastgele çiftlerde dener."""
    rng = random.Random(99)
    for _ in range(300):
        guess, answer = rng.choice(guesses), rng.choice(answers)
        pattern = feedback(guess, answer)
        constraints = Constraints.from_history([(guess, pattern)])
        for word in rng.sample(answers, 50) + [answer]:
            assert constraints.is_satisfied(word) == (feedback(guess, word) == pattern)


def test_csp_solver_matches_reference_filter(random_histories, answers, solver):
    for _, history in random_histories:
        expected = [w for w in answers if is_consistent(w, history)]
        result = solver.solve(Constraints.from_history(history))
        assert sorted(result.words) == sorted(expected)
        assert result.stats.nodes_visited <= solver.trie.node_count


def test_pattern_table_matches_scalar_feedback(guesses, answers, table):
    rng = random.Random(5)
    for _ in range(20_000):
        guess, answer = rng.choice(guesses), rng.choice(answers)
        assert table.pattern(guess, answer) == feedback(guess, answer)


def test_vectorized_matrix_on_tricky_duplicates():
    words = ["kapak", "kalem", "kasap", "ekmek", "melek", "ekler", "tatlı", "otlak", "kekik", "kayak", "anane"]
    matrix = compute_pattern_matrix(encode(words), encode(words))
    for g, guess in enumerate(words):
        for a, answer in enumerate(words):
            assert matrix[g, a] == feedback(guess, answer)


def test_table_filter_matches_reference(random_histories, answers, table):
    for _, history in random_histories:
        ids = table.all_ids()
        for guess, pattern in history:
            ids = table.filter_ids(ids, guess, pattern)
        assert [answers[i] for i in ids] == [w for w in answers if is_consistent(w, history)]


def test_incremental_filters_agree(random_histories, answers, table):
    for _, history in random_histories[:100]:
        a = b = c = list(answers)
        for guess, pattern in history:
            a = filter_by_feedback(a, guess, pattern)
            b = filter_by_constraints(b, guess, pattern)
            c = table.filter_words(c, guess, pattern)
        assert a == b == c


def test_partition_counts_cover_all_candidates(answers, table):
    ids = table.all_ids()
    counts = table.partition_counts("kalem", ids)
    assert counts.sum() == len(answers)
    assert counts.shape == (243,)
    assert np.count_nonzero(counts) > 10


def test_describe_explains_constraints():
    constraints = Constraints.from_history([("kapak", feedback("kapak", "kalem"))])
    lines = constraints.describe()
    assert "1. harf K" in lines and "2. harf A" in lines
    assert "Kelimede yok: P" in lines
    assert "K başka pozisyonda yok" in lines


def test_contradictory_feedback_is_detected():
    with pytest.raises(ContradictionError):
        Constraints.from_history([("kalem", parse_pattern("yyyyy")), ("kalem", parse_pattern("ggggg"))])
