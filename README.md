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

### Modo juego: acertijo en pantalla (`calavera.html?juego`)

La pantalla enseña **su propio acertijo** (`acertijo-pantalla.json`, no es ninguno de los 10 de los folios; se pueden añadir más) con un QR por opción. Cuando alguien escanea una con el móvil, aparece la calavera:
con grito y frase burlona si falla; si acierta, dice algo a regañadientes y grita solo el 25 % de las veces.
Después cambia de acertijo (también cada 5 min si nadie contesta). Solo reacciona a los QR: ni micrófono ni sorpresas
(`?juego&micro` los añade). Teclas extra: T simula un fallo, N cambia de acertijo. El puntito verde abajo a la izquierda
indica que está conectada.

El móvil avisa a la pantalla por [ntfy.sh](https://ntfy.sh) (servicio gratuito, sin cuenta): `j.html` publica `{q, o}`
en el tema de `canal.txt` y la pantalla lo escucha. No viaja nada más. Los QR de los folios impresos **no** avisan: solo suenan los de la pantalla.
`build.py` genera `docs/pantalla.js` (textos y QR de la pantalla). Los acertijos de la pantalla llevan id 101 en adelante y no cuentan en el «n de 10» del móvil; los folios no cambian, no hay que reimprimir.
