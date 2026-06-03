# Google Flow + Gemini Omni Flash — notas de uso

A skill gera os prompts; tu fazes o upload no Flow e geras. Estas notas otimizam para o
**Gemini Omni Flash** (modelo de vídeo do Flow, anunciado no Google I/O 2026).

## O que é o Omni Flash (e porque muda o jogo)
- Modelo **multimodal**: aceita **texto + imagem + áudio + vídeo** como input e produz
  **vídeo com áudio** (até ~10s, qualidade 4k-class).
- **Edita footage real** preservando o sujeito -> ideal para o modo **overlay** (sobes o
  teu take e ele mantem-te, mudando só o que pedires).
- **Edição conversacional multi-turn**: refinas por instruções cirúrgicas ("mesma cena,
  muda só X, preserva Y"), com memória de personagem/estilo entre edições.
- **Renderização de texto exato** melhorou mas **ainda falha** (pode trocar/espelhar
  letras). Para texto crítico legível -> pós-produção.
- **Watermark SynthID**: TODO output do Omni leva SynthID e **não é removível** (nem por
  prompt nem por export). Planeia o enquadramento/composição contando com ela.

## Estrutura de prompt que o Omni prefere (brief de produção)
Ordem oficial recomendada (a skill já segue isto nos templates):
1. **Frame / shot** - wide, close-up, over-the-shoulder, macro, locked-off.
2. **Câmara** - push-in, orbit, tilt, dolly, handheld, "one continuous shot".
3. **Linguagem visual** - estilo + luz + local juntos ("photorealistic, warm desk-lamp
   light, dark tabletop").
4. **Ação** - quem/o que se move e **o que tem de ficar estável**.
5. **Texto** - palavras exatas + onde aparecem + se é permitido texto extra ("no
   subtitles, no logos").
6. **Áudio** - room ambience / música / SFX / nada ("natural room ambience only").

## Como subir os inputs (multimodal) por modo
**Overlay (manter o creator):**
- Input de **vídeo**: takes/take_NN.mp4.
- (Opcional) **áudio original** do take -> ajuda a manter a voz em sync e reduz áudio bugado.
- (Opcional) **imagem de referência** de estilo (preset/brand).
- Prompt: prompts/take_NN.txt (versão overlay, com safe zones).

**Motion-plate (cena sem pessoa, para compor depois):**
- **Não** subas o teu vídeo (ou sobe só uma imagem de referência de estilo/marca).
- Prompt: prompts/take_NN.txt (versão plate).
- Compor o creator por cima no CapCut.

## Fluxo manual
1. Abre o Google Flow -> novo projeto. Confirma créditos.
2. **Gera 1 take piloto** (o herói) para validar o look. Se quiseres, 2 variantes A/B.
3. Para cada take NN: sobe os inputs do modo + cola prompts/take_NN.txt + gera.
4. Para afinar, usa **edição conversacional**: "mesma cena, mas <muda só isto>, preserva o
   resto" - não reescrevas o prompt todo.
5. Download dos takes -> junta no CapCut (ver audio-fix.md); adiciona o **texto crítico**
   e o **áudio original**; corta/enquadra contando com a watermark SynthID.

## Dicas
- Mantém o mesmo preset/estilo (e paleta hex) em todos os prompts para coerência.
- Se um take não ficar bom, ajusta só esse (overlay) ou regenera o plate desse take.
- Takes <=10s por design da skill - não excedas o limite do Omni.
