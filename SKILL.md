---
name: motion-takes
description: >-
  Use when the user wants to turn a raw talking-head/creator video into "takes"
  for Google Flow motion design. Transcribes the video, cuts it into clips of up
  to 10 seconds at natural speech pauses (never mid-sentence), extracts each take
  plus a preview frame, runs a short art-direction briefing, and writes one Google
  Flow motion prompt per take. It does NOT generate the motion and does NOT upload
  to Flow — the user uploads the takes manually and pastes the prompts. Trigger on
  requests like "corta este vídeo em takes", "gera os prompts pro Flow", "skill de
  edição de motion", "cut my video for Google Flow".
---

# motion-takes

Transforma um vídeo bruto (creator a falar para a câmara) numa pasta de projeto
pronta para o **Google Flow**: takes curtos cortados nas pausas certas + um prompt
de motion por take. **A skill só corta e escreve prompts. Não gera motion nem faz
upload** — isso é manual, no Flow.

## O que esta skill faz e o que NÃO faz

| Faz | Não faz |
|-----|---------|
| Transcreve com timestamps por palavra | Gerar o motion/vídeo final |
| Corta em takes ≤ 10s nas pausas (sem partir a fala) | Fazer upload automático pro Flow |
| Extrai `takes/*.mp4` + `frames/*.jpg` | Editar no CapCut |
| Faz briefing de arte | Decidir sozinha sem confirmar o briefing |
| Escreve `prompts/take_NN.txt` | — |

## Pré-requisitos

- `ffmpeg` + `ffprobe` no PATH.
- Backend de transcrição (escolhe um):
  - **ElevenLabs** (padrão): `export ELEVENLABS_API_KEY=...`
  - **OpenAI**: `export OPENAI_API_KEY=...` e `--backend openai`
  - **Whisper local** (offline): `pip install faster-whisper` e `--backend whisper`
- Python 3.9+ (os scripts de API usam só a stdlib).

`SKILL_DIR` = a pasta desta skill (onde está este ficheiro).

## Fluxo (segue por esta ordem)

### 1. Construir o projeto de takes
Corre o pipeline. Substitui `<video>` pelo caminho do vídeo do utilizador.

```bash
python3 "$SKILL_DIR/scripts/build_project.py" "<video>" \
  --out "<pasta_projeto>" --backend elevenlabs --language pt --max 10
```

Dicas:
- Sem `--out`, usa o nome do vídeo.
- Para **não gastar API** ao re-testar cortes, reutiliza a transcrição:
  `--words "<pasta_projeto>/words.json"`.
- Se a transcrição falhar por falta de key, diz ao utilizador qual env var definir,
  ou troca de `--backend`.

Isto cria: `takes/`, `frames/`, `prompts/` (vazios), `transcript.txt`, `words.json`,
`takes.json`, `project.yaml`, `README.md`.

### 2. Ler e entender o contexto
- Lê `transcript.txt` (o que o creator diz) e `takes.json` (tempos + texto de cada take).
- Olha 1–2 `frames/*.jpg` se precisares de contexto visual (cenário, enquadramento).
- Resume em 1 frase o tema do vídeo e o objetivo aparente.

### 3. Briefing (perguntas — UMA de cada vez)
Faz estas perguntas ao utilizador, uma a uma, e regista as respostas no `project.yaml`
(secção `briefing`). Oferece sempre um default sensato:

1. **Layout** do vídeo final (ex.: horizontal 16:9, creator centralizado).
2. **Modo dos takes**: `só-motion`, `overlay` (motion sobreposto ao creator) ou
   `misto` (uns só-motion, outros overlay). Se `misto`, decidam por take.
3. **Estilo / preset**: lista os ficheiros de `presets/` (ex.: `apple-clean`). O
   utilizador escolhe um, ou indica um `design.md` próprio da marca.
4. **design.md** da marca (opcional): se existir, lê-o e respeita paleta, tipografia
   e regras de uso.
5. **Objetivo** do vídeo (ex.: vender uma skill, ensinar, hook de YouTube).

Se o utilizador pedir para a IA decidir tudo, escolhe defaults coerentes e segue.

### 4. Escrever os prompts (um por take)
Para **cada** take, escreve um prompt de Google Flow em `prompts/take_NN.txt` usando:
- o **texto do take** (o que é dito nesse trecho) → o motion deve ilustrar isso;
- o **preset** escolhido (lê `presets/<nome>.md`) + o `design.md` se existir;
- o **modo** do take (só-motion vs overlay);
- a estrutura recomendada em `templates/flow-prompt.md`.

Regras dos prompts:
- 1 prompt = 1 take. Escreve para o **clip específico** (duração real do take).
- Descreve elementos que reforcem a fala (ex.: ícone de código quando ele diz "código").
- Em modo `overlay`, deixa claro que o creator continua no frame e o motion entra
  por cima (cantos, topo, laterais), sem tapar o rosto.
- Em modo `só-motion`, descreve a cena 100% gerada.
- Mantém coerência visual entre takes (mesma paleta/estilo do preset/design.md).
- Português ou inglês conforme a preferência do utilizador (Flow aceita ambos).

Atualiza o `project.yaml`: preenche `mode` de cada take e a secção `briefing`.

### 5. Entregar
Diz ao utilizador, em resumo:
- quantos takes, onde está a pasta;
- que abra o Google Flow, faça upload de `takes/take_NN.mp4` e cole `prompts/take_NN.txt`;
- que junte tudo no CapCut e, se o áudio gerado bugar, ponha o áudio original por baixo
  (ver `references/audio-fix.md`).

## Ajustes finos (2ª passagem)
Se o utilizador quiser "mais denso / mais zoom / trocar cenário / virar avatar", **não
voltes a cortar** — basta reescrever os `prompts/take_NN.txt` afetados com a nova direção
e pedir-lhe para regenerar esses takes no Flow.

## Re-cortes
Se os cortes não agradarem, ajusta `--max`, `--min` (take mínimo) ou `--pad` e volta a
correr `build_project.py` com `--words` (reutiliza a transcrição, não gasta API).

## Referências
- `references/google-flow.md` — limites e fluxo do Flow.
- `references/audio-fix.md` — corrigir áudio no CapCut.
- `references/install.md` — instalar dependências (Linux/macOS/Windows).
- `templates/flow-prompt.md` — anatomia de um bom prompt de Flow.
- `templates/design.md` — modelo de brandbook.
- `DESIGN.md` — arquitetura da skill.
