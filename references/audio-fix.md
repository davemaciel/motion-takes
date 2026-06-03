# Corrigir o áudio (CapCut)

O motion gerado pelo Flow costuma trazer o **áudio "bugado"**. Solução simples: usar o
áudio ORIGINAL por baixo e silenciar o áudio do take gerado.

## Passo a passo
1. No CapCut, importa os takes gerados (download do Flow) e o **vídeo original** (ou o
   áudio original).
2. Para cada take gerado:
   - Coloca o **vídeo gerado** na pista de cima.
   - Coloca o **áudio original** na pista de baixo, alinhado.
   - **Silencia** (mute) o áudio da pista de cima (o take gerado).
3. Alinha pelo início da fala de cada take (os cortes da skill respeitam as pausas, por
   isso o alinhamento é direto).
4. Exporta.

## Porquê funciona
A skill cortou os takes exatamente nos limites de fala do vídeo original, por isso o
áudio original encaixa no vídeo gerado sem desfasamento percetível.

## Dica
Se notares micro-desfasamento, ajusta o áudio original alguns frames. O `transcript.txt`
e os tempos em `takes.json` ajudam a saber onde cada take começa/acaba.
