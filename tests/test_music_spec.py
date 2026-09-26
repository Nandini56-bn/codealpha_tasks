from backend.app.ai.music_spec import MusicSpec, apply_mass_and_genre_expansion, build_lyria_prompt


def test_mass_music_maps_to_production_description():
    spec = MusicSpec(
        genre="mass",
        original_request="naku oka mass music kavali generate chesi ivvu",
        instruments=[],
    )
    expanded = apply_mass_and_genre_expansion(spec)
    assert expanded.genre == "indian commercial / mass"
    assert expanded.tempo_bpm == 128
    assert "dhol" in " ".join(expanded.instruments).lower() or "drums" in expanded.style_description.lower()
    prompt = build_lyria_prompt(expanded)
    assert "Indian commercial" in prompt or "indian commercial" in prompt.lower()
    assert "Do not imitate" in prompt
    assert "specific artist" in prompt.lower()


def test_dj_and_classical_prompts_are_distinct():
    dj = apply_mass_and_genre_expansion(MusicSpec(genre="dj", original_request="make me a DJ beat with energetic drums"))
    classical = apply_mass_and_genre_expansion(MusicSpec(genre="classical", original_request="I want classical piano music", vocals=False))
    dj_prompt = build_lyria_prompt(dj)
    classical_prompt = build_lyria_prompt(classical)
    assert "DJ" in dj_prompt or "club" in dj_prompt.lower()
    assert "classical" in classical_prompt.lower()
    assert "Instrumental only" in classical_prompt


def test_custom_lyrics_are_passed_into_lyria_prompt():
    spec = MusicSpec(genre="pop", vocals=True, lyrics_required=True, language="Telugu")
    lyrics = "[Verse]\nOka kotha udayam\n[Chorus]\nMunduku veltham"
    prompt = build_lyria_prompt(spec, lyrics=lyrics)
    assert "Lyrics:" in prompt
    assert "Oka kotha udayam" in prompt
    assert "[Chorus]" in prompt


def test_music_spec_coerces_types():
    spec = MusicSpec(
        tempo_bpm="140",
        instruments="drums, bass, synth",
        vocals="yes",
        lyrics_required="true",
        structure="Intro, Chorus, Outro",
    )
    assert spec.tempo_bpm == 140
    assert spec.instruments == ["drums", "bass", "synth"]
    assert spec.vocals is True
    assert spec.lyrics_required is True
    assert spec.structure[0] == "Intro"
