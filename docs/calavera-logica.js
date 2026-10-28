/* Cerebro de la calavera: decide cuándo hablar a partir del volumen del aula.
   Solo recibe números (el volumen de cada instante); no oye ni guarda audio.
   Sin dependencias del navegador, para poder probarlo con Node. */
(function (raiz) {
  function Cerebro(opciones) {
    var o = {
      sensibilidad: 1,       // >1: reacciona con menos ruido
      silencioSeg: 45,       // sin ruido durante tanto tiempo -> frase de silencio (0 = no despertar por silencio)
      enfriamientoSeg: 18,   // pausa mínima tras hablar, salvo golpes
      golpeEnfriaSeg: 5,
      picoMinimo: 0.10,      // un golpe necesita al menos este pico (0-1)
      picoRelativo: 3.5,     // y superar tantas veces el pico medio de los últimos segundos
      cresta: 4.5,           // pico / volumen medio: los golpes son muy puntuales, la voz no
      muestrasRuido: 30,     // muestras altas en 3 s para contar como alboroto (a 20 Hz = 1,5 s)
      aleatoriaMinSeg: 70,
      aleatoriaMaxSeg: 160,
      calentamiento: 40      // muestras antes de empezar a reaccionar (2 s a 20 Hz)
    };
    for (var k in opciones) o[k] = opciones[k];
    this.o = o;
    this.hist = [];
    this.altos = [];
    this.prev = 0;
    this._picoLento = 0;
    this.ultimoRuido = null;
    this.ultimaHabla = -1e12;
    this.ultimoGolpe = -1e12;
    this.siguienteAleatoria = null;
    this._baseline = 0.01;
    this._n = 0;
  }

  Cerebro.prototype.umbral = function () {
    return Math.max(0.025, this._baseline * 2.5) / this.o.sensibilidad;
  };

  /* Pico necesario ahora mismo para que algo cuente como golpe. */
  Cerebro.prototype.umbralPico = function () {
    return Math.max(this.o.picoMinimo, this._picoLento * this.o.picoRelativo) / this.o.sensibilidad;
  };

  Cerebro.prototype.estado = function (ahora, hablando) {
    if (hablando || ahora - this.ultimaHabla < 1200) return 'hablando';
    if (this.hist.length < this.o.calentamiento) return 'calentando';
    return 'escuchando';
  };

  Cerebro.prototype._actualizarBase = function () {
    var s = this.hist.slice().sort(function (a, b) { return a - b; });
    this._baseline = s[Math.floor(s.length * 0.2)] || 0.01;
  };

  Cerebro.prototype._programar = function (ahora) {
    var o = this.o;
    this.siguienteAleatoria = ahora + (o.aleatoriaMinSeg + Math.random() * (o.aleatoriaMaxSeg - o.aleatoriaMinSeg)) * 1000;
  };

  /* Devuelve null, 'golpe', 'ruido', 'silencio' o 'aleatoria'. */
  /* nivel: volumen medio (0-1). pico: valor máximo de la señal en el mismo instante (0-1). */
  Cerebro.prototype.muestra = function (nivel, ahora, hablando, pico) {
    var o = this.o;
    if (pico === undefined) pico = nivel;
    if (this.ultimoRuido === null) { this.ultimoRuido = ahora; this._programar(ahora); }

    /* El altavoz de la calavera no cuenta como ruido del aula (ni su cola de eco). */
    if (hablando) { this.ultimaHabla = ahora; this.prev = nivel; return null; }
    if (ahora - this.ultimaHabla < 1200) { this.prev = nivel; return null; }

    this.hist.push(nivel);
    if (this.hist.length > 2400) this.hist.shift();
    if (++this._n % 40 === 0) this._actualizarBase();
    if (this.hist.length < o.calentamiento) { this.prev = nivel; return null; }

    var u = this.umbral();
    var alto = nivel > u;
    if (alto) { this.ultimoRuido = ahora; this.altos.push(ahora); }
    while (this.altos.length && this.altos[0] < ahora - 3000) this.altos.shift();

    /* Golpe: pico alto frente al pico medio reciente (vale aunque haya ruido de fondo)
       y muy puntual (pico mucho mayor que el volumen medio). */
    var cresta = nivel > 1e-4 ? pico / nivel : 99;
    var golpe = pico > this.umbralPico() && (pico === nivel || cresta > o.cresta);
    this._picoLento += (Math.min(pico, Math.max(this._picoLento * 2, 0.05)) - this._picoLento) * 0.03;
    this.prev = nivel;

    if (golpe && ahora - this.ultimoGolpe > o.golpeEnfriaSeg * 1000) {
      this.ultimoGolpe = ahora;
      this.ultimaHabla = ahora;
      return 'golpe';
    }
    if (ahora - this.ultimaHabla < o.enfriamientoSeg * 1000) return null;

    if (this.altos.length >= o.muestrasRuido) { this.altos = []; this.ultimaHabla = ahora; return 'ruido'; }
    if (o.silencioSeg > 0 && ahora - this.ultimoRuido > o.silencioSeg * 1000) { this.ultimoRuido = ahora; this.ultimaHabla = ahora; return 'silencio'; }
    if (ahora >= this.siguienteAleatoria) { this._programar(ahora); this.ultimaHabla = ahora; return 'aleatoria'; }
    return null;
  };

  /* Sin micrófono: solo frases aleatorias. */
  Cerebro.prototype.sinMicro = function (ahora, hablando) {
    if (this.siguienteAleatoria === null) this._programar(ahora);
    if (hablando) { this.ultimaHabla = ahora; return null; }
    if (ahora - this.ultimaHabla > this.o.enfriamientoSeg * 1000 && ahora >= this.siguienteAleatoria) {
      this._programar(ahora);
      this.ultimaHabla = ahora;
      return 'aleatoria';
    }
    return null;
  };

  /* Bolsa de frases: sale cada una una vez antes de repetir, y nunca la misma dos veces seguidas. */
  function Bolsa(lista) {
    this.lista = lista; this.cola = []; this.ultima = null;
  }
  Bolsa.prototype.siguiente = function () {
    if (!this.cola.length) {
      this.cola = this.lista.slice();
      for (var i = this.cola.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var t = this.cola[i]; this.cola[i] = this.cola[j]; this.cola[j] = t;
      }
      if (this.cola.length > 1 && this.cola[this.cola.length - 1] === this.ultima) this.cola.unshift(this.cola.pop());
    }
    this.ultima = this.cola.pop();
    return this.ultima;
  };

  var api = { Cerebro: Cerebro, Bolsa: Bolsa };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else raiz.CalaveraLogica = api;
})(this);
