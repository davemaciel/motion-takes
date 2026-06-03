# Áudio (Gemini Omni + CapCut)

O **Gemini Omni gera áudio** junto com o vídeo. Para um creator a falar, há duas formas de
manter a voz certa:

## Opção A — alimentar o áudio original no Omni (preferida)
Ao gerar o take, **sobe também o áudio original** do clip como input multimodal e pede no
prompt: `keep the original creator voice in sync, natural room ambience only, no music`.
Assim o Omni tende a preservar a fala em sync. Mesmo assim, confere no editor.

## Opção B — corrigir no CapCut (à prova de bala)
Se o áudio gerado ficar "bugado", usa o **áudio original** por baixo e silencia o do take.
1. No CapCut, importa os takes gerados e o **vídeo/áudio original**.
2. Para cada take gerado:
   - Vídeo gerado na pista de cima.
   - **Áudio original** na pista de baixo, alinhado.
   - **Silencia** (mute) o áudio da pista de cima.
3. Alinha pelo início da fala de cada take (os cortes da skill respeitam as pausas).
4. Exporta.

## Porquê funciona
A skill cortou os takes exatamente nos limites de fala do original, por isso o áudio
original encaixa sem desfasamento percetível. Os tempos estão em `takes.json`.

## Nota SynthID
Todo output do Omni leva watermark **SynthID** (permanente). Enquadra/compõe contando com
ela — não há como removê-la por prompt ou export.
