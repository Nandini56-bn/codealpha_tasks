/**
 * Dual player: Tone.js MIDI synthesis OR HTML5 audio (Lyria).
 * MIDI and generated audio are never mixed up.
 */
class AudioEngine {
  constructor() {
    this.synth = null;
    this.midiData = null;
    this.isPlaying = false;
    this.duration = 0;
    this.currentTime = 0;
    this.animFrameId = null;
    this.onProgressCallback = null;
    this.onEndedCallback = null;
    this.mode = "idle"; // midi | audio
    this.audioEl = null;
    this.audioCtx = null;
    this.analyser = null;
    this.freqData = null;
    this.sourceNode = null;
    this.gainNode = null;
    this.volume = 0.8;
  }

  async init() {
    if (typeof Tone !== "undefined") {
      this.synth = new Tone.PolySynth(Tone.Synth, {
        oscillator: { type: "triangle" },
        envelope: { attack: 0.02, decay: 0.3, sustain: 0.4, release: 0.8 }
      }).toDestination();
      Tone.Destination.volume.value = -6;
    }
    this.audioEl = new Audio();
    this.audioEl.preload = "auto";
    this.audioEl.addEventListener("ended", () => {
      this.isPlaying = false;
      window.dispatchEvent(new CustomEvent("playback_ended"));
      if (this.onEndedCallback) this.onEndedCallback();
    });
    this.audioEl.addEventListener("timeupdate", () => {
      if (this.mode !== "audio") return;
      this.currentTime = this.audioEl.currentTime || 0;
      this.duration = this.audioEl.duration && isFinite(this.audioEl.duration) ? this.audioEl.duration : this.duration;
      if (this.onProgressCallback) this.onProgressCallback(this.currentTime, this.duration || 0);
    });
  }

  async _ensureAnalyser() {
    if (this.analyser) return;
    const Ctx = window.AudioContext || window.webkitAudioContext;
    this.audioCtx = this.audioCtx || new Ctx();
    this.analyser = this.audioCtx.createAnalyser();
    this.analyser.fftSize = 256;
    this.freqData = new Uint8Array(this.analyser.frequencyBinCount);
    this.gainNode = this.audioCtx.createGain();
    this.gainNode.gain.value = this.volume;
    if (!this.sourceNode && this.audioEl) {
      this.sourceNode = this.audioCtx.createMediaElementSource(this.audioEl);
      this.sourceNode.connect(this.gainNode);
      this.gainNode.connect(this.analyser);
      this.analyser.connect(this.audioCtx.destination);
    }
  }

  getAnalyserSnapshot() {
    if (!this.analyser || this.mode !== "audio" || !this.isPlaying) return null;
    this.analyser.getByteFrequencyData(this.freqData);
    const bins = this.freqData;
    let sum = 0;
    let bass = 0;
    const bassCount = Math.max(1, Math.floor(bins.length * 0.12));
    for (let i = 0; i < bins.length; i++) {
      sum += bins[i];
      if (i < bassCount) bass += bins[i];
    }
    return {
      bins,
      energy: sum / (bins.length * 255),
      bass: bass / (bassCount * 255)
    };
  }

  async loadMidiArrayBuffer(arrayBuffer) {
    if (typeof Midi === "undefined") {
      throw new Error("@tonejs/midi library not loaded.");
    }
    this.stop();
    this.mode = "midi";
    if (this.audioEl) {
      this.audioEl.pause();
      this.audioEl.removeAttribute("src");
    }
    await Tone.start();
    this.midiData = new Midi(arrayBuffer);
    this.duration = this.midiData.duration || 10;
    Tone.Transport.cancel();
    Tone.Transport.position = 0;

    this.midiData.tracks.forEach((track) => {
      track.notes.forEach((note) => {
        Tone.Transport.schedule((time) => {
          if (this.synth) {
            this.synth.triggerAttackRelease(note.name, note.duration, time, note.velocity);
          }
          window.dispatchEvent(new CustomEvent("note_on", { detail: note }));
        }, note.time);
      });
    });

    Tone.Transport.schedule(() => {
      this.isPlaying = false;
      window.dispatchEvent(new CustomEvent("playback_ended"));
      if (this.onEndedCallback) this.onEndedCallback();
    }, this.duration + 0.5);

    window.dispatchEvent(new CustomEvent("player_mode", { detail: { mode: "midi" } }));
    return {
      duration: this.duration,
      trackCount: this.midiData.tracks.length,
      noteCount: this.midiData.tracks.reduce((acc, t) => acc + t.notes.length, 0)
    };
  }

  async loadAudioUrl(url) {
    this.stop();
    this.mode = "audio";
    this.midiData = null;
    if (typeof Tone !== "undefined") {
      Tone.Transport.cancel();
      Tone.Transport.stop();
    }
    await this._ensureAnalyser();
    if (this.audioCtx && this.audioCtx.state === "suspended") {
      await this.audioCtx.resume();
    }
    this.audioEl.src = url;
    await new Promise((resolve, reject) => {
      const onReady = () => {
        this.audioEl.removeEventListener("error", onError);
        this.duration = this.audioEl.duration && isFinite(this.audioEl.duration) ? this.audioEl.duration : 0;
        resolve();
      };
      const onError = () => {
        this.audioEl.removeEventListener("canplay", onReady);
        reject(new Error("Could not load generated audio file."));
      };
      this.audioEl.addEventListener("canplay", onReady, { once: true });
      this.audioEl.addEventListener("error", onError, { once: true });
      this.audioEl.load();
    });
    window.dispatchEvent(new CustomEvent("player_mode", { detail: { mode: "audio" } }));
    return { duration: this.duration };
  }

  async play() {
    if (this.mode === "midi") {
      if (!this.midiData) return;
      await Tone.start();
      if (this.duration && Tone.Transport.seconds >= this.duration) {
        Tone.Transport.seconds = 0;
      }
      Tone.Transport.start();
      this.isPlaying = true;
      window.dispatchEvent(new CustomEvent("playback_started", { detail: { mode: "midi" } }));
      this._startProgressTracker();
      return;
    }
    if (this.mode === "audio" && this.audioEl && this.audioEl.src) {
      if (this.audioCtx && this.audioCtx.state === "suspended") {
        await this.audioCtx.resume();
      }
      try {
        await this.audioEl.play();
      } catch (err) {
        throw err;
      }
      this.isPlaying = true;
      window.dispatchEvent(new CustomEvent("playback_started", { detail: { mode: "audio" } }));
      this._startProgressTracker();
    }
  }

  pause() {
    if (this.mode === "midi" && typeof Tone !== "undefined") {
      Tone.Transport.pause();
    }
    if (this.mode === "audio" && this.audioEl) {
      this.audioEl.pause();
    }
    this.isPlaying = false;
    window.dispatchEvent(new CustomEvent("playback_paused"));
    if (this.animFrameId) cancelAnimationFrame(this.animFrameId);
  }

  stop() {
    if (typeof Tone !== "undefined") {
      Tone.Transport.stop();
      Tone.Transport.position = 0;
    }
    if (this.audioEl) {
      this.audioEl.pause();
      this.audioEl.currentTime = 0;
    }
    this.isPlaying = false;
    this.currentTime = 0;
    window.dispatchEvent(new CustomEvent("playback_stopped"));
    if (this.animFrameId) cancelAnimationFrame(this.animFrameId);
    if (this.onProgressCallback) this.onProgressCallback(0, this.duration);
  }

  seek(progressPercent) {
    if (!this.duration) return;
    const targetSeconds = (progressPercent / 100) * this.duration;
    if (this.mode === "midi" && typeof Tone !== "undefined") {
      Tone.Transport.seconds = targetSeconds;
    }
    if (this.mode === "audio" && this.audioEl) {
      this.audioEl.currentTime = targetSeconds;
    }
    this.currentTime = targetSeconds;
    if (this.onProgressCallback) this.onProgressCallback(this.currentTime, this.duration);
  }

  setVolume(percent) {
    this.volume = Math.max(0, Math.min(1, percent / 100));
    if (this.gainNode) this.gainNode.gain.value = this.volume;
    if (this.audioEl) this.audioEl.volume = this.volume;
    if (typeof Tone !== "undefined") {
      Tone.Destination.volume.value = this.volume <= 0 ? -Infinity : (this.volume - 1) * 24;
    }
  }

  _startProgressTracker() {
    const update = () => {
      if (!this.isPlaying) return;
      if (this.mode === "midi") {
        this.currentTime = Tone.Transport.seconds;
        if (this.duration && this.currentTime >= this.duration) {
          this.currentTime = this.duration;
          if (this.onProgressCallback) this.onProgressCallback(this.currentTime, this.duration);
          this.pause();
          window.dispatchEvent(new CustomEvent("playback_ended"));
          return;
        }
      } else if (this.mode === "audio") {
        const snap = this.getAnalyserSnapshot();
        if (snap) {
          window.dispatchEvent(new CustomEvent("audio_frame", { detail: snap }));
        }
      }
      if (this.onProgressCallback) {
        this.onProgressCallback(this.currentTime, this.duration);
      }
      window.dispatchEvent(new CustomEvent("playback_progress", {
        detail: { currentTime: this.currentTime, duration: this.duration, mode: this.mode }
      }));
      this.animFrameId = requestAnimationFrame(update);
    };
    update();
  }
}

window.audioEngine = new AudioEngine();
