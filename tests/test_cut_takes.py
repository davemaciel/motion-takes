"""Testes do algoritmo de corte de takes (cut_takes.compute_takes).

Executar: python3 -m pytest tests/ -q   (ou)   python3 tests/test_cut_takes.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from cut_takes import compute_takes  # noqa: E402


def W(word, start, end):
    return {"word": word, "start": start, "end": end}


class TestComputeTakes(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(compute_takes([]), [])

    def test_single_word(self):
        words = [W("ola", 0.0, 0.5)]
        takes = compute_takes(words)
        self.assertEqual(len(takes), 1)
        self.assertEqual(takes[0]["text"], "ola")

    def test_no_take_exceeds_max(self):
        # 20 palavras de 1s cada, sem pausas -> tem de partir em takes <= 10s
        words = [W(f"w{i}", float(i), float(i) + 0.9) for i in range(20)]
        takes = compute_takes(words, max_dur=10.0, min_dur=1.5, pad=0.0)
        self.assertGreaterEqual(len(takes), 2)
        for t in takes:
            self.assertLessEqual(t["end"] - t["start"], 10.0 + 1e-6,
                                 f"take excede 10s: {t}")

    def test_prefers_pause_boundary(self):
        # Duas frases de ~5s com uma pausa GRANDE a meio (aos 5.0-6.0s).
        # O corte deve acontecer na pausa, nao a meio da segunda frase.
        words = []
        t = 0.0
        for i in range(5):  # frase 1: 0.0 -> 5.0
            words.append(W(f"a{i}", t, t + 0.8))
            t += 1.0
        t = 6.0  # pausa de 1s (de 5.0 a 6.0)
        for i in range(5):  # frase 2: 6.0 -> 11.0
            words.append(W(f"b{i}", t, t + 0.8))
            t += 1.0
        takes = compute_takes(words, max_dur=10.0, min_dur=1.5, pad=0.0)
        self.assertEqual(len(takes), 2)
        # O fim do 1o take deve estar na ultima palavra da frase 1 (~4.8s),
        # nao a meio da frase 2.
        self.assertLess(takes[0]["end"], 5.5)
        self.assertEqual(takes[0]["text"], "a0 a1 a2 a3 a4")
        self.assertEqual(takes[1]["text"], "b0 b1 b2 b3 b4")

    def test_never_splits_a_word(self):
        # Os limites dos takes nunca devem cair dentro de [start,end] de uma palavra.
        words = [W(f"w{i}", i * 0.7, i * 0.7 + 0.6) for i in range(40)]
        takes = compute_takes(words, max_dur=10.0, min_dur=1.5, pad=0.05)
        for w in words:
            for t in takes:
                # uma palavra ou esta totalmente dentro de um take ou totalmente fora
                inside = t["start"] <= w["start"] + 1e-6 and w["end"] <= t["end"] + 1e-6
                overlaps_edge = (w["start"] < t["start"] - 1e-6 < w["end"]) or \
                                (w["start"] < t["end"] + 1e-6 < w["end"] - 1e-6)
                self.assertFalse(overlaps_edge and not inside,
                                 f"limite do take parte a palavra {w} -> {t}")

    def test_sentence_punctuation_bonus(self):
        # 14 palavras de 1s cada (total 13.8s) FORCAM um corte antes dos 10s.
        # Gaps todos iguais (0.2s); so a palavra 4 termina frase ('cinco.').
        # Com gaps iguais, o bonus de fim-de-frase deve vencer o vies de
        # "encher os 10s" e o corte deve cair em 'cinco.'.
        words = []
        for i in range(14):
            w = "cinco." if i == 4 else f"w{i}"
            words.append(W(w, i * 1.0, i * 1.0 + 0.8))
        takes = compute_takes(words, max_dur=10.0, min_dur=1.5, pad=0.0)
        self.assertTrue(takes[0]["text"].endswith("cinco."),
                        f"esperava corte no fim da frase, got {takes[0]}")

    def test_covers_all_words_in_order(self):
        words = [W(f"w{i}", i * 1.3, i * 1.3 + 1.0) for i in range(25)]
        takes = compute_takes(words, max_dur=10.0)
        joined = " ".join(t["text"] for t in takes).split()
        self.assertEqual(joined, [w["word"] for w in words])

    def test_indices_are_sequential(self):
        words = [W(f"w{i}", i * 1.3, i * 1.3 + 1.0) for i in range(25)]
        takes = compute_takes(words, max_dur=10.0)
        self.assertEqual([t["index"] for t in takes], list(range(1, len(takes) + 1)))

    def test_pad_does_not_overlap_neighbors(self):
        words = [W(f"w{i}", float(i), float(i) + 0.5) for i in range(30)]
        takes = compute_takes(words, max_dur=5.0, min_dur=1.0, pad=0.3)
        for a, b in zip(takes, takes[1:]):
            self.assertLessEqual(a["end"], b["start"] + 1e-6,
                                 "takes consecutivos nao se devem sobrepor")

    def test_duration_never_exceeds_max_with_expansion(self):
        # Mesmo com pad/expansao para o silencio, nenhuma duracao final > max.
        words = [W(f"w{i}", float(i) + 0.05, float(i) + 0.85) for i in range(28)]
        takes = compute_takes(words, max_dur=10.0, min_dur=1.5, pad=0.15)
        for t in takes:
            self.assertLessEqual(t["end"] - t["start"], 10.0 + 1e-6, f"take > max: {t}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
