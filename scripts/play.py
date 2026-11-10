"""Türkçe Wordle'ı terminalde oyna, bir ajanı izle ya da ajandan öneri al.

Kullanım:
  python scripts/play.py oyna                          # sen oyna
  python scripts/play.py izle --ajan harf              # ajan rastgele bir kelimeyi çözsün
  python scripts/play.py izle --ajan harf --kelime kalem
  python scripts/play.py yardimci --ajan harf          # başka bir sitede oynarken öneri al

Yardımcı modunda deseni şöyle yaz: y = yeşil, s = sarı, g = gri (örnek: yysgg).
"""

import argparse
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from wordle_tr.agents import AGENTS, make_agent  # noqa: E402
from wordle_tr.alphabet import normalize, to_upper  # noqa: E402
from wordle_tr.constraints import Constraints  # noqa: E402
from wordle_tr.feedback import ALL_GREEN, GREEN, YELLOW, decode_pattern, filter_candidates, parse_pattern  # noqa: E402
from wordle_tr.game import MAX_GUESSES, InvalidGuessError, WordleGame  # noqa: E402
from wordle_tr.words import load_answers, load_guesses  # noqa: E402

_BACKGROUND = {GREEN: "42;30", YELLOW: "43;30"}
_GRAY = "100;97"


def render(guess: str, pattern: int, color: bool) -> str:
    colors = decode_pattern(pattern)
    if color:
        return " ".join(f"\033[1;{_BACKGROUND.get(c, _GRAY)}m {to_upper(ch)} \033[0m" for ch, c in zip(guess, colors))
    marks = {GREEN: "🟩", YELLOW: "🟨"}
    return " ".join(to_upper(guess)) + "   " + "".join(marks.get(c, "⬜") for c in colors)


def play_human(guesses, answers, color, rng):
    game = WordleGame(rng.choice(answers), set(guesses))
    print(f"5 harfli bir Türkçe kelime tuttum. {MAX_GUESSES} hakkın var. (Çıkmak için: q)")
    while not game.over:
        text = input(f"{game.guesses_used + 1}. tahmin: ")
        if text.strip().lower() == "q":
            break
        try:
            pattern = game.play(text)
        except InvalidGuessError as error:
            print(f"  {error}")
            continue
        print("  " + render(game.history[-1][0], pattern, color))
    if game.won:
        print(f"Tebrikler! {game.guesses_used} tahminde buldun.")
    else:
        print(f"Kelime: {to_upper(game.answer)}")


def watch_agent(agent, guesses, answers, word, color):
    game = WordleGame(word, set(guesses), max_guesses=None)
    candidates = list(answers) if word in answers else list(guesses)
    print(f"Ajan: {agent.name}   Gizli kelime: {to_upper(word)}")
    while not game.won:
        guess = agent.choose_guess(game.history, candidates)
        before = len(candidates)
        pattern = game.play(guess)
        candidates = filter_candidates(candidates, guess, pattern)
        print(f"  {game.guesses_used}. {render(guess, pattern, color)}   aday: {before} -> {len(candidates)}")
    print(f"{game.guesses_used} tahminde bulundu.")


def assistant(agent, guesses, answers, color):
    print("Başka bir sitede oynarken ajandan öneri al. Her tahminden sonra deseni yaz:")
    print("  y = yeşil, s = sarı, g = gri (örnek: yysgg). Kendi kelimeni denediysen önce kelimeyi yaz.")
    history, candidates = [], list(answers)
    while True:
        suggestion = agent.choose_guess(history, candidates)
        print(f"\nÖneri: {to_upper(suggestion)}   (kalan aday: {len(candidates)})")
        text = input("Hangi kelimeyi denedin? [Enter = öneri, q = çık]: ").strip()
        if text.lower() == "q":
            return
        guess = normalize(text) if text else suggestion
        if guess not in guesses:
            print("  Bu kelime listede yok, tekrar dene.")
            continue
        try:
            pattern = parse_pattern(input("Desen: "))
            Constraints.from_history(history + [(guess, pattern)])  # çelişki varsa hata verir
        except ValueError as error:  # ContradictionError da bir ValueError'dır
            print(f"  {error}")
            continue
        print("  " + render(guess, pattern, color))
        if pattern == ALL_GREEN:
            print(f"Bulundu: {len(history) + 1} tahmin.")
            return
        history.append((guess, pattern))
        candidates = filter_candidates(candidates, guess, pattern)
        if not candidates:
            print("Bu desenlere uyan kelime kalmadı. Bir deseni yanlış girmiş olabilirsin.")
            return
        print("  Bilinenler: " + "; ".join(Constraints.from_history(history).describe()))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mod", choices=["oyna", "izle", "yardimci"])
    parser.add_argument("--ajan", choices=list(AGENTS), default="harf")
    parser.add_argument("--kelime", help="izle modunda gizli kelime (varsayılan: rastgele)")
    parser.add_argument("--tohum", type=int, help="rastgelelik tohumu")
    parser.add_argument("--renksiz", action="store_true", help="ANSI renkleri yerine emoji kullan")
    args = parser.parse_args()

    if os.name == "nt":
        os.system("")  # Windows terminalinde ANSI renklerini açar
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    guesses, answers = load_guesses(), load_answers()
    rng = random.Random(args.tohum)
    color = not args.renksiz and sys.stdout.isatty()
    if args.mod == "oyna":
        play_human(guesses, answers, color, rng)
    elif args.mod == "izle":
        word = normalize(args.kelime) if args.kelime else rng.choice(answers)
        if word not in guesses:
            sys.exit(f"'{word}' kelime listesinde yok.")
        watch_agent(make_agent(args.ajan, args.tohum), guesses, answers, word, color)
    else:
        assistant(make_agent(args.ajan, args.tohum), guesses, answers, color)


if __name__ == "__main__":
    main()
