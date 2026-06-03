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
- **Abre TODOS os `frames/*.jpg`** e, para cada take, anota: onde está o rosto, onde estão
  as mãos, se há logos/boné/texto no frame, que **zonas estão livres** (laterais, topo,
  fundo), a direção da luz e a profundidade. Isto decide as safe zones dos prompts.
- Resume em 1 frase o tema do vídeo e o objetivo aparente.
- **Lê `references/prompt-craft.md` antes de escrever qualquer prompt.** É o que separa um
  resultado cinematográfico de "texto chapado com emoji".

### 3. Briefing (perguntas — UMA de cada vez)
Faz estas perguntas ao utilizador, uma a uma, e regista as respostas no `project.yaml`
(secção `briefing`). Oferece sempre um default sensato:

1. **Layout** do vídeo final (ex.: horizontal 16:9, creator centralizado).
2. **Modo por take** (classificação de risco — ver `references/prompt-craft.md`):
   - `overlay` (motion sobre o creator) — só para takes de **baixo risco** (luz/linhas/
     partículas nas laterais/fundo).
   - `motion-plate` (cena gerada **sem pessoa**, composta depois no CapCut) — para o take
     **herói** e qualquer take de **alto risco**: texto grande, logos, ou elementos perto
     do rosto/mãos. Mais controlado e profissional.
   - Em geral será `misto`. Decidam por take.
3. **Estilo / preset**: lista os ficheiros de `presets/` (ex.: `apple-clean`). O
   utilizador escolhe um, ou indica um `design.md` próprio da marca.
4. **design.md** da marca (opcional): se existir, lê-o e respeita paleta, tipografia
   e regras de uso.
5. **Objetivo** do vídeo (ex.: vender uma skill, ensinar, hook de YouTube).

Se o utilizador pedir para a IA decidir tudo, escolhe defaults coerentes e segue.

### 4. Escrever os prompts (um por take)
**Lê `references/prompt-craft.md` primeiro.** Para **cada** take, escreve um prompt rico em
`prompts/take_NN.txt` usando o template do modo do take:
- `overlay` → `templates/flow-overlay-prompt.md`
- `motion-plate` → `templates/flow-motion-plate-prompt.md`

Cada prompt DEVE ter (senão fica genérico):
- **Uma metáfora visual concreta** ligada à frase do take — **nunca** só texto/legenda.
- **SHOT** (lente + câmara), **LIGHT**, **MATERIALS/RENDER** — não só "minimalista".
- **2–4 beats de tempo** dentro do take (entra → destaca → sai).
- **Paleta exata** (hex) do preset/`design.md`, máx 1 acento forte.
- **Safe zones** + preservação do creator (modo overlay): nada sobre rosto/olhos/boca/mãos;
  proíbe espelhar/inverter a cena.
- O **negative prompt** por defeito (ver `prompt-craft.md`).

**Texto exato é frágil no Veo** (espelha, troca letras). NÃO peças texto crítico (número de
oferta, preço, CTA) ao modelo — gera só a animação/metáfora e diz ao utilizador para pôr o
texto no CapCut. A **watermark** do Flow é da plataforma, não do prompt.

Antes de gravar cada prompt, corre o **checklist anti-genérico** de `prompt-craft.md`. Se
falhar, reescreve. Atualiza o `project.yaml`: `mode` de cada take + a secção `briefing`.

### 5. Entregar
Diz ao utilizador, em resumo:
- quantos takes, qual o **modo** de cada um (overlay vs motion-plate), onde está a pasta;
- **gera 1 take piloto** (o herói) e, se quiser, 2 variantes A/B, antes de gerar tudo;
- no Google Flow: overlay → upload de `takes/take_NN.mp4`; motion-plate → gera a cena sem
  pessoa. Cola `prompts/take_NN.txt`. Sobe a imagem de referência quando fizer sentido.
- junta no CapCut: compõe os motion-plates, **adiciona o texto crítico** e põe o **áudio
  original** por baixo (ver `references/audio-fix.md`). Corta/cobre a watermark se houver.

## Ajustes finos (2ª passagem)
Se o utilizador quiser "mais denso / mais zoom / trocar cenário / virar avatar", **não
voltes a cortar** — basta reescrever os `prompts/take_NN.txt` afetados com a nova direção
e pedir-lhe para regenerar esses takes no Flow.

## Re-cortes
Se os cortes não agradarem, ajusta `--max`, `--min` (take mínimo) ou `--pad` e volta a
correr `build_project.py` com `--words` (reutiliza a transcrição, não gasta API).

## Referências
- `references/prompt-craft.md` — **como escrever prompts ricos e anti-genéricos (lê 1º)**.
- `references/google-flow.md` — limites e fluxo do Flow.
- `references/audio-fix.md` — corrigir áudio no CapCut.
- `references/install.md` — instalar dependências (Linux/macOS/Windows).
- `templates/flow-overlay-prompt.md` — prompt de overlay (motion sobre o creator).
- `templates/flow-motion-plate-prompt.md` — prompt de motion plate (sem pessoa, p/ compor).
- `templates/design.md` — modelo de brandbook.
- `DESIGN.md` — arquitetura da skill.
