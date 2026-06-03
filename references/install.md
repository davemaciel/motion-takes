# Instalação

## Dependências base
- **ffmpeg** + **ffprobe**
- **Python 3.9+**

### Linux (Debian/Ubuntu)
```bash
sudo apt update && sudo apt install -y ffmpeg python3
```

### macOS (Homebrew)
```bash
brew install ffmpeg python
```

### Windows
- Instala o ffmpeg: https://www.gyan.dev/ffmpeg/builds/ (adiciona ao PATH).
- Instala o Python: https://www.python.org/downloads/ (marca "Add to PATH").
- Corre os comandos da skill no PowerShell, trocando `python3` por `python`.

## Backend de transcrição (escolhe um)

### ElevenLabs (padrão, recomendado)
```bash
export ELEVENLABS_API_KEY="a-tua-key"
```
A skill usa o modelo `scribe_v1` (timestamps por palavra).

### OpenAI
```bash
export OPENAI_API_KEY="a-tua-key"
# e corre o build com:  --backend openai
```

### Whisper local (offline, sem key)
```bash
pip install faster-whisper        # ou: pip install --break-system-packages faster-whisper
# e corre o build com:  --backend whisper
# modelo configurável: export MT_WHISPER_MODEL=small   (tiny|base|small|medium|large-v3)
```

Os backends de API (ElevenLabs/OpenAI) **não precisam de pip** — usam só a stdlib.

## Variáveis úteis
- `MT_BACKEND` — backend padrão (`elevenlabs`|`openai`|`whisper`).
- `MT_LANGUAGE` — idioma padrão (ex.: `pt`; vazio = auto).
- `MT_WHISPER_MODEL` — tamanho do modelo Whisper local.

## Instalar a skill (onde colocar a pasta)

Esta skill funciona no **GitHub Copilot CLI** e no **Claude Code** — o formato `SKILL.md`
é o mesmo. Muda só a pasta onde a colocas.

### GitHub Copilot CLI (o que estás a usar)
O Copilot CLI faz scan destas localizações:
- **Pessoal:** `~/.copilot/skills/`  ← **recomendado** · também lê `~/.claude/skills/` e `~/.agents/skills/`
- **Por projeto:** `<projeto>/.github/skills/`, `<projeto>/.agents/skills/` ou `<projeto>/.claude/skills/`
- **Manual:** dentro do CLI, `/skills add <caminho>`

Instalar (global):
```bash
mkdir -p ~/.copilot/skills
cp -r motion-takes ~/.copilot/skills/
```
Confirma com `/skills` (lista) ou `/env` dentro do Copilot CLI. Depois é só pedir:
"corta este vídeo em takes pro Flow: caminho/do/video.mp4".

### Claude Code
- **Global:** copia `motion-takes/` para `~/.claude/skills/`.
- **Por projeto:** copia para `<projeto>/.claude/skills/`.

O agente descobre a skill pelo `SKILL.md` em qualquer um dos casos.
