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
