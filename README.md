# Acertijos de Halloween con QR

Cada folio lleva un acertijo y un QR por opción. Escanear una opción lleva a `docs/j.html`, que dice si se ha acertado.
Las incorrectas siempre dan susto; las correctas, con un 25 % de probabilidad (`PROB_SUSTO_ACIERTO` en `build.py`).

## Uso

1. Editar `acertijos.json` (texto, respuesta correcta, tres falsas y frase de premio).
2. Publicar la carpeta `docs/` en una dirección con HTTPS (GitHub Pages, Vercel…).
3. `python3 build.py --base https://TU-DIRECCION` genera `docs/datos.js` y `folios.html`.
4. Abrir `folios.html` en Chrome → Imprimir → A4, sin márgenes, con gráficos de fondo. Una página por acertijo.

Cambiar `--base` obliga a reimprimir (la dirección va dentro del QR). El orden de las opciones es estable entre ejecuciones.

`vendor/` lleva `segno` (generador de QR, sin dependencias) porque este equipo no tiene `pip`.

## La calavera del aula (`docs/calavera.html`)

Pantalla para el aula: en reposo está **toda negra**. Cuando el micrófono oye un alboroto o un golpe
(o, de vez en cuando, por sorpresa) aparece una calavera con un grito, dice una frase de humor negro (voz del navegador)
y se esconde otra vez. El sonido no se graba ni se envía: solo se mide el volumen. La primera vez saluda.

- Dirección: `https://freuma.github.io/halloween-qr/calavera.html` (añadir `?debug` para ver el nivel del micro).
- Abrir en Chrome, pulsar «Despertar» y aceptar el micrófono. Teclas: Espacio (despertarla ya), V (cambiar de voz),
  D (nivel), M (micrófono sí/no), +/− (sensibilidad), F (pantalla completa).
- `frases.js`: todas las frases por categoría (bienvenida, ruido, golpe, silencio, aleatoria). Las de «silencio» no se usan: el silencio no la despierta (`silencioSeg: 0` en `calavera.html`; poner 45 para reactivarlo).
- `calavera-logica.js`: cuándo habla; sin dependencias del navegador.
