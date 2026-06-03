# Google Flow — notas de uso

A skill **não** integra com o Flow. Tu fazes o upload e colas os prompts. Estas notas
existem para a skill (e para ti) respeitarem as regras do Flow.

## Limites que moldam a skill
- **Cada take vai para um clip de no máximo ~10 segundos.** É por isso que a skill corta
  em takes ≤ 10s. Não excedas isto ou o Flow recusa o upload.
- Vídeo de referência deve estar limpo (sem respiros/silêncios longos). A skill já corta
  nas pausas, mas convém o vídeo bruto já vir com os respiros tirados.

## Fluxo manual
1. Abre o Google Flow → novo projeto.
2. Confirma que tens créditos (cada geração consome créditos).
3. Para cada take `NN`:
   - Upload de `takes/take_NN.mp4`.
   - Cola o conteúdo de `prompts/take_NN.txt`.
   - Gera.
4. Faz o download dos takes gerados.
5. Junta tudo no CapCut (ver `audio-fix.md`).

## Dicas
- Gera primeiro 1 take de teste para validar o estilo antes de gerar todos.
- Se um take não ficar bom, ajusta só o prompt desse take e regenera (não mexas nos outros).
- Mantém o mesmo preset/estilo em todos os prompts para coerência visual.
