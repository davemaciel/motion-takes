#!/usr/bin/env python3
"""cut_takes.py — corta uma transcricao (palavras com timestamps) em "takes"
prontos para o Google Flow (Gemini Omni Flash).

Regras:
  * Cada take dura no maximo `max_dur` segundos (default 10.0, limite do Omni/Flow).
  * Os cortes acontecem em PAUSAS naturais da fala (nunca a meio de uma palavra).
  * Prefere fim de frase (pontuacao . ! ?) e takes nem demasiado curtos.

Uso (CLI):
  python3 cut_takes.py words.json -o takes.json [--max 10] [--min 1.5] [--pad 0.15]

`words.json` aceite em dois formatos:
  {"words":[{"word":"ola","start":0.1,"end":0.4}, ...]}   ou   [ {...}, ... ]
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Dict

SENTENCE_END = (".", "!", "?", "…")


def _ends_sentence(word: str) -> bool:
    w = word.strip().strip('"\u201d\u201c\')')
    return w.endswith(SENTENCE_END)


def compute_takes(
    words: List[Dict],
    max_dur: float = 10.0,
    min_dur: float = 1.5,
    pad: float = 0.15,
) -> List[Dict]:
    """Devolve uma lista de takes: {index, start, end, text, word_start, word_end}.

    `start`/`end` ja incluem o `pad` e estao "encostados" ao meio do silencio
    entre takes, garantindo que nenhuma fronteira parte uma palavra.
    """
    words = [w for w in words if w.get("word", "").strip() != ""]
    n = len(words)
    if n == 0:
        return []

    raw = []  # pares (i_inicio, i_fim) em indices de palavra
    start_idx = 0
    while start_idx < n:
        take_start = words[start_idx]["start"]

        # maior j tal que todas as palavras [start_idx..j] cabem em max_dur
        j = start_idx
        while j + 1 < n and (words[j + 1]["end"] - take_start) <= max_dur:
            j += 1

        # escolher o melhor ponto de corte k em [start_idx..j]
        best_k = j
        best_score = float("-inf")
        for k in range(start_idx, j + 1):
            take_len = words[k]["end"] - take_start
            # evitar takes demasiado curtos, a menos que seja forcado (k == j)
            if take_len < min_dur and k < j:
                continue
            if k + 1 < n:
                gap = max(0.0, words[k + 1]["start"] - words[k]["end"])
            else:
                gap = max_dur  # fim do video: gap "infinito"
            punct = 1.0 if _ends_sentence(words[k]["word"]) else 0.0
            score = gap * 1.0 + punct * 0.6 + (take_len / max_dur) * 0.3
            if score >= best_score:
                best_score = score
                best_k = k

        raw.append((start_idx, best_k))
        start_idx = best_k + 1

    # converter indices em tempos, colocando a fronteira no meio do silencio
    takes = []
    for idx, (i0, i1) in enumerate(raw):
        w_start = words[i0]["start"]
        w_end = words[i1]["end"]

        # limite inferior: meio do silencio com a palavra anterior (ou inicio)
        if i0 - 1 >= 0:
            prev_end = words[i0 - 1]["end"]
            lower_bound = (prev_end + w_start) / 2.0
        else:
            lower_bound = 0.0
        # limite superior: meio do silencio com a palavra seguinte (ou fim)
        if i1 + 1 < n:
            next_start = words[i1 + 1]["start"]
            upper_bound = (w_end + next_start) / 2.0
        else:
            upper_bound = w_end + pad

        start = max(lower_bound, w_start - pad)
        end = min(upper_bound, w_end + pad)
        start = max(0.0, start)
        if end <= start:
            end = w_end

        # Garantir duracao <= max_dur encolhendo a expansao que esta no SILENCIO
        # (nunca corta dentro da palavra: nao passa de w_start / w_end).
        if (end - start) > max_dur:
            overshoot = (end - start) - max_dur
            # primeiro recolhe o fim ate w_end
            give_end = min(overshoot, end - w_end)
            end -= max(0.0, give_end)
            overshoot = (end - start) - max_dur
            if overshoot > 0:
                give_start = min(overshoot, w_start - start)
                start += max(0.0, give_start)

        text = " ".join(words[k]["word"].strip() for k in range(i0, i1 + 1))
        takes.append({
            "index": idx + 1,
            "start": round(start, 3),
            "end": round(end, 3),
            "duration": round(end - start, 3),
            "text": text,
        })
    return takes


def _load_words(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data.get("words", [])
    return data


def main(argv=None):
    ap = argparse.ArgumentParser(description="Corta transcricao em takes para o Google Flow (Omni).")
    ap.add_argument("words_json", help="ficheiro words.json (saida de transcribe.py)")
    ap.add_argument("-o", "--out", default="takes.json", help="ficheiro de saida")
    ap.add_argument("--max", type=float, default=10.0, dest="max_dur")
    ap.add_argument("--min", type=float, default=1.5, dest="min_dur")
    ap.add_argument("--pad", type=float, default=0.15)
    args = ap.parse_args(argv)

    words = _load_words(args.words_json)
    takes = compute_takes(words, args.max_dur, args.min_dur, args.pad)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"count": len(takes), "takes": takes}, f, ensure_ascii=False, indent=2)

    total = sum(t["duration"] for t in takes)
    print(f"[cut_takes] {len(takes)} takes, total {total:.1f}s -> {args.out}")
    for t in takes:
        preview = t["text"][:60] + ("…" if len(t["text"]) > 60 else "")
        print(f"  take {t['index']:02d}  {t['start']:6.2f}-{t['end']:6.2f}s "
              f"({t['duration']:4.1f}s)  {preview}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
