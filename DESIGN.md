# motion-takes — Design

## Objetivo
Skill de Claude Code que pega num vídeo bruto de um creator (a falar para a câmara) e:

1. **Transcreve** com timestamps por palavra (backend plugável: ElevenLabs / OpenAI / Whisper local).
2. **Corta em takes ≤ 10s** em pausas naturais da fala — **nunca corta no meio de uma palavra/frase** (limite de 10s é imposto pelo Google Flow).
3. **Extrai** cada take em ficheiro de vídeo + um frame de pré-visualização.
4. **Entende o contexto** e faz **perguntas de briefing** (layout, overlay vs só-motion, estilo, design.md).
5. **Gera os prompts** de motion para o Google Flow, **um por take** (apenas texto — o upload dos vídeos para o Flow é feito manualmente pelo utilizador).
6. Organiza tudo numa **pasta de projeto** (`takes/`, `frames/`, `prompts/`, `transcript.txt`, `project.yaml`, `README.md`).

A skill **NÃO** gera o motion. A parte do Flow é só o prompt.

## Arquitetura (unidades isoladas)

```
vídeo ──▶ transcribe.py ──▶ words.json ──▶ cut_takes.py ──▶ takes.json ──▶ extract_takes.py ──▶ takes/*.mp4 + frames/*.jpg
                (backend plugável)        (algoritmo puro, testado)            (ffmpeg)
build_project.py  orquestra os 3 acima + cria a pasta de projeto e o project.yaml
SKILL.md          orquestra o briefing + a escrita dos prompts (feito pelo modelo)
```

### Contrato de dados normalizado
`words.json`:
```json
{ "language": "pt", "text": "…", "words": [ {"word":"olá","start":0.12,"end":0.34}, … ] }
```
Qualquer backend de transcrição produz este formato. O resto do pipeline não sabe qual backend foi usado.

### Backends de transcrição (`scripts/transcribe.py`)
- `elevenlabs` (padrão): POST `…/v1/speech-to-text`, `model_id=scribe_v1`, filtra `type==word`. Key: `ELEVENLABS_API_KEY`.
- `openai`: POST `…/v1/audio/transcriptions`, `whisper-1`, `verbose_json`, `timestamp_granularities[]=word`. Key: `OPENAI_API_KEY`.
- `whisper` (offline): `faster-whisper`, `word_timestamps=True`. Sem key.
- Seleção: flag `--backend` ou env `MT_BACKEND` (default `elevenlabs`).
- Só stdlib (urllib) para os backends de API → sem dependências extra. Whisper é import opcional.

### Algoritmo de corte (`scripts/cut_takes.py`) — o coração
Greedy "encher e recuar até à melhor pausa":
1. A partir da 1ª palavra livre, acumula palavras enquanto `fim - inicio_take ≤ MAX` (10s).
2. Dentro dessa janela, escolhe o ponto de corte com melhor *score*:
   `score = gap_depois_da_palavra*1.0 + pontuacao_final_de_frase*0.6 + (duracao_take/MAX)*0.3`
   - `gap` = silêncio até à palavra seguinte → cortar onde há pausa real.
   - bónus se a palavra termina em `. ! ?` → respeita fim de frase.
   - bónus por usar mais dos 10s → evita takes minúsculos.
   - takes abaixo de `MIN` (default 1.5s) são evitados (exceto se forçado).
3. O corte fica no **meio do silêncio** (midpoint do gap) com um pad, para não cortar fonemas nas bordas.
4. Palavra isolada > MAX (raro): emite o take e avisa.

Função pura `compute_takes(words, max_dur, min_dur, pad)` → lista de takes `{index,start,end,text}`. Testada com dados sintéticos (TDD).

### Extração (`scripts/extract_takes.py`)
Para cada take, `ffmpeg -ss start -to end` **com re-encode** (corte preciso ao frame, ao contrário do stream-copy) → `takes/take_01.mp4`. Extrai 1º frame → `frames/take_01.jpg`. Escreve também `prompts/take_01.txt` vazio (a preencher pelo modelo).

### Orquestração da skill (`SKILL.md`)
1. Corre `build_project.py <video> [--out pasta] [--max 10] [--backend …]`.
2. Lê `transcript.txt` e `takes.json`, entende o contexto.
3. Faz as perguntas de briefing (uma de cada vez): layout, modo (só-motion / overlay / misto), estilo/preset, design.md.
4. Para cada take, escreve um prompt de Google Flow em `prompts/take_NN.txt` usando o texto do take + o preset escolhido + o `design.md`.
5. Atualiza `project.yaml` com as respostas e o mapa de takes.

### Presets e design.md
- `presets/*.md`: estilos de motion (ex.: `apple-clean`). Definem direção de arte, ritmo, tipografia, do/don't.
- `templates/design.md`: modelo de brandbook do utilizador (paleta, fontes, layout).
- `templates/flow-overlay-prompt.md` / `templates/flow-motion-plate-prompt.md`: estrutura recomendada de um bom prompt de Flow.
- `references/prompt-craft.md`: guia anti-genérico para prompts ricos.

## Portabilidade
- Scripts em Python stdlib + ffmpeg. Funciona em Linux e macOS. Notas de Windows em `references/`.
- Skill copiável para `~/.claude/skills/motion-takes/` (global) ou `<projeto>/.claude/skills/` (por projeto).

## Não-objetivos (YAGNI)
- Não gera motion/vídeo final.
- Não faz upload automático para o Flow (o vídeo explica que há uma 2ª etapa de automação; fica fora deste âmbito por escolha do utilizador).
- Não mexe em CapCut (a correção de áudio é manual, documentada nas referências).
