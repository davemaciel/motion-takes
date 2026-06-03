#!/usr/bin/env python3
"""extract_takes.py — extrai cada take em ficheiro de video + frame de preview.

Le takes.json (saida de cut_takes.py) e o video original. Para cada take:
  * corta com ffmpeg (RE-ENCODE -> corte preciso ao frame, nao parte a fala)
  * gera takes/take_NN.mp4
  * gera frames/take_NN.jpg (primeiro frame do take)
  * cria prompts/take_NN.txt vazio (a preencher pela skill)

Uso:
  python3 extract_takes.py video.mp4 takes.json --out PROJ_DIR
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys


def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError("ffmpeg falhou:\n" + " ".join(cmd) + "\n" +
                           p.stderr.decode("utf-8", "ignore")[-800:])


def extract(video: str, takes_json: str, out_dir: str, reencode: bool = True):
    with open(takes_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    takes = data.get("takes", data) if isinstance(data, dict) else data

    takes_dir = os.path.join(out_dir, "takes")
    frames_dir = os.path.join(out_dir, "frames")
    prompts_dir = os.path.join(out_dir, "prompts")
    for d in (takes_dir, frames_dir, prompts_dir):
        os.makedirs(d, exist_ok=True)

    made = []
    for t in takes:
        nn = f"{t['index']:02d}"
        start, end = float(t["start"]), float(t["end"])
        dur = max(0.05, end - start)
        clip = os.path.join(takes_dir, f"take_{nn}.mp4")
        frame = os.path.join(frames_dir, f"take_{nn}.jpg")
        prompt = os.path.join(prompts_dir, f"take_{nn}.txt")

        if reencode:
            cmd = ["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i", video,
                   "-t", f"{dur:.3f}",
                   "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                   "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                   "-movflags", "+faststart", clip]
        else:
            cmd = ["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i", video,
                   "-t", f"{dur:.3f}", "-c", "copy", clip]
        run(cmd)

        # primeiro frame do take
        run(["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i", video,
             "-frames:v", "1", "-q:v", "3", frame])

        if not os.path.exists(prompt):
            with open(prompt, "w", encoding="utf-8") as f:
                f.write("")  # preenchido pela skill (SKILL.md)
        made.append((nn, clip, t.get("text", "")))
        print(f"  take {nn}  {start:6.2f}-{end:6.2f}s -> {os.path.relpath(clip, out_dir)}")

    return made


def main(argv=None):
    ap = argparse.ArgumentParser(description="Extrai takes de video com ffmpeg.")
    ap.add_argument("video")
    ap.add_argument("takes_json")
    ap.add_argument("--out", required=True, help="pasta do projeto")
    ap.add_argument("--copy", action="store_true",
                    help="usar stream-copy (rapido, mas corte menos preciso)")
    args = ap.parse_args(argv)

    made = extract(args.video, args.takes_json, args.out, reencode=not args.copy)
    print(f"[extract_takes] {len(made)} takes -> {os.path.join(args.out, 'takes')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
