import random

from wordle_tr.agents import LetterFrequencyAgent, RandomAgent, make_agent
from wordle_tr.simulate import evaluate, play_game


def test_agents_find_every_sampled_answer(answers, guesses):
    secrets = random.Random(7).sample(answers, 40)
    allowed = set(guesses)
    for agent in [RandomAgent(seed=0), LetterFrequencyAgent()]:
        for secret in secrets:
            result = play_game(agent, secret, answers, allowed)
            assert result.guesses[-1] == secret
            assert len(set(result.guesses)) == len(result.guesses)  # aynı kelime iki kez denenmez


def test_letter_frequency_agent_is_deterministic(answers):
    agent = LetterFrequencyAgent()
    first = agent.choose_guess([], answers)
    assert first == agent.choose_guess([], answers)
    assert len(set(first)) == 5  # en iyi açılış kelimesinde harf tekrarı olmaz


def test_random_agent_is_reproducible_with_seed(answers):
    a = [RandomAgent(seed=3).choose_guess([], answers) for _ in range(3)]
    b = [RandomAgent(seed=3).choose_guess([], answers) for _ in range(3)]
    assert a == b


def test_evaluate_summary(answers):
    secrets = answers[:30]
    summary, results = evaluate(make_agent("harf"), answers, secrets)
    assert summary.games == 30 == len(results)
    assert sum(summary.distribution.values()) == 30
    assert 1 <= summary.mean_guesses <= 10
    assert 0 <= summary.solve_rate <= 1
