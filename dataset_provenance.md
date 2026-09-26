# Dataset Provenance & Licensing Documentation

This document records what the **live Local LSTM MIDI Generator** actually uses.

---

## 1. Classical / Baroque Dataset (LIVE)

* **Dataset Name**: J.S. Bach Chorales & Classical Keyboard Compositions (built into `music21.corpus`).
* **Source**: `music21` open-source library corpus (`music21.corpus.getComposer('bach')`).
* **Original Source**: J.S. Bach (1685–1750) Original Compositions.
* **Piece-Specific License**: **Public Domain**.
* **Number of Files**: 50 preprocessed `.mid` compositions used to build `backend/data/processed/vocab.json` and `dataset.pkl`.
* **Genre**: Classical / Baroque counterpoint piano sequences.
* **Preprocessing**: `music21.converter` tokens such as `'C4'`, `'0.4.7'`, `'REST'`.
* **Used by**: `lstm_music_model.pth` and `POST /api/music/generate`.

---

## 2. Leftover genre folders (NOT live models)

`backend/data/processed/jazz/` and `backend/data/processed/ragtime/` plus related download scripts may exist from earlier experiments.

They are **not** wired as extra LSTM genre engines in the running app. The UI does not claim a local jazz or ragtime generator. Modern/general genres are generated only through **Lyria 3.5** when API access exists.

Do not train new checkpoints on fake/stub MIDI.

---

## Summary

| Material | Live LSTM? | Notes |
| :--- | :--- | :--- |
| Bach chorales (`music21.corpus`) | Yes | Public domain |
| Jazz/ragtime leftover vocabs | No | Ignored by the live generator |
| Lyria 3.5 audio | N/A | Foundation model via Gemini API, not local MIDI training |
