"""Hafta 7: Ajanları oyunlarda çalıştırma ve değerlendirme."""

import statistics
import time
from collections import Counter
from dataclasses import dataclass
from typing import Callable, Collection, Optional, Sequence

from .agents.base import Agent
from .feedback import filter_candidates
from .game import MAX_GUESSES, WordleGame

# (adaylar, tahmin, desen) -> kalan adaylar
FilterFn = Callable[[Sequence[str], str, int], list[str]]

# Ajanlar her zaman tutarlı bir aday tahmin ettiği için oyun mutlaka biter;
# bu sınır yalnızca hatalı bir ajana karşı güvenlik içindir.
SAFETY_LIMIT = 30


@dataclass
class GameResult:
    answer: str
    guesses: list[str]
    agent_seconds: float   # ajanın tahmin seçerken harcadığı toplam süre
    filter_seconds: float  # aday filtrelemede harcanan toplam süre

    @property
    def num_guesses(self) -> int:
        return len(self.guesses)

    @property
    def solved(self) -> bool:
        """Gerçek oyundaki gibi 6 tahmin içinde bulundu mu?"""
        return self.num_guesses <= MAX_GUESSES


def play_game(agent: Agent, answer: str, answers: Sequence[str],
              allowed_guesses: Optional[Collection[str]] = None,
              filter_fn: FilterFn = filter_candidates) -> GameResult:
    """Ajanı tek bir gizli kelimeye karşı, kelime bulunana kadar oynatır.

    6 tahmin sınırı burada uygulanmaz; böylece 6'yı aşan oyunlarda ajanın kaç tahmine
    ihtiyaç duyduğunu da görürüz. "Çözüldü mü" bilgisi GameResult.solved'dadır.
    """
    game = WordleGame(answer, allowed_guesses, max_guesses=None)
    candidates = list(answers)
    agent.reset()
    agent_seconds = filter_seconds = 0.0
    while not game.won:
        if game.guesses_used >= SAFETY_LIMIT:
            raise RuntimeError(f"{agent.name} ajanı '{answer}' kelimesini {SAFETY_LIMIT} tahminde bulamadı")
        if not candidates:
            raise RuntimeError(f"Aday kalmadı: '{answer}' gizli kelime listesinde olmayabilir")
        start = time.perf_counter()
        guess = agent.choose_guess(game.history, candidates)
        agent_seconds += time.perf_counter() - start
        pattern = game.play(guess)
        start = time.perf_counter()
        candidates = filter_fn(candidates, guess, pattern)
        filter_seconds += time.perf_counter() - start
    return GameResult(answer, [guess for guess, _ in game.history], agent_seconds, filter_seconds)


@dataclass
class Summary:
    agent: str
    games: int
    mean_guesses: float
    solve_rate: float                 # 6 tahmin içinde çözülen oyunların oranı
    distribution: dict[int, int]      # tahmin sayısı -> oyun sayısı
    worst: list[tuple[str, int]]      # en çok tahmin gerektiren kelimeler
    mean_move_ms: float               # tahmin başına ortalama süre (ajan + filtre)
    total_seconds: float

    def as_dict(self) -> dict:
        return {
            "ajan": self.agent,
            "oyun_sayisi": self.games,
            "ortalama_tahmin": round(self.mean_guesses, 4),
            "cozme_orani_6": round(self.solve_rate, 4),
            "dagilim": {str(k): v for k, v in sorted(self.distribution.items())},
            "en_kotu_kelimeler": self.worst,
            "tahmin_basina_ms": round(self.mean_move_ms, 3),
            "toplam_saniye": round(self.total_seconds, 2),
        }


def summarize(agent_name: str, results: Sequence[GameResult], worst_count: int = 10) -> Summary:
    counts = [r.num_guesses for r in results]
    moves = sum(counts)
    seconds = sum(r.agent_seconds + r.filter_seconds for r in results)
    worst = sorted(results, key=lambda r: -r.num_guesses)[:worst_count]
    return Summary(
        agent=agent_name,
        games=len(results),
        mean_guesses=statistics.fmean(counts),
        solve_rate=sum(r.solved for r in results) / len(results),
        distribution=dict(sorted(Counter(counts).items())),
        worst=[(r.answer, r.num_guesses) for r in worst],
        mean_move_ms=1000 * seconds / moves,
        total_seconds=seconds,
    )


def evaluate(agent: Agent, answers: Sequence[str], secrets: Optional[Sequence[str]] = None,
             allowed_guesses: Optional[Collection[str]] = None,
             filter_fn: FilterFn = filter_candidates,
             progress: bool = False) -> tuple[Summary, list[GameResult]]:
    """Ajanı `secrets` içindeki her kelimeye karşı bir kez oynatır (varsayılan: tüm gizli kelimeler)."""
    secrets = answers if secrets is None else secrets
    results = []
    for i, secret in enumerate(secrets, 1):
        results.append(play_game(agent, secret, answers, allowed_guesses, filter_fn))
        if progress and i % 250 == 0:
            print(f"  {agent.name}: {i}/{len(secrets)} oyun", flush=True)
    return summarize(agent.name, results), results
