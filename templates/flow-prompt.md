# Anatomia de um bom prompt de Google Flow (por take)

Escreve **1 prompt por take**, descrevendo só aquele clip. Estrutura recomendada:

```
[CENA / MODO] + [SUJEITO] + [ELEMENTOS DE MOTION ligados à fala] +
[ESTILO/PALETA do preset ou design.md] + [CÂMARA/RITMO] + [DURAÇÃO] + [NEGATIVOS]
```

## Campos
- **Cena / modo**:
  - `só-motion` → "Full-frame generated scene, no person."
  - `overlay` → "Keep the creator centered and untouched; motion graphics overlaid
    on edges/top/sides, never covering the face."
- **Sujeito**: o que está no frame (creator, produto, ambiente).
- **Elementos de motion**: liga ao que é DITO no take. Ex.: diz "código" →
  ícone/janela de código; diz "rápido" → snap-zoom; diz um número → contador animado.
- **Estilo/paleta**: copia a direção do preset escolhido (`presets/<nome>.md`) e/ou do
  `design.md` da marca (cores exatas, fontes, do/don't).
- **Câmara/ritmo**: zoom-in/out lento (Apple Clean) ou pushes rápidos (Bold Tech).
- **Duração**: indica a duração real do take (ex.: "~8s clip").
- **Negativos**: o que evitar (texto a mais, tapar o rosto, cores fora da paleta).

## Exemplo (overlay, Apple Clean, take diz "criei uma skill em 4 dias")
> Overlay motion graphics on the creator (centered, face untouched). A single large
> minimalist caption "4 DIAS" animates in softly from the top with ease-in-out, plus
> a thin line icon of a calendar/skill badge sliding from the right. Apple-clean
> style: off-white space, one desaturated blue accent, SF-Pro-like type, subtle depth
> blur, calm pace. ~7s clip. Avoid clutter, extra text, covering the face, extra colors.

## Boas práticas
- Mantém **coerência** entre takes: mesma paleta/estilo em todos.
- Um conceito visual por take. Não enfies 5 ideias num clip de 8s.
- Se o utilizador pedir "mais denso" depois, acrescenta elementos e mantém o estilo.
- Português ou inglês — o Flow aceita ambos; usa o que o utilizador preferir.
