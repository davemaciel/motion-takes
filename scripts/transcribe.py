#!/usr/bin/env python3
"""transcribe.py — transcreve um video/audio em PALAVRAS com timestamps.

Backend plugavel (--backend ou env MT_BACKEND), saida normalizada:
  {"language": "...", "text": "...", "words": [{"word","start","end"}, ...]}

Backends:
  elevenlabs (default)  ELEVENLABS_API_KEY   modelo scribe_v1
  openai                OPENAI_API_KEY       modelo whisper-1 (verbose_json, word ts)
  whisper               (offline)            faster-whisper, sem key

So usa a stdlib para os backends de API. Whisper local e import opcional.

Uso:
  python3 transcribe.py input.mp4 -o words.json [--backend elevenlabs] [--language pt]
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import subprocess
import sys
import tempfile
import urllib.request
import uuid

EL_URL = "https://api.elevenlabs.io/v1/speech-to-text"
OPENAI_URL = "https://api.openai.com/v1/audio/transcriptions"


# ----------------------------------------------------------------------------
# Audio: extrair faixa de audio comprimida (mp3 mono 16k) do video de entrada.
# Reduz upload e e aceite por todas as APIs. Devolve caminho temporario.
# ----------------------------------------------------------------------------
def extract_audio(input_path: str) -> str:
    out = os.path.join(tempfile.gettempdir(), f"mt_audio_{uuid.uuid4().hex}.mp3")
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vn", "-ac", "1", "-ar", "16000", "-b:a", "64k", out,
    ]
    proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if proc.returncode != 0 or not os.path.exists(out):
        raise RuntimeError("ffmpeg falhou a extrair audio:\n" + proc.stderr.decode("utf-8", "ignore")[-800:])
    return out


# ----------------------------------------------------------------------------
# multipart/form-data minimal (sem dependencias externas)
# ----------------------------------------------------------------------------
def _multipart(fields: dict, file_field: str, file_path: str) -> tuple[bytes, str]:
    boundary = "----MTBoundary" + uuid.uuid4().hex
    crlf = b"\r\n"
    body = bytearray()
    for k, v in fields.items():
        body += b"--" + boundary.encode() + crlf
        body += f'Content-Disposition: form-data; name="{k}"'.encode() + crlf + crlf
        body += str(v).encode() + crlf
    fname = os.path.basename(file_path)
    ctype = mimetypes.guess_type(fname)[0] or "application/octet-stream"
    with open(file_path, "rb") as f:
        data = f.read()
    body += b"--" + boundary.encode() + crlf
    body += f'Content-Disposition: form-data; name="{file_field}"; filename="{fname}"'.encode() + crlf
    body += f"Content-Type: {ctype}".encode() + crlf + crlf
    body += data + crlf
    body += b"--" + boundary.encode() + b"--" + crlf
    return bytes(body), boundary


def _post_multipart(url: str, headers: dict, fields: dict, file_field: str, file_path: str) -> dict:
    body, boundary = _multipart(fields, file_field, file_path)
    headers = dict(headers)
    headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")[:1000]
        raise RuntimeError(f"HTTP {e.code} de {url}:\n{detail}")


# ----------------------------------------------------------------------------
# Backends
# ----------------------------------------------------------------------------
def transcribe_elevenlabs(audio_path: str, language: str | None) -> dict:
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise RuntimeError("Falta ELEVENLABS_API_KEY no ambiente.")
    fields = {"model_id": "scribe_v1"}
    if language:
        fields["language_code"] = language
    data = _post_multipart(EL_URL, {"xi-api-key": key}, fields, "file", audio_path)
    words = []
    for w in data.get("words", []):
        if w.get("type", "word") != "word":
            continue
        words.append({
            "word": w.get("text", "").strip(),
            "start": float(w.get("start", 0.0)),
            "end": float(w.get("end", 0.0)),
        })
    return {"language": data.get("language_code", language or ""),
            "text": data.get("text", ""), "words": words}


def transcribe_openai(audio_path: str, language: str | None) -> dict:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("Falta OPENAI_API_KEY no ambiente.")
    fields = {
        "model": "whisper-1",
        "response_format": "verbose_json",
        "timestamp_granularities[]": "word",
    }
    if language:
        fields["language"] = language
    data = _post_multipart(OPENAI_URL, {"Authorization": f"Bearer {key}"}, fields, "file", audio_path)
    words = [{"word": w["word"].strip(), "start": float(w["start"]), "end": float(w["end"])}
             for w in data.get("words", [])]
    return {"language": data.get("language", language or ""),
            "text": data.get("text", ""), "words": words}


def transcribe_whisper(audio_path: str, language: str | None) -> dict:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise RuntimeError(
            "faster-whisper nao instalado. Instala com:\n"
            "  pip install faster-whisper   (ou: pip install --break-system-packages faster-whisper)\n"
            "Ou usa --backend elevenlabs / openai.")
    model_size = os.environ.get("MT_WHISPER_MODEL", "base")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(audio_path, language=language, word_timestamps=True)
    words, text_parts = [], []
    for seg in segments:
        text_parts.append(seg.text)
        for w in (seg.words or []):
            words.append({"word": w.word.strip(), "start": float(w.start), "end": float(w.end)})
    return {"language": info.language, "text": "".join(text_parts).strip(), "words": words}


BACKENDS = {
    "elevenlabs": transcribe_elevenlabs,
    "openai": transcribe_openai,
    "whisper": transcribe_whisper,
}


def transcribe(input_path: str, backend: str, language: str | None) -> dict:
    fn = BACKENDS.get(backend)
    if not fn:
        raise RuntimeError(f"Backend desconhecido: {backend}. Opcoes: {', '.join(BACKENDS)}")
    audio = extract_audio(input_path)
    try:
        result = fn(audio, language)
    finally:
        try:
            os.remove(audio)
        except OSError:
            pass
    if not result["words"]:
        raise RuntimeError("Transcricao sem palavras/timestamps. Verifica o audio do video e a key da API.")
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Transcreve video em palavras com timestamps.")
    ap.add_argument("input", help="video ou audio de entrada")
    ap.add_argument("-o", "--out", default="words.json")
    ap.add_argument("--backend", default=os.environ.get("MT_BACKEND", "elevenlabs"),
                    choices=list(BACKENDS))
    ap.add_argument("--language", default=os.environ.get("MT_LANGUAGE", "pt"),
                    help="codigo de idioma (ex: pt). Vazio = auto")
    args = ap.parse_args(argv)

    lang = args.language or None
    print(f"[transcribe] backend={args.backend} language={lang or 'auto'} input={args.input}")
    try:
        result = transcribe(args.input, args.backend, lang)
    except RuntimeError as e:
        print(f"[erro] {e}", file=sys.stderr)
        return 1
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"[transcribe] {len(result['words'])} palavras -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
