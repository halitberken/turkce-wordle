"""Wordle ajanları. Yeni ajanlar (entropi, expectimax) AGENTS sözlüğüne eklenir."""

from typing import Optional

from .base import Agent
from .baselines import LetterFrequencyAgent, RandomAgent

AGENTS = {
    "rastgele": RandomAgent,
    "harf": LetterFrequencyAgent,
}


def make_agent(name: str, seed: Optional[int] = None) -> Agent:
    """Komut satırında verilen isimden ajan oluşturur."""
    if name not in AGENTS:
        raise ValueError(f"Bilinmeyen ajan {name!r}. Seçenekler: {', '.join(AGENTS)}")
    if name == "rastgele":
        return RandomAgent(seed)
    return AGENTS[name]()


__all__ = ["AGENTS", "Agent", "LetterFrequencyAgent", "RandomAgent", "make_agent"]
