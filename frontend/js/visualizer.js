/**
 * Dual visualizer: MIDI note-on events OR AnalyserNode FFT for generated audio.
 */
class Visualizer {
  constructor() {
    this.canvases = [];
    this.animId = null;
    this.isPlaying = false;
    this.barCount = 48;
    this.bars = new Float32Array(48);
    this.targetBars = new Float32Array(48);
    this.roll = [];
    this.wave = 0;
    this.mode = "idle";
    this.particles = [];
  }

  init() {
    const main = document.getElementById("visualizer-canvas");
    const stage = document.getElementById("stage-viz-canvas");
    this.canvases = [main, stage].filter(Boolean).map((canvas) => ({
      canvas,
      ctx: canvas.getContext("2d")
    }));
    this.resize();
    window.addEventListener("resize", () => this.resize());
    window.addEventListener("note_on", (e) => this.handleNote(e.detail));
    window.addEventListener("audio_frame", (e) => this.handleAudioFrame(e.detail));
    window.addEventListener("player_mode", (e) => this.setMode(e.detail.mode));
    window.addEventListener("playback_started", (e) => {
      this.isPlaying = true;
      if (e.detail && e.detail.mode) this.setMode(e.detail.mode);
      const dot = document.getElementById("visualizer-dot");
      if (dot) dot.classList.remove("inactive");
      this.startLoop();
    });
    window.addEventListener("playback_stopped", () => this.stopLoop());
    window.addEventListener("playback_ended", () => this.stopLoop());
    window.addEventListener("playback_paused", () => {
      this.isPlaying = false;
    });
    this.drawIdleState();
  }

  setMode(mode) {
    this.mode = mode;
    const title = document.getElementById("viz-title");
    const caption = document.getElementById("viz-caption");
    const badge = document.getElementById("viz-badge");
    const label = document.getElementById("visualizer-label");
    if (mode === "midi") {
      if (title) title.innerText = "MIDI Note Visualizer";
      if (caption) caption.innerText = "Bars and piano-roll hits are driven by generated MIDI note-on events during Tone.js playback — not an FFT analyzer.";
      if (badge) badge.innerText = "Note-event canvas";
      if (label) label.innerText = "LIVE MIDI NOTE STREAM";
    } else if (mode === "audio") {
      if (title) title.innerText = "Audio Spectrum Visualizer";
      if (caption) caption.innerText = "Frequency bars, waveform motion, bass, and energy meters are driven by Web Audio AnalyserNode FFT on the mixed Lyria audio — not MIDI note events.";
      if (badge) badge.innerText = "AnalyserNode FFT";
      if (label) label.innerText = "LIVE AUDIO SPECTRUM";
    }
  }

  resize() {
    this.canvases.forEach(({ canvas }) => {
      const dpr = window.devicePixelRatio || 1;
      canvas.width = Math.max(1, canvas.clientWidth * dpr);
      canvas.height = Math.max(1, canvas.clientHeight * dpr);
    });
  }

  handleNote(note) {
    if (this.mode === "audio") return;
    const midiNum = note.midi || 60;
    const barIdx = Math.floor(((midiNum - 21) / 87) * this.barCount);
    const validIdx = Math.max(0, Math.min(this.barCount - 1, barIdx));
    this.targetBars[validIdx] = Math.min(1.0, this.targetBars[validIdx] + 0.85);
    if (validIdx > 0) this.targetBars[validIdx - 1] += 0.35;
    if (validIdx < this.barCount - 1) this.targetBars[validIdx + 1] += 0.35;
    this.wave = Math.min(1, this.wave + 0.45);
    this.roll.push({ x: validIdx / this.barCount, life: 1, midi: midiNum });
    if (this.roll.length > 80) this.roll.shift();
  }

  handleAudioFrame(detail) {
    if (this.mode !== "audio" || !detail || !detail.bins) return;
    const bins = detail.bins;
    const step = Math.max(1, Math.floor(bins.length / this.barCount));
    for (let i = 0; i < this.barCount; i++) {
      this.targetBars[i] = bins[Math.min(bins.length - 1, i * step)] / 255;
    }
    this.wave = Math.min(1, detail.energy * 1.8);
    const bassEl = document.getElementById("bass-meter");
    const energyEl = document.getElementById("energy-meter");
    if (bassEl) bassEl.innerText = detail.bass.toFixed(2);
    if (energyEl) energyEl.innerText = detail.energy.toFixed(2);
    if (detail.energy > 0.28) {
      this.particles.push({
        x: Math.random(),
        y: 1,
        life: 1,
        speed: 0.004 + detail.bass * 0.01
      });
      if (this.particles.length > 60) this.particles.shift();
    }
  }

  startLoop() {
    if (this.animId) cancelAnimationFrame(this.animId);
    const loop = () => {
      this.render();
      this.animId = requestAnimationFrame(loop);
    };
    loop();
  }

  stopLoop() {
    this.isPlaying = false;
    const dot = document.getElementById("visualizer-dot");
    if (dot) dot.classList.add("inactive");
    if (this.animId) cancelAnimationFrame(this.animId);
    this.drawIdleState();
  }

  render() {
    this.canvases.forEach((entry, i) => this.drawFrame(entry, i === 0));
  }

  drawFrame({ canvas, ctx }, full) {
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);

    const barWidth = w / this.barCount;
    for (let i = 0; i < this.barCount; i++) {
      this.bars[i] += (this.targetBars[i] - this.bars[i]) * 0.22;
      if (this.mode !== "audio") this.targetBars[i] *= 0.9;
      const barHeight = Math.max(4, this.bars[i] * (h * (full ? 0.55 : 0.8)));
      const x = i * barWidth + 1;
      const y = h - barHeight;
      const g = ctx.createLinearGradient(0, h, 0, y);
      g.addColorStop(0, "#2de2e6");
      g.addColorStop(0.55, "#9b5de5");
      g.addColorStop(1, "#ff3cac");
      ctx.fillStyle = g;
      ctx.fillRect(x, y, Math.max(1, barWidth - 2), barHeight);
    }

    this.wave *= this.mode === "audio" ? 0.96 : 0.94;
    ctx.beginPath();
    ctx.strokeStyle = "rgba(255,209,102,0.85)";
    ctx.lineWidth = Math.max(1.5, h * 0.012);
    for (let i = 0; i < w; i += 4) {
      const amp = this.wave * h * 0.12 * Math.sin((i / w) * Math.PI * 6 + performance.now() / 180);
      const y = h * 0.42 + amp;
      if (i === 0) ctx.moveTo(i, y);
      else ctx.lineTo(i, y);
    }
    ctx.stroke();

    if (full) {
      this.roll.forEach((n) => {
        n.life *= 0.985;
        const nx = n.x * w;
        const ny = h * 0.18 + (1 - n.life) * h * 0.2;
        ctx.globalAlpha = Math.max(0, n.life);
        ctx.fillStyle = "#ffd166";
        ctx.fillRect(nx, ny, Math.max(6, w * 0.018), 8);
        ctx.globalAlpha = 1;
      });
      this.roll = this.roll.filter((n) => n.life > 0.05);

      this.particles.forEach((p) => {
        p.y -= p.speed;
        p.life *= 0.985;
        ctx.globalAlpha = Math.max(0, p.life);
        ctx.fillStyle = "#ff3cac";
        ctx.beginPath();
        ctx.arc(p.x * w, p.y * h, 3, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1;
      });
      this.particles = this.particles.filter((p) => p.life > 0.05 && p.y > 0);
    }
  }

  drawIdleState() {
    this.canvases.forEach(({ canvas, ctx }) => {
      const w = canvas.width;
      const h = canvas.height;
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = "rgba(255,255,255,0.08)";
      const barWidth = w / this.barCount;
      for (let i = 0; i < this.barCount; i++) {
        ctx.fillRect(i * barWidth + 2, h - 8, barWidth - 4, 6);
      }
    });
  }
}

window.visualizer = new Visualizer();
