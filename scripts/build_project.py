#!/usr/bin/env python3
"""build_project.py — pipeline completo: video -> pasta de projeto pronta para o Flow.

Passos:
  1. transcribe.py  -> words.json   (backend plugavel)
  2. cut_takes.py   -> takes.json   (takes <= 10s em pausas naturais)
  3. extract_takes  -> takes/*.mp4 + frames/*.jpg + prompts/*.txt (vazios)
  4. escreve transcript.txt, project.yaml, README.md

Depois disto, a SKILL.md trata do briefing e de preencher prompts/take_NN.txt.

Uso:
  python3 build_project.py video.mp4 [--out PROJ] [--backend elevenlabs]
          [--language pt] [--max 10] [--min 1.5] [--pad 0.15]
          [--words words.json]   # reutiliza transcricao ja feita (poupa API)
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import transcribe as T  # noqa: E402
import cut_takes as C  # noqa: E402
import extract_takes as E  # noqa: E402


def slug(name: str) -> str:
    base = os.path.splitext(os.path.basename(name))[0]
    keep = "".join(c if c.isalnum() or c in "-_" else "-" for c in base).strip("-")
    return keep.lower() or "projeto"


def write_transcript(result: dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(result.get("text", "").strip() + "\n")


def write_yaml(path: str, project: dict):
    """Escreve um project.yaml simples (sem dependencia de PyYAML)."""
    def esc(v):
        s = str(v)
        if any(c in s for c in ":#\n\"'") or s == "":
            return '"' + s.replace('"', '\\"').replace("\n", " ") + '"'
        return s

    lines = []
    lines.append(f"project: {esc(project['project'])}")
    lines.append(f"source_video: {esc(project['source_video'])}")
    lines.append(f"language: {esc(project['language'])}")
    lines.append(f"backend: {esc(project['backend'])}")
    lines.append(f"max_take_seconds: {project['max_take_seconds']}")
    lines.append("briefing:")
    lines.append("  layout: \"\"            # ex: horizontal 16:9, creator centralizado")
    lines.append("  mode: \"\"              # so-motion | overlay | misto")
    lines.append("  preset: \"\"            # ex: apple-clean")
    lines.append("  design_md: \"\"         # caminho do design.md da marca (opcional)")
    lines.append("  goal: \"\"             # objetivo do video")
    lines.append("takes:")
    for t in project["takes"]:
        lines.append(f"  - index: {t['index']}")
        lines.append(f"    start: {t['start']}")
        lines.append(f"    end: {t['end']}")
        lines.append(f"    duration: {t['duration']}")
        lines.append(f"    mode: \"\"           # so-motion | overlay (preenchido no briefing)")
        lines.append(f"    text: {esc(t['text'])}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


README = """# {project}

Projeto gerado pela skill **motion-takes** a partir de `{video}`.

## Estrutura
- `takes/`      — clips de video cortados (<= {max}s), prontos para upload no Google Flow
- `frames/`     — 1o frame de cada take (referencia visual)
- `prompts/`    — 1 prompt de motion por take (preenchido pela skill)
- `transcript.txt` — transcricao completa
- `words.json`  — transcricao com timestamps por palavra
- `takes.json`  — mapa dos takes (tempos + texto)
- `project.yaml`— briefing + mapa dos takes

## Como usar no Google Flow (manual)
1. Abre o Google Flow e cria um novo projeto.
2. Para cada take: faz upload de `takes/take_NN.mp4` e cola o prompt de `prompts/take_NN.txt`.
3. Gera. Repete para todos os takes.
4. Junta os takes gerados no CapCut. Se o audio gerado bugar, poe o audio
   ORIGINAL por baixo e silencia o audio do take gerado (ver references/audio-fix.md).

{count} takes gerados.
"""


def build(args) -> dict:
    out_dir = args.out or slug(args.video)
    os.makedirs(out_dir, exist_ok=True)

    words_path = os.path.join(out_dir, "words.json")
    takes_path = os.path.join(out_dir, "takes.json")

    # 1. transcricao (ou reutilizar)
    if args.words:
        print(f"[build] a reutilizar transcricao: {args.words}")
        with open(args.words, "r", encoding="utf-8") as f:
            result = json.load(f)
    else:
        result = T.transcribe(args.video, args.backend, args.language or None)
    with open(words_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    write_transcript(result, os.path.join(out_dir, "transcript.txt"))

    # 2. corte
    takes = C.compute_takes(result["words"], args.max_dur, args.min_dur, args.pad)
    if not takes:
        raise RuntimeError("Nenhum take gerado (transcricao vazia?).")
    with open(takes_path, "w", encoding="utf-8") as f:
        json.dump({"count": len(takes), "takes": takes}, f, ensure_ascii=False, indent=2)
    print(f"[build] {len(takes)} takes")

    # 3. extracao
    E.extract(args.video, takes_path, out_dir, reencode=not args.copy)

    # 4. metadados
    project = {
        "project": slug(args.video),
        "source_video": os.path.abspath(args.video),
        "language": result.get("language", args.language or ""),
        "backend": "reused" if args.words else args.backend,
        "max_take_seconds": args.max_dur,
        "takes": takes,
    }
    write_yaml(os.path.join(out_dir, "project.yaml"), project)
    with open(os.path.join(out_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(README.format(project=project["project"], video=os.path.basename(args.video),
                              max=args.max_dur, count=len(takes)))

    print(f"[build] projeto pronto em: {os.path.abspath(out_dir)}")
    return {"out_dir": out_dir, "takes": takes}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Pipeline video -> projeto de takes para o Flow.")
    ap.add_argument("video")
    ap.add_argument("--out", default=None, help="pasta do projeto (default: nome do video)")
    ap.add_argument("--backend", default=os.environ.get("MT_BACKEND", "elevenlabs"),
                    choices=list(T.BACKENDS))
    ap.add_argument("--language", default=os.environ.get("MT_LANGUAGE", "pt"))
    ap.add_argument("--max", type=float, default=10.0, dest="max_dur")
    ap.add_argument("--min", type=float, default=1.5, dest="min_dur")
    ap.add_argument("--pad", type=float, default=0.15)
    ap.add_argument("--words", default=None, help="words.json existente (salta a transcricao)")
    ap.add_argument("--copy", action="store_true", help="stream-copy em vez de re-encode")
    args = ap.parse_args(argv)
    try:
        build(args)
    except (RuntimeError, FileNotFoundError) as e:
        print(f"[erro] {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
