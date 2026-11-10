"""Hafta 8: Aday kelimeleri bir kısıt sağlama problemi (CSP) olarak bulma.

CSP modeli:
  Değişkenler: X1..X5, gizli kelimenin harfleri
  Alanlar:     her X_i için mümkün harfler (Constraints.domains, başta 29 harf)
  Kısıtlar:    tekli kısıtlar (yeşil/sarı/gri), harf sayısı kısıtları (en az/en çok)
               ve sözlük kısıtı (X1..X5 birlikte geçerli bir kelime olmalı)

Arama: soldan sağa geri izleme (backtracking). Sözlük bir önek ağacında (trie)
tutulur; böylece sözlükte olmayan bir önek (örneğin "kx") hiç genişletilmez.
Her atamadan sonra ileri kontrol (forward checking) yapılır: kalan pozisyonlar,
hâlâ eksik olan harflerin hepsini alamıyorsa o dal budanır.
"""

from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, Optional

from .alphabet import WORD_LENGTH
from .constraints import Constraints


class TrieNode:
    __slots__ = ("children", "word")

    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.word: Optional[str] = None


class WordTrie:
    """Kelimeleri ortak öneklerini paylaşarak saklayan önek ağacı."""

    def __init__(self, words: Iterable[str]):
        self.root = TrieNode()
        self.node_count = 1
        for word in words:
            node = self.root
            for letter in word:
                if letter not in node.children:
                    node.children[letter] = TrieNode()
                    self.node_count += 1
                node = node.children[letter]
            node.word = word


@dataclass
class SearchStats:
    nodes_visited: int = 0       # genişletilen trie düğümü sayısı
    domain_prunes: int = 0       # alan dışında kaldığı için atlanan harfler
    count_prunes: int = 0        # bir harfin en çok sayısı aşıldığı için budanan dallar
    lookahead_prunes: int = 0    # ileri kontrolde budanan dallar


@dataclass
class SolveResult:
    words: list[str]
    stats: SearchStats = field(default_factory=SearchStats)


class CSPSolver:
    def __init__(self, words: Iterable[str]):
        self.trie = WordTrie(words)

    def solve(self, constraints: Constraints) -> SolveResult:
        """Kısıtları sağlayan tüm sözlük kelimelerini bulur."""
        domains = constraints.domains()
        max_count = constraints.max_count
        min_count = constraints.min_count
        stats = SearchStats()
        found: list[str] = []
        counts = Counter()

        def feasible(next_position: int) -> bool:
            """İleri kontrol: eksik harfler kalan pozisyonlara sığıyor mu?"""
            remaining = WORD_LENGTH - next_position
            missing_total = 0
            for letter, low in min_count.items():
                missing = low - counts[letter]
                if missing <= 0:
                    continue
                missing_total += missing
                slots = sum(1 for j in range(next_position, WORD_LENGTH) if letter in domains[j])
                if slots < missing:
                    return False
            return missing_total <= remaining

        def search(node: TrieNode, position: int) -> None:
            stats.nodes_visited += 1
            if position == WORD_LENGTH:
                if node.word is not None:
                    found.append(node.word)
                return
            domain = domains[position]
            for letter, child in node.children.items():
                if letter not in domain:
                    stats.domain_prunes += 1
                    continue
                counts[letter] += 1
                if counts[letter] > max_count.get(letter, WORD_LENGTH):
                    stats.count_prunes += 1
                elif not feasible(position + 1):
                    stats.lookahead_prunes += 1
                else:
                    search(child, position + 1)
                counts[letter] -= 1

        if feasible(0):
            search(self.trie.root, 0)
        return SolveResult(found, stats)
