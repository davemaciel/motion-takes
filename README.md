# motion-takes

Skill que transforma um vídeo bruto de creator em **takes prontos para o Google Flow**
+ um **prompt de motion por take**. Funciona no **GitHub Copilot CLI** e no **Claude
Code** (mesmo formato `SKILL.md`). Inspirada no fluxo "cortar o vídeo em takes de 10s e
gerar prompts", mas construída do zero e aberta.

> A skill **só corta os takes e escreve os prompts**. Não gera motion nem faz upload —
> isso é manual, no Google Flow. O design foi essa escolha.

## O que faz
1. Transcreve o vídeo com timestamps por palavra (ElevenLabs / OpenAI / Whisper local).
2. Corta em takes **≤ 10s nas pausas naturais** (nunca parte a fala).
3. Extrai `takes/*.mp4` + `frames/*.jpg` e cria `prompts/*.txt` (vazios).
4. Faz um **briefing** de arte (layout, overlay vs só-motion, preset/design.md, objetivo).
5. Escreve **1 prompt de Flow por take**.

## Início rápido
```bash
export ELEVENLABS_API_KEY="..."        # ou OPENAI_API_KEY (+ --backend openai)
python3 scripts/build_project.py "meu_video.mp4" --out projeto --language pt
```
Depois, no Copilot CLI (ou Claude Code), é só pedir: *"corta este vídeo em takes pro
Flow"* — o `SKILL.md` guia o resto (briefing + prompts).

## Ficheiros
- `SKILL.md` — instruções que o agente (Copilot CLI / Claude Code) segue.
- `scripts/` — `build_project.py` (pipeline), `transcribe.py`, `cut_takes.py`, `extract_takes.py`.
- `presets/` — estilos de motion (`apple-clean`, `bold-tech`).
- `templates/` — `flow-prompt.md`, `design.md` (brandbook).
- `references/` — `install.md`, `google-flow.md`, `audio-fix.md`.
- `tests/` — testes do algoritmo de corte (`python3 -m unittest discover tests`).
- `DESIGN.md` — arquitetura.

## Testes
```bash
python3 -m unittest discover -s tests -v
```

## Instalar
Copia a pasta para `~/.copilot/skills/` (Copilot CLI) **ou** `~/.claude/skills/` (Claude
Code) — ou para `<projeto>/.github/skills/` por projeto. Ver `references/install.md` para
dependências (ffmpeg, Python, backends) e detalhes de descoberta.
