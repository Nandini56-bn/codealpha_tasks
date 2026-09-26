/**
 * Application orchestrator — LSTM MIDI + Lyria audio, history, lyrics, visualizer.
 */
document.addEventListener("DOMContentLoaded", () => {
  window.audioEngine.init();
  window.bandAnimator.init();
  window.visualizer.init();
  window.chatController.init();

  const state = {
    mode: "lyria",
    lastLyrics: "",
    generating: false
  };

  const enterPerformance = () => {
    document.body.classList.add("performance-mode");
    document.querySelectorAll(".nav-pill").forEach((b) => b.classList.remove("active"));
    const studioBtn = document.querySelector('[data-tab="tab-studio"]');
    if (studioBtn) studioBtn.classList.add("active");
    document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
    const studio = document.getElementById("tab-studio");
    if (studio) studio.classList.add("active");
    window.visualizer.resize();
  };

  const exitPerformance = () => {
    document.body.classList.remove("performance-mode");
    window.visualizer.resize();
  };

  const showTab = (targetId) => {
    exitPerformance();
    document.querySelectorAll(".nav-pill").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));
    const btn = document.querySelector(`[data-tab="${targetId}"]`);
    if (btn) btn.classList.add("active");
    const targetContent = document.getElementById(targetId);
    if (targetContent) targetContent.classList.add("active");
    window.visualizer.resize();
  };

  document.querySelectorAll(".nav-pill").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (btn.id === "nav-performance-btn") {
        enterPerformance();
        return;
      }
      const target = btn.getAttribute("data-tab");
      if (target) {
        showTab(target);
        if (target === "tab-history") loadHistory();
      }
    });
  });

  const perfBtn = document.getElementById("performance-mode-btn");
  const exitBtn = document.getElementById("exit-performance-btn");
  if (perfBtn) perfBtn.addEventListener("click", enterPerformance);
  if (exitBtn) exitBtn.addEventListener("click", exitPerformance);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") exitPerformance();
  });

  const viewHistBtn = document.getElementById("view-history-tab-btn");
  if (viewHistBtn) {
    viewHistBtn.addEventListener("click", () => {
      showTab("tab-history");
      loadHistory();
    });
  }

  const aboutEduBtn = document.getElementById("about-how-it-works-btn");
  if (aboutEduBtn) {
    aboutEduBtn.addEventListener("click", () => showTab("tab-education"));
  }

  const setStatus = (text, show = true) => {
    const banner = document.getElementById("status-banner");
    const statusText = document.getElementById("status-text");
    if (statusText) statusText.innerText = text;
    if (banner) banner.style.display = show ? "flex" : "none";
  };

  const setMode = (mode) => {
    state.mode = mode;
    const lyriaBtn = document.getElementById("mode-lyria-btn");
    const lstmBtn = document.getElementById("mode-lstm-btn");
    const genSourceSelect = document.getElementById("generation-source-select");
    const genAiBtn = document.getElementById("generate-ai-btn");
    const genLstmBtn = document.getElementById("generate-btn");

    if (lyriaBtn) lyriaBtn.classList.toggle("active", mode === "lyria");
    if (lstmBtn) lstmBtn.classList.toggle("active", mode === "lstm");
    if (genSourceSelect) genSourceSelect.value = mode;

    if (genAiBtn) genAiBtn.hidden = mode !== "lyria";
    if (genLstmBtn) genLstmBtn.hidden = mode !== "lstm";
  };

  const lyriaPill = document.getElementById("mode-lyria-btn");
  const lstmPill = document.getElementById("mode-lstm-btn");
  if (lyriaPill) lyriaPill.addEventListener("click", () => setMode("lyria"));
  if (lstmPill) lstmPill.addEventListener("click", () => setMode("lstm"));

  const genSourceSelect = document.getElementById("generation-source-select");
  if (genSourceSelect) {
    genSourceSelect.addEventListener("change", (e) => setMode(e.target.value));
  }

  const volumeSlider = document.getElementById("volume-slider");
  if (volumeSlider) {
    volumeSlider.addEventListener("input", () => {
      window.audioEngine.setVolume(parseInt(volumeSlider.value, 10));
    });
  }

  const applyPlayerMeta = ({ kicker, name, meta, midiUrl, audioUrl, lyricsUrl, filename, audioName, lyricsName }) => {
    document.getElementById("track-kicker").innerText = kicker;
    document.getElementById("track-name").innerText = name;
    document.getElementById("track-meta").innerText = meta;
    const midiBtn = document.getElementById("download-midi-btn");
    const audioBtn = document.getElementById("download-audio-btn");
    
    if (midiBtn) {
      midiBtn.hidden = !midiUrl;
      if (midiUrl) {
        midiBtn.href = midiUrl;
        midiBtn.setAttribute("download", filename || "composition.mid");
      }
    }
    if (audioBtn) {
      audioBtn.hidden = !audioUrl;
      if (audioUrl) {
        audioBtn.href = audioUrl;
        audioBtn.setAttribute("download", audioName || "song.mp3");
      }
    }
    const badge = document.getElementById("sync-badge");
    if (badge) badge.innerText = kicker.includes("MIDI") ? "MIDI note-sync" : "Audio analyser sync";
    const led = document.getElementById("led-title");
    if (led) led.innerText = name.slice(0, 28).toUpperCase();
  };

  const pollJob = async (jobId) => {
    for (let i = 0; i < 180; i++) {
      const res = await fetch(`/api/music/status/${jobId}`);
      const job = await res.json();
      if (job.message) setStatus(job.message, true);
      if (job.status === "succeeded") return job.result;
      if (job.status === "failed") {
        throw new Error(job.error || job.message || "AI song generation failed");
      }
      await new Promise((r) => setTimeout(r, 2500));
    }
    throw new Error("Timed out waiting for Lyria API. Check history later or try again.");
  };

  const playLyriaResult = async (data) => {
    const lyrics = data.lyrics || "";
    state.lastLyrics = lyrics;
    const editor = document.getElementById("lyrics-editor");
    if (editor && lyrics) editor.value = lyrics;
    if (window.bandAnimator && data.music_spec) {
      window.bandAnimator.setFeatured(data.music_spec.instruments || []);
    }
    applyPlayerMeta({
      kicker: "Lyria (AI Audio)",
      name: data.composition_name || data.filename,
      meta: `Style: ${data.genre || "Mass / Indian"} · Model: ${data.model || "lyria-3.5"}`,
      audioUrl: data.download_url,
      audioName: data.filename,
      lyricsUrl: data.lyrics_download_url
    });
    await window.audioEngine.loadAudioUrl(data.static_url || data.download_url);
    await window.audioEngine.play();
  };

  const generateAiSong = async (message, specOverride = null) => {
    if (state.generating) return;
    state.generating = true;
    const generateBtn = document.getElementById("generate-ai-btn");
    if (generateBtn) generateBtn.disabled = true;
    setStatus("Gemini is preparing a MusicSpec...", true);
    try {
      const genreVal = document.getElementById("ai-genre").value || "indian commercial / mass";
      const vocalsVal = document.getElementById("ai-vocals").value;
      const spec = specOverride || {
        genre: genreVal,
        vocals: vocalsVal === "vocals"
      };
      const body = {
        message: message || document.getElementById("ai-request").value || "naku oka mass music kavali generate chesi ivvu",
        spec: spec,
        generate_lyrics: true
      };
      const response = await fetch("/api/music/generate-ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Request failed");
      if (data.api_key_missing || data.status === "error") {
        throw new Error(data.message || data.reply || "AI Song Generator is not available.");
      }
      setStatus("Lyria 3.5 is composing audio. This can take a minute...", true);
      const result = await pollJob(data.job_id);
      setStatus("Loading generated audio...", true);
      await playLyriaResult(result);
      setStatus("Playing generated audio", false);
      loadHistory();
    } catch (err) {
      setStatus(`Error: ${err.message}`, true);
    } finally {
      state.generating = false;
      if (generateBtn) generateBtn.disabled = false;
    }
  };

  window.chatController.onGenerateSpec = async (text, spec) => {
    setMode("lyria");
    await generateAiSong(text, spec);
  };
  window.chatController.onGenerateLyrics = async (text, spec) => {
    showTab("tab-lyrics");
    await generateLyrics(text, spec);
  };

  const generateBtn = document.getElementById("generate-btn");
  if (generateBtn) {
    generateBtn.addEventListener("click", async () => {
      generateBtn.disabled = true;
      setStatus("Running local PyTorch LSTM inference...", true);
      if (typeof Tone !== "undefined") await Tone.start();
      try {
        const response = await fetch("/api/music/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            generate_length: 64,
            creativity: 1.0,
            genre: "Classical Bach",
            instrument: "Piano"
          })
        });
        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || "Generation request failed");
        }
        const data = await response.json();
        setStatus("Loading generated MIDI into the concert player...", true);
        const midiRes = await fetch(data.download_url);
        const arrayBuffer = await midiRes.arrayBuffer();
        await window.audioEngine.loadMidiArrayBuffer(arrayBuffer);
        window.bandAnimator.setFeatured(["piano"]);
        applyPlayerMeta({
          kicker: "Local LSTM (MIDI)",
          name: data.composition_name,
          meta: `Style: Bach Classical · Model: PyTorch LSTM · ${data.note_count} notes`,
          midiUrl: data.download_url,
          filename: data.filename
        });
        setStatus("", false);
        generateBtn.disabled = false;
        window.audioEngine.play();
        loadHistory();
      } catch (err) {
        setStatus(`Error: ${err.message}`, true);
        generateBtn.disabled = false;
      }
    });
  }

  const generateAiBtn = document.getElementById("generate-ai-btn");
  if (generateAiBtn) {
    generateAiBtn.addEventListener("click", () => generateAiSong());
  }

  const playBtn = document.getElementById("play-btn");
  const pauseBtn = document.getElementById("pause-btn");
  const replayBtn = document.getElementById("replay-btn");
  if (playBtn) {
    playBtn.addEventListener("click", () => {
      window.audioEngine.play();
      playBtn.hidden = true;
      if (pauseBtn) pauseBtn.hidden = false;
    });
  }
  if (pauseBtn) {
    pauseBtn.addEventListener("click", () => {
      window.audioEngine.pause();
      pauseBtn.hidden = true;
      if (playBtn) playBtn.hidden = false;
    });
  }
  if (replayBtn) replayBtn.addEventListener("click", () => {
    window.audioEngine.stop();
    window.audioEngine.play();
    if (playBtn) playBtn.hidden = true;
    if (pauseBtn) pauseBtn.hidden = false;
  });

  const progressBarBg = document.getElementById("progress-bar-bg");
  if (progressBarBg) {
    progressBarBg.addEventListener("click", (e) => {
      const rect = progressBarBg.getBoundingClientRect();
      const percent = ((e.clientX - rect.left) / rect.width) * 100;
      window.audioEngine.seek(percent);
    });
  }

  window.audioEngine.onProgressCallback = (currentTime, duration) => {
    const fill = document.getElementById("progress-bar-fill");
    const timeDisplay = document.getElementById("time-display");
    if (fill && duration > 0) {
      fill.style.width = `${Math.min(100, (currentTime / duration) * 100)}%`;
    }
    if (timeDisplay) {
      const format = (sec) => {
        const m = Math.floor(sec / 60);
        const s = Math.floor(sec % 60);
        return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
      };
      timeDisplay.innerText = `${format(currentTime || 0)} / ${format(duration || 0)}`;
    }
  };

  async function generateLyrics(message, spec) {
    const editor = document.getElementById("lyrics-editor");
    setStatus("Generating original lyrics with Gemini...", true);
    const res = await fetch("/api/music/lyrics", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: message || "Write original song lyrics",
        spec,
        previous_lyrics: editor.value || null
      })
    });
    const data = await res.json();
    if (data.api_key_missing || data.status === "error") {
      setStatus(data.message || "Lyrics require GEMINI_API_KEY", true);
      return;
    }
    editor.value = data.lyrics || "";
    state.lastLyrics = editor.value;
    setStatus("Lyrics ready", false);
  }

  const lyricsGenBtn = document.getElementById("lyrics-generate-btn");
  if (lyricsGenBtn) {
    lyricsGenBtn.addEventListener("click", () => generateLyrics());
  }

  async function loadHistory() {
    try {
      const res = await fetch("/api/music/history");
      const data = await res.json();
      const items = data.history || [];
      const previewContainer = document.getElementById("history-list");
      const fullContainer = document.getElementById("full-history-list");
      
      if (!items.length) {
        if (previewContainer) previewContainer.innerHTML = "<div class='history-item-placeholder'>No generated tracks yet.</div>";
        if (fullContainer) fullContainer.innerHTML = "<div class='history-item-placeholder'>No generated tracks yet.</div>";
        return;
      }

      const html = items.map((item) => {
        const mode = item.mode || item.metadata?.mode || "lstm";
        const filename = item.filename || item.metadata?.filename;
        const genre = item.genre || "Music";
        return `<div class="history-item" data-id="${item.id}" data-mode="${mode}" data-file="${filename || ""}">
          <div>
            <strong>${item.composition_name || filename || item.id}</strong>
            <div style="font-size:11px; opacity:0.7;">${genre} • ${mode.toUpperCase()}</div>
          </div>
          <button type="button" class="btn-ghost-sm" style="padding:4px 8px;">▶ Play</button>
        </div>`;
      }).join("");

      if (previewContainer) previewContainer.innerHTML = html;
      if (fullContainer) fullContainer.innerHTML = html;

      document.querySelectorAll(".history-item").forEach((btn) => {
        btn.addEventListener("click", async () => {
          const filename = btn.getAttribute("data-file");
          const mode = btn.getAttribute("data-mode");
          if (!filename) return;
          const url = `/api/music/download/${filename}`;
          if (mode === "lyria" || filename.endsWith(".mp3") || filename.endsWith(".wav")) {
            applyPlayerMeta({
              kicker: "Lyria (AI Audio)",
              name: filename,
              meta: "Replaying generated AI song",
              audioUrl: url,
              audioName: filename
            });
            await window.audioEngine.loadAudioUrl(url);
            await window.audioEngine.play();
          } else {
            const midiRes = await fetch(url);
            const buf = await midiRes.arrayBuffer();
            await window.audioEngine.loadMidiArrayBuffer(buf);
            applyPlayerMeta({
              kicker: "Local LSTM (MIDI)",
              name: filename,
              meta: "Replaying generated LSTM MIDI",
              midiUrl: url,
              filename
            });
            window.audioEngine.play();
          }
          showTab("tab-studio");
        });
      });
    } catch (err) {}
  }

  loadHistory();

  fetch("/api/music/capabilities")
    .then((r) => r.json())
    .then((caps) => {
      const note = document.getElementById("lyria-setup-note");
      if (!note) return;
      if (!caps.api_key_configured) {
        note.innerText = "GEMINI_API_KEY is missing in backend .env. Local LSTM MIDI generation works offline.";
      } else {
        note.innerText = `Director: ${caps.gemini_director.model}. Audio: ${caps.lyria.model}.`;
      }
    })
    .catch(() => {});
});
