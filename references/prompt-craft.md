# Prompt craft para Google Flow (Veo / Omni Flash)

Guia para escrever prompts que geram **motion design real** — não "texto chapado por
cima da pessoa". Lê isto antes de escrever os prompts dos takes.

## A regra de ouro

> Um bom prompt descreve uma **CENA com câmara, luz, material e movimento**, com **UMA
> metáfora visual** ligada ao que é dito — não uma legenda flutuante.

O modelo de vídeo é gerativo e cinematográfico. Se lhe deres pouca informação, ele
preenche com o cliché mais provável: tela vazia, uma palavra grande e um emoji de
brilho. Foi exatamente isso que correu mal antes. Detalhe = controlo.

## O que o Veo/Flow faz bem e o que faz mal

| Faz bem (usa o Flow para isto) | Faz mal (resolve noutro sítio) |
|---|---|
| Luz volumétrica, partículas, fumo, vidro, líquidos | **Texto legível exato** (espelha, troca letras) |
| Objetos 3D, parallax, profundidade, reflexos | **Logos / marcas** fiéis |
| Câmara cinematográfica (dolly, órbita, macro) | **Mãos e rostos em close** (deforma) |
| Transformações e transições de material | Orientação exata da cena (às vezes espelha tudo) |
| Ambientes e fundos gerados | UI/numeros precisos |

### Consequência prática (IMPORTANTE)
- **Texto crítico/legível** (número de oferta, preço, CTA): NÃO confies no Flow. Gera só
  a **animação/metáfora** e adiciona o texto final no **CapCut / After Effects**.
- **Identidade do creator** (rosto, boné, t-shirt, expressão): video-to-video pode
  espelhar ou deformar. Para resultado profissional, considera o modo **motion plate**
  (gerar o motion sem a pessoa) e compor por cima no editor.
- **Watermark do Flow**: a marca d'água no canto é da **plataforma/plano de exportação**,
  não do prompt — negative prompt não a tira. Exporta no plano que remove, ou corta/cobre
  no editor.

## Os dois modos (escolhe por take)

### A) Overlay direto (rápido, experimental)
Sobe o `take_NN.mp4` como plate-fonte e pedes ao Flow para **manter o creator** e
acrescentar motion só nas **zonas livres**. Risco: pode espelhar/deformar. Bom para
takes simples (luzes, linhas, partículas nas laterais/fundo).
→ Template: `templates/flow-overlay-prompt.md`

### B) Motion plate (controlado, profissional)
Geras a cena de motion **sem pessoa** (fundo transparente/preto ou cena cheia) e
**compões** sobre o creator no CapCut. Dá o look rico de keynote sem arriscar a cara do
creator. Recomendado para o take "herói" e para qualquer take com texto/objeto perto do
rosto.
→ Template: `templates/flow-motion-plate-prompt.md`

## Classificação de risco (decide o modo)

Para cada take, classifica:
- **Baixo** → overlay direto OK. Motion só em luz/linhas/partículas/HUD nas laterais/fundo.
- **Médio** → overlay possível, mas testa 1 primeiro. Objetos 3D perto do creator.
- **Alto** → **usa motion plate + composição**. Sempre que houver: texto grande exato,
  logos, elementos a cruzar rosto/mãos, ou transformação do cenário.

Texto exato e marca = **sempre** pós-produção, independentemente do modo.

## Anatomia de um prompt (campos obrigatórios)

Escreve 1 prompt por take, em **inglês** (o Flow costuma responder melhor), cobrindo:

1. **SHOT** — lente e câmara: `85mm macro`, `wide 24mm`, `slow dolly-in`, `subtle orbit`,
   `rack focus`, `locked-off`. Diz a **duração real** do take (ex.: `~6s`).
2. **LIGHT** — `soft volumetric side light`, `rim light in brand red`, `caustics`,
   `practical glints`. A luz é metade do "premium".
3. **SUBJECT / PLATE** — overlay: "keep the source creator untouched"; plate: "no person,
   full generated scene".
4. **MOTION CONCEPT** — UMA metáfora visual ligada às palavras ditas. Verbo de movimento
   concreto: *forms, assembles, shatters, dissolves into particles, unfolds, sweeps*.
   Ex.: diz "4 dias" → 4 painéis de vidro montam-se em sequência; diz "código" → linhas
   de código correm e condensam-se num ícone.
5. **MATERIALS / RENDER** — `frosted glass`, `brushed metal`, `volumetric particles`,
   `depth of field`, `subsurface glow`, `4k hyperreal`. Dá textura, mata o "flat".
6. **TYPOGRAPHY** — só se for texto não-crítico/decorativo; descreve como anima em 3D
   (`extruded letters catch a light sweep`). Texto crítico → deixa para o editor.
7. **TIMING BEATS** — 2 a 4 micro-momentos DENTRO do take (ex.: `0-1.5s … / 1.5-4s … /
   4-6s …`). Dá ritmo; evita um plano estático.
8. **GRADE / PALETTE** — cores exatas do preset/`design.md` (hex). Máx 1 acento forte.
9. **SFX** — opcional: `soft whoosh on the assemble, low sub on the reveal`.
10. **NEGATIVES** — ver abaixo.

## Hierarquia (não transformar em lista de compras)

Por ordem de prioridade dentro do prompt:
1. **Preservar o creator** (modo overlay) — regra nº1.
2. **Uma metáfora visual forte** — obrigatória.
3. **Máx 2–3 elementos secundários** — nada de 5 ideias num clip de 6s.
4. **Safe zones explícitas** — laterais (terços esq/dir), topo, fundo, profundidade atrás
   do ombro. **Nunca** sobre o rosto, boca, olhos, mãos.

Frase-tipo de safe zone (overlay):
> Keep all generated motion in the left/right thirds and the background depth behind the
> shoulders. The creator's face, eyes, mouth, hands, body silhouette, cap and shirt logo,
> and the original camera orientation must stay unchanged and never mirrored.

## Negative prompt por defeito (cola sempre)

> no flat caption-only design, no single big word over the person, no emoji, no clipart
> sparkles, no app or tool watermark, no mirrored or flipped text, no backwards letters,
> no gibberish text, no warped face, no deformed hands, no extra fingers, no changing the
> creator's appearance, no extra colors beyond the palette, no busy clutter.

## Checklist anti-genérico (corre antes de entregar cada prompt)

- [ ] Tem **uma metáfora visual concreta** (não só texto/emoji)?
- [ ] Tem **câmara, luz e material** descritos (não só "minimalista")?
- [ ] Tem **2–4 beats de tempo** dentro do take?
- [ ] Define **safe zones** e preserva o creator (se overlay)?
- [ ] Texto exato foi **removido do prompt** e marcado para pós-produção?
- [ ] Inclui o **negative prompt**?
- [ ] O conceito **liga-se à frase** dita nesse take?
Se algum falhar, reescreve.

## Fluxo recomendado de geração

1. Gera **1 take piloto** (o herói) antes de gerar todos — valida o look.
2. Para o take herói, gera **2 variantes (A/B)** e escolhe.
3. Só depois gera o resto em lote, mantendo paleta/estilo coerentes.
4. Junta no CapCut; adiciona **texto crítico** e o **áudio original** por baixo
   (ver `audio-fix.md`).
