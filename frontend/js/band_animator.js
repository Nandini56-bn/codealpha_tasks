/**
 * Virtual Cartoon Band — 8 Original Cartoon Musician Visuals & Stage Performance Animator.
 * Characters:
 *  1. Mira – Piano
 *  2. Niko – Bass
 *  3. Rex – Drums
 *  4. Kai – Guitar
 *  5. Lina – Violin
 *  6. Otto – Saxophone
 *  7. Sora – Flute
 *  8. Asha – Vocal
 */
class BandAnimator {
  constructor() {
    this.containerEl = null;
    this.stageEl = null;
    this.flashTimer = null;
    this.danceInterval = null;
    this.isPlaying = false;
    this.musicians = [
      { id: "pianist", name: "Mira · Piano", isPrimary: true, role: "piano" },
      { id: "bassist", name: "Niko · Bass", isPrimary: false, role: "bass" },
      { id: "drummer", name: "Rex · Drums", isPrimary: false, role: "drums" },
      { id: "guitarist", name: "Kai · Guitar", isPrimary: false, role: "guitar" },
      { id: "violinist", name: "Lina · Violin", isPrimary: false, role: "violin" },
      { id: "saxophonist", name: "Otto · Sax", isPrimary: false, role: "sax" },
      { id: "flutist", name: "Sora · Flute", isPrimary: false, role: "flute" },
      { id: "vocalist", name: "Asha · Vocal", isPrimary: false, role: "vocal" }
    ];
    this.featured = ["pianist"];
    this.mode = "midi";
    this.activeTimeouts = {};
  }

  init(containerId = "musicians-row") {
    this.containerEl = document.getElementById(containerId);
    this.stageEl = document.getElementById("concert-stage");
    if (!this.containerEl) return;
    this.renderMusicians();
    this.attachEventListeners();
  }

  setFeatured(instruments) {
    const map = {
      piano: "pianist", keyboard: "pianist", keys: "pianist", synth: "pianist",
      drums: "drummer", drum: "drummer", dhol: "drummer", percussion: "drummer",
      guitar: "guitarist", "electric guitar": "guitarist",
      violin: "violinist", strings: "violinist",
      sax: "saxophonist", saxophone: "saxophonist",
      flute: "flutist",
      bass: "bassist",
      vocal: "vocalist", vocals: "vocalist", singer: "vocalist"
    };
    const featured = new Set(["pianist"]);
    (instruments || []).forEach((name) => {
      const id = map[String(name).toLowerCase().trim()];
      if (id) featured.add(id);
    });
    this.featured = Array.from(featured);
    this.featured.forEach(id => this.pulseMusician(id));
  }

  renderMusicians() {
    this.containerEl.innerHTML = this.musicians.map((m) => `
      <div class="musician-card slot-${m.id} ${m.isPrimary ? "active" : ""}" id="musician-${m.id}">
        <div class="character-svg-wrapper">${this.getCharacterSVG(m.id)}</div>
        <div class="instrument-label">${m.name}</div>
      </div>
    `).join("");
  }

  getCharacterSVG(id) {
    const art = {
      pianist: this.svgPianist(),
      bassist: this.svgBassist(),
      drummer: this.svgDrummer(),
      guitarist: this.svgGuitarist(),
      violinist: this.svgViolinist(),
      saxophonist: this.svgSaxophonist(),
      flutist: this.svgFlutist(),
      vocalist: this.svgVocalist()
    };
    return art[id] || "";
  }

  // 1. MIRA - PIANO (Original 2D Cartoon Visual)
  svgPianist() {
    return `<svg viewBox="0 0 180 230" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="mira-hair" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#8b5cf6"/>
          <stop offset="100%" stop-color="#06b6d4"/>
        </linearGradient>
        <linearGradient id="mira-vest" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="#ec4899"/>
          <stop offset="100%" stop-color="#be185d"/>
        </linearGradient>
        <linearGradient id="synth-body" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#1e1b4b"/>
          <stop offset="50%" stop-color="#312e81"/>
          <stop offset="100%" stop-color="#1e1b4b"/>
        </linearGradient>
      </defs>

      <ellipse cx="90" cy="218" rx="70" ry="10" fill="rgba(0,0,0,0.45)"/>
      <path d="M55 125 L125 125 L135 178 L45 178 Z" fill="url(#mira-vest)"/>
      <path d="M68 125 L90 155 L112 125 Z" fill="#fef08a"/>

      <g class="anim-head">
        <rect x="83" y="110" width="14" height="18" fill="#fbcfe8" rx="4"/>
        <path d="M48 60 Q90 20 132 60 Q140 110 125 120 Q90 100 55 120 Q40 110 48 60 Z" fill="url(#mira-hair)"/>
        <ellipse cx="90" cy="78" rx="28" ry="30" fill="#fde047" opacity="0.15"/>
        <ellipse cx="90" cy="78" rx="27" ry="29" fill="#fcd34d"/>
        <ellipse cx="78" cy="74" rx="5" ry="7" fill="#1e1b4b"/>
        <ellipse cx="102" cy="74" rx="5" ry="7" fill="#1e1b4b"/>
        <circle cx="79" cy="72" r="2" fill="#ffffff"/>
        <circle cx="103" cy="72" r="2" fill="#ffffff"/>
        <path d="M72 63 Q78 59 84 63" stroke="#4c1d95" stroke-width="2.5" fill="none" stroke-linecap="round"/>
        <path d="M96 63 Q102 59 108 63" stroke="#4c1d95" stroke-width="2.5" fill="none" stroke-linecap="round"/>
        <path d="M80 88 Q90 98 100 88" stroke="#be185d" stroke-width="3" fill="none" stroke-linecap="round"/>
        <circle cx="71" cy="84" r="4" fill="#f43f5e" opacity="0.4"/>
        <circle cx="109" cy="84" r="4" fill="#f43f5e" opacity="0.4"/>
        <path d="M52 68 Q90 40 128 68 Q110 50 90 62 Q70 50 52 68 Z" fill="url(#mira-hair)"/>
        <polygon points="62,52 66,44 70,52 64,47 68,47" fill="#facc15"/>
      </g>

      <g>
        <line x1="45" y1="170" x2="35" y2="215" stroke="#334155" stroke-width="6" stroke-linecap="round"/>
        <line x1="135" y1="170" x2="145" y2="215" stroke="#334155" stroke-width="6" stroke-linecap="round"/>
        <line x1="35" y1="215" x2="145" y2="215" stroke="#1e293b" stroke-width="4"/>
        <rect x="15" y="150" width="150" height="32" rx="6" fill="url(#synth-body)" stroke="#a855f7" stroke-width="2"/>
        <rect x="20" y="153" width="140" height="4" fill="#22d3ee"/>
        <rect x="20" y="160" width="140" height="18" fill="#f8fafc" rx="2"/>
        <g fill="#0f172a">
          <rect x="28" y="160" width="6" height="10"/>
          <rect x="38" y="160" width="6" height="10"/>
          <rect x="54" y="160" width="6" height="10"/>
          <rect x="64" y="160" width="6" height="10"/>
          <rect x="74" y="160" width="6" height="10"/>
          <rect x="90" y="160" width="6" height="10"/>
          <rect x="100" y="160" width="6" height="10"/>
          <rect x="116" y="160" width="6" height="10"/>
          <rect x="126" y="160" width="6" height="10"/>
          <rect x="136" y="160" width="6" height="10"/>
        </g>
      </g>

      <g class="anim-piano-hand">
        <ellipse cx="50" cy="155" rx="9" ry="6" fill="#fcd34d"/>
        <ellipse cx="130" cy="155" rx="9" ry="6" fill="#fcd34d"/>
      </g>
    </svg>`;
  }

  // 2. NIKO - BASS (Original 2D Cartoon Visual)
  svgBassist() {
    return `<svg viewBox="0 0 180 230" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="niko-hoodie" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#4c1d95"/>
          <stop offset="100%" stop-color="#1e1b4b"/>
        </linearGradient>
        <linearGradient id="bass-body" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#ef4444"/>
          <stop offset="100%" stop-color="#991b1b"/>
        </linearGradient>
      </defs>

      <ellipse cx="90" cy="218" rx="60" ry="10" fill="rgba(0,0,0,0.45)"/>
      <path d="M52 120 L128 120 L138 190 L42 190 Z" fill="url(#niko-hoodie)"/>
      <rect x="62" y="185" width="20" height="30" fill="#111827"/>
      <rect x="98" y="185" width="20" height="30" fill="#111827"/>

      <g class="anim-head">
        <rect x="82" y="105" width="16" height="18" fill="#d97706" rx="3"/>
        <path d="M45 65 Q90 10 135 65 L140 85 L40 85 Z" fill="#10b981"/>
        <polygon points="50,45 62,25 72,48" fill="#059669"/>
        <polygon points="75,25 90,10 105,28" fill="#059669"/>
        <polygon points="108,30 122,18 132,42" fill="#059669"/>
        <ellipse cx="90" cy="78" rx="27" ry="28" fill="#f59e0b"/>
        <rect x="62" y="66" width="24" height="16" rx="4" fill="#06b6d4" opacity="0.85"/>
        <rect x="94" y="66" width="24" height="16" rx="4" fill="#06b6d4" opacity="0.85"/>
        <line x1="86" y1="74" x2="94" y2="74" stroke="#0f172a" stroke-width="4"/>
        <path d="M78 92 Q90 100 102 90" stroke="#78350f" stroke-width="3" fill="none" stroke-linecap="round"/>
      </g>

      <g class="anim-bass-pluck">
        <rect x="42" y="80" width="90" height="8" rx="2" fill="#e2e8f0" transform="rotate(-32 90 140)"/>
        <polygon points="30,80 42,72 45,90" fill="#78350f"/>
        <path d="M100 120 C130 110 150 140 140 165 C130 190 90 185 85 160 C80 140 90 125 100 120 Z" fill="url(#bass-body)" stroke="#fca5a5" stroke-width="2"/>
        <ellipse cx="115" cy="152" rx="10" ry="10" fill="#18181b"/>
        <line x1="38" y1="84" x2="132" y2="152" stroke="#fef08a" stroke-width="1.5"/>
        <line x1="38" y1="86" x2="132" y2="154" stroke="#fef08a" stroke-width="1.5"/>
        <circle cx="58" cy="112" r="9" fill="#f59e0b"/>
        <circle cx="120" cy="148" r="9" fill="#f59e0b"/>
      </g>
    </svg>`;
  }

  // 3. REX - DRUMS (Original 2D Cartoon Visual)
  svgDrummer() {
    return `<svg viewBox="0 0 190 240" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="drum-shell" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#d97706"/>
          <stop offset="50%" stop-color="#f59e0b"/>
          <stop offset="100%" stop-color="#b45309"/>
        </linearGradient>
        <linearGradient id="cymbal-gold" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#fef08a"/>
          <stop offset="100%" stop-color="#eab308"/>
        </linearGradient>
      </defs>

      <ellipse cx="95" cy="226" rx="80" ry="12" fill="rgba(0,0,0,0.5)"/>

      <ellipse cx="95" cy="180" rx="48" ry="32" fill="url(#drum-shell)" stroke="#78350f" stroke-width="3"/>
      <ellipse cx="95" cy="180" rx="42" ry="26" fill="#fef3c7"/>
      <text x="95" y="185" font-family="'Syne', sans-serif" font-weight="800" font-size="13" fill="#b45309" text-anchor="middle">AI FEST</text>
      
      <ellipse cx="46" cy="150" rx="22" ry="10" fill="url(#drum-shell)"/>
      <ellipse cx="46" cy="147" rx="22" ry="8" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>

      <ellipse cx="144" cy="150" rx="22" ry="10" fill="url(#drum-shell)"/>
      <ellipse cx="144" cy="147" rx="22" ry="8" fill="#ffffff" stroke="#94a3b8" stroke-width="2"/>

      <line x1="25" y1="140" x2="20" y2="80" stroke="#64748b" stroke-width="4"/>
      <ellipse cx="20" cy="80" rx="30" ry="8" fill="url(#cymbal-gold)" stroke="#ca8a04" stroke-width="1.5"/>

      <line x1="165" y1="140" x2="170" y2="75" stroke="#64748b" stroke-width="4"/>
      <ellipse cx="170" cy="75" rx="32" ry="8" fill="url(#cymbal-gold)" stroke="#ca8a04" stroke-width="1.5"/>

      <path d="M68 95 L122 95 L130 135 L60 135 Z" fill="#06b6d4"/>

      <g class="anim-head">
        <rect x="87" y="80" width="16" height="18" fill="#fbcfe8" rx="4"/>
        <path d="M50 48 Q95 5 140 48 L142 62 L48 62 Z" fill="#ea580c"/>
        <polygon points="55,30 68,10 80,32" fill="#c2410c"/>
        <polygon points="85,12 100,-2 112,18" fill="#c2410c"/>
        <polygon points="115,22 130,8 138,35" fill="#c2410c"/>
        <rect x="48" y="48" width="94" height="10" fill="#facc15" rx="3"/>
        <ellipse cx="95" cy="65" rx="26" ry="26" fill="#fcd34d"/>
        <circle cx="84" cy="60" r="6" fill="#1e1b4b"/>
        <circle cx="106" cy="60" r="6" fill="#1e1b4b"/>
        <circle cx="86" cy="58" r="2.5" fill="#ffffff"/>
        <circle cx="108" cy="58" r="2.5" fill="#ffffff"/>
        <path d="M80 72 Q95 90 110 72 Z" fill="#991b1b"/>
        <path d="M84 73 Q95 79 106 73" fill="#ffffff"/>
      </g>

      <g class="anim-drum-stick">
        <line x1="72" y1="105" x2="38" y2="125" stroke="#fcd34d" stroke-width="8" stroke-linecap="round"/>
        <line x1="38" y1="125" x2="25" y2="88" stroke="#fef08a" stroke-width="4" stroke-linecap="round"/>
        <line x1="118" y1="105" x2="152" y2="125" stroke="#fcd34d" stroke-width="8" stroke-linecap="round"/>
        <line x1="152" y1="125" x2="165" y2="82" stroke="#fef08a" stroke-width="4" stroke-linecap="round"/>
      </g>
    </svg>`;
  }

  // 4. KAI - GUITAR (Original 2D Cartoon Visual)
  svgGuitarist() {
    return `<svg viewBox="0 0 180 230" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="kai-jacket" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#1e1b4b"/>
          <stop offset="100%" stop-color="#0f172a"/>
        </linearGradient>
        <linearGradient id="v-guitar" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#dc2626"/>
          <stop offset="100%" stop-color="#f59e0b"/>
        </linearGradient>
      </defs>

      <ellipse cx="90" cy="218" rx="60" ry="10" fill="rgba(0,0,0,0.45)"/>
      <path d="M50 118 L130 118 L138 190 L42 190 Z" fill="url(#kai-jacket)"/>
      <path d="M70 118 L90 148 L110 118 Z" fill="#ec4899"/>
      <rect x="62" y="185" width="18" height="30" fill="#1e293b"/>
      <rect x="100" y="185" width="18" height="30" fill="#1e293b"/>

      <g class="anim-head">
        <rect x="82" y="102" width="16" height="18" fill="#fbcfe8" rx="3"/>
        <path d="M42 58 Q90 10 138 58 Q145 100 128 105 Q90 85 52 105 Z" fill="#0284c7"/>
        <path d="M42 62 Q75 35 110 52 Q85 40 60 55 Z" fill="#38bdf8"/>
        <ellipse cx="90" cy="74" rx="26" ry="27" fill="#fcd34d"/>
        <ellipse cx="78" cy="70" rx="5" ry="6" fill="#0f172a"/>
        <circle cx="79" cy="68" r="2" fill="#ffffff"/>
        <path d="M96 70 Q102 64 108 70" stroke="#0f172a" stroke-width="3" fill="none" stroke-linecap="round"/>
        <path d="M80 86 Q90 94 100 86" stroke="#991b1b" stroke-width="3" fill="none" stroke-linecap="round"/>
      </g>

      <g class="anim-guitar-strum">
        <rect x="35" y="70" width="95" height="7" rx="2" fill="#f8fafc" transform="rotate(-30 90 135)"/>
        <polygon points="22,68 35,58 38,78" fill="#dc2626"/>
        <polygon points="100,120 155,145 140,185 115,150 90,178 80,140" fill="url(#v-guitar)" stroke="#fef08a" stroke-width="2"/>
        <circle cx="118" cy="148" r="7" fill="#18181b"/>
        <circle cx="55" cy="105" r="8" fill="#fcd34d"/>
        <circle cx="118" cy="142" r="8" fill="#fcd34d"/>
      </g>
    </svg>`;
  }

  // 5. LINA - VIOLIN (Original 2D Cartoon Visual)
  svgViolinist() {
    return `<svg viewBox="0 0 180 230" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="lina-dress" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#a855f7"/>
          <stop offset="100%" stop-color="#6b21a8"/>
        </linearGradient>
        <linearGradient id="violin-wood" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#b45309"/>
          <stop offset="100%" stop-color="#78350f"/>
        </linearGradient>
      </defs>

      <ellipse cx="90" cy="218" rx="55" ry="9" fill="rgba(0,0,0,0.45)"/>
      <path d="M55 120 L125 120 L140 195 L40 195 Z" fill="url(#lina-dress)"/>

      <g class="anim-head">
        <rect x="83" y="105" width="14" height="18" fill="#fbcfe8" rx="3"/>
        <path d="M45 55 Q90 15 135 55 Q150 115 130 135 Q115 90 90 100 Q65 90 50 135 Q30 115 45 55 Z" fill="#fde047"/>
        <circle cx="58" cy="50" r="7" fill="#ec4899"/>
        <circle cx="58" cy="50" r="3" fill="#fef08a"/>
        <ellipse cx="90" cy="76" rx="26" ry="27" fill="#fcd34d"/>
        <ellipse cx="78" cy="72" rx="4.5" ry="6.5" fill="#1e1b4b"/>
        <ellipse cx="102" cy="72" rx="4.5" ry="6.5" fill="#1e1b4b"/>
        <circle cx="79" cy="70" r="2" fill="#ffffff"/>
        <circle cx="103" cy="70" r="2" fill="#ffffff"/>
        <path d="M82 87 Q90 94 98 87" stroke="#b45309" stroke-width="2.5" fill="none" stroke-linecap="round"/>
      </g>

      <g>
        <path d="M65 110 C50 120 50 145 68 152 C85 160 90 135 80 120 Z" fill="url(#violin-wood)" stroke="#fef08a" stroke-width="1.5"/>
        <line x1="72" y1="92" x2="68" y2="152" stroke="#1e293b" stroke-width="3"/>
      </g>

      <g class="anim-violin-bow">
        <line x1="40" y1="110" x2="115" y2="155" stroke="#f8fafc" stroke-width="3" stroke-linecap="round"/>
        <circle cx="105" cy="148" r="7" fill="#fcd34d"/>
      </g>
    </svg>`;
  }

  // 6. OTTO - SAXOPHONE (Original 2D Cartoon Visual)
  svgSaxophonist() {
    return `<svg viewBox="0 0 180 230" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="otto-suit" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#eab308"/>
          <stop offset="100%" stop-color="#ca8a04"/>
        </linearGradient>
        <linearGradient id="sax-gold" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#fef08a"/>
          <stop offset="50%" stop-color="#f59e0b"/>
          <stop offset="100%" stop-color="#b45309"/>
        </linearGradient>
      </defs>

      <ellipse cx="90" cy="218" rx="60" ry="10" fill="rgba(0,0,0,0.45)"/>
      <path d="M50 115 L130 115 L138 190 L42 190 Z" fill="url(#otto-suit)"/>
      <rect x="75" y="115" width="30" height="75" fill="#1e293b"/>
      <rect x="62" y="185" width="20" height="30" fill="#0f172a"/>
      <rect x="98" y="185" width="20" height="30" fill="#0f172a"/>

      <g class="anim-head">
        <rect x="82" y="100" width="16" height="18" fill="#d97706" rx="3"/>
        <ellipse cx="90" cy="74" rx="27" ry="27" fill="#f59e0b"/>
        <path d="M45 52 Q90 28 135 52 L145 58 L35 58 Z" fill="#881337"/>
        <rect x="58" y="32" width="64" height="24" rx="4" fill="#881337"/>
        <rect x="58" y="48" width="64" height="8" fill="#facc15"/>
        <rect x="64" y="66" width="22" height="14" rx="3" fill="#0f172a"/>
        <rect x="94" y="66" width="22" height="14" rx="3" fill="#0f172a"/>
        <line x1="86" y1="72" x2="94" y2="72" stroke="#0f172a" stroke-width="3"/>
        <path d="M72 88 Q90 82 108 88 Q90 98 72 88 Z" fill="#451a03"/>
      </g>

      <g class="anim-sax-sway">
        <path d="M88 95 C92 120 100 155 125 165 C142 172 155 155 145 138" stroke="url(#sax-gold)" stroke-width="12" fill="none" stroke-linecap="round"/>
        <ellipse cx="145" cy="138" rx="16" ry="10" fill="url(#sax-gold)" stroke="#ca8a04" stroke-width="2"/>
        <circle cx="92" cy="115" r="7" fill="#f59e0b"/>
        <circle cx="106" cy="140" r="7" fill="#f59e0b"/>
      </g>
    </svg>`;
  }

  // 7. SORA - FLUTE (Original 2D Cartoon Visual)
  svgFlutist() {
    return `<svg viewBox="0 0 180 230" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="sora-top" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#06b6d4"/>
          <stop offset="100%" stop-color="#0891b2"/>
        </linearGradient>
        <linearGradient id="flute-silver" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#ffffff"/>
          <stop offset="50%" stop-color="#cbd5e1"/>
          <stop offset="100%" stop-color="#94a3b8"/>
        </linearGradient>
      </defs>

      <ellipse cx="90" cy="218" rx="50" ry="9" fill="rgba(0,0,0,0.45)"/>
      <path d="M58 118 L122 118 L132 195 L48 195 Z" fill="url(#sora-top)"/>

      <g class="anim-head">
        <rect x="83" y="104" width="14" height="18" fill="#fbcfe8" rx="3"/>
        <circle cx="48" cy="62" r="16" fill="#f43f5e"/>
        <circle cx="132" cy="62" r="16" fill="#f43f5e"/>
        <path d="M50 55 Q90 20 130 55 Q138 90 122 98 Q90 85 58 98 Z" fill="#fb7185"/>
        <ellipse cx="90" cy="74" rx="25" ry="26" fill="#fcd34d"/>
        <ellipse cx="78" cy="70" rx="4.5" ry="6" fill="#0f172a"/>
        <ellipse cx="102" cy="70" rx="4.5" ry="6" fill="#0f172a"/>
        <circle cx="79" cy="68" r="2" fill="#ffffff"/>
        <circle cx="103" cy="68" r="2" fill="#ffffff"/>
        <ellipse cx="90" cy="85" rx="4" ry="5" fill="#be185d"/>
      </g>

      <g class="anim-flute-play">
        <rect x="35" y="82" width="115" height="7" rx="3.5" fill="url(#flute-silver)" stroke="#64748b" stroke-width="1"/>
        <circle cx="65" cy="85" r="1.8" fill="#1e293b"/>
        <circle cx="78" cy="85" r="1.8" fill="#1e293b"/>
        <circle cx="90" cy="85" r="1.8" fill="#1e293b"/>
        <circle cx="102" cy="85" r="1.8" fill="#1e293b"/>
        <circle cx="114" cy="85" r="1.8" fill="#1e293b"/>
        <circle cx="70" cy="88" r="6" fill="#fcd34d"/>
        <circle cx="108" cy="88" r="6" fill="#fcd34d"/>
      </g>
    </svg>`;
  }

  // 8. ASHA - VOCAL (Original 2D Cartoon Visual)
  svgVocalist() {
    return `<svg viewBox="0 0 180 230" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="asha-gown" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#f43f5e"/>
          <stop offset="100%" stop-color="#881337"/>
        </linearGradient>
        <linearGradient id="mic-chrome" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#ffffff"/>
          <stop offset="100%" stop-color="#475569"/>
        </linearGradient>
      </defs>

      <ellipse cx="90" cy="218" rx="55" ry="9" fill="rgba(0,0,0,0.45)"/>
      <path d="M52 118 L128 118 L142 195 L38 195 Z" fill="url(#asha-gown)"/>

      <g class="anim-head">
        <rect x="82" y="102" width="16" height="18" fill="#fbcfe8" rx="3"/>
        <circle cx="55" cy="55" r="22" fill="#1e1b4b"/>
        <circle cx="125" cy="55" r="22" fill="#1e1b4b"/>
        <circle cx="90" cy="40" r="24" fill="#1e1b4b"/>
        <path d="M50 50 Q90 15 130 50 Q142 98 126 108 Q90 88 54 108 Z" fill="#312e81"/>
        <ellipse cx="90" cy="74" rx="26" ry="27" fill="#fcd34d"/>
        <ellipse cx="78" cy="68" rx="5" ry="6.5" fill="#0f172a"/>
        <ellipse cx="102" cy="68" rx="5" ry="6.5" fill="#0f172a"/>
        <circle cx="79" cy="66" r="2" fill="#ffffff"/>
        <circle cx="103" cy="66" r="2" fill="#ffffff"/>
        <path d="M80 82 Q90 98 100 82 Z" fill="#991b1b"/>
        <path d="M83 83 Q90 87 97 83" fill="#ffffff"/>
      </g>

      <g class="anim-mic">
        <line x1="125" y1="100" x2="120" y2="215" stroke="#94a3b8" stroke-width="4"/>
        <ellipse cx="120" cy="215" rx="18" ry="5" fill="#334155"/>
        <rect x="120" y="85" width="10" height="18" rx="5" fill="url(#mic-chrome)" stroke="#1e293b" stroke-width="1.5"/>
        <ellipse cx="125" cy="85" rx="8" ry="8" fill="url(#mic-chrome)"/>
        <circle cx="120" cy="98" r="7" fill="#fcd34d"/>
      </g>
    </svg>`;
  }

  attachEventListeners() {
    window.addEventListener("note_on", (e) => this.handleNoteTrigger(e.detail));
    window.addEventListener("audio_frame", (e) => this.handleAudioEnergy(e.detail));
    window.addEventListener("player_mode", (e) => { this.mode = e.detail.mode; });
    window.addEventListener("playback_started", () => {
      this.isPlaying = true;
      if (this.stageEl) this.stageEl.classList.add("is-live");
      const pianist = document.getElementById("musician-pianist");
      if (pianist) pianist.classList.add("active");
      this.startStageDanceLoop();
    });
    window.addEventListener("playback_ended", () => this.clearAllActiveStates());
    window.addEventListener("playback_stopped", () => this.clearAllActiveStates());
    window.addEventListener("playback_paused", () => {
      this.isPlaying = false;
      if (this.stageEl) this.stageEl.classList.remove("is-live", "flash");
      this.stopStageDanceLoop();
    });
  }

  startStageDanceLoop() {
    this.stopStageDanceLoop();
    this.danceInterval = setInterval(() => {
      if (!this.isPlaying) return;
      this.musicians.forEach((m) => {
        const card = document.getElementById(`musician-${m.id}`);
        if (!card) return;
        const shiftX = (Math.random() * 8 - 4).toFixed(1);
        const shiftY = (Math.random() * 6 - 3).toFixed(1);
        card.style.setProperty("--sway-x", `${shiftX}px`);
        card.style.setProperty("--sway-y", `${shiftY}px`);
      });
    }, 400);
  }

  stopStageDanceLoop() {
    if (this.danceInterval) {
      clearInterval(this.danceInterval);
      this.danceInterval = null;
    }
    this.musicians.forEach((m) => {
      const card = document.getElementById(`musician-${m.id}`);
      if (card) {
        card.style.removeProperty("--sway-x");
        card.style.removeProperty("--sway-y");
      }
    });
  }

  handleAudioEnergy(detail) {
    if (this.mode !== "audio" || !detail) return;
    const energy = detail.energy || 0;
    const bass = detail.bass || 0;
    if (this.stageEl) {
      this.stageEl.classList.toggle("flash", energy > 0.42);
      this.stageEl.style.setProperty("--energy", energy.toFixed(3));
    }
    if (bass > 0.35) this.pulseMusician("drummer");
    if (bass > 0.28) this.pulseMusician("bassist");
    if (energy > 0.22) this.pulseMusician("guitarist");
    if (energy > 0.18) this.pulseMusician("pianist");
    if (energy > 0.3) this.pulseMusician("saxophonist");
    if (energy > 0.26) this.pulseMusician("violinist");
    if (energy > 0.32) this.pulseMusician("flutist");
    if (energy > 0.24) this.pulseMusician("vocalist");
    if (energy > 0.4) this.spawnNoteParticle();
  }

  handleNoteTrigger(note) {
    this.pulseMusician("pianist");
    if (this.stageEl) {
      this.stageEl.classList.add("flash");
      clearTimeout(this.flashTimer);
      this.flashTimer = setTimeout(() => this.stageEl.classList.remove("flash"), 120);
    }

    const midiNum = note.midi || 60;
    if (midiNum >= 76) this.pulseMusician("flutist");
    else if (midiNum >= 69) this.pulseMusician("violinist");
    else if (midiNum >= 62) this.pulseMusician("guitarist");
    else if (midiNum >= 55) this.pulseMusician("saxophonist");
    else this.pulseMusician("drummer");

    this.spawnNoteParticle(note.name || "♪");
  }

  pulseMusician(id) {
    const cardEl = document.getElementById(`musician-${id}`);
    if (!cardEl) return;
    cardEl.classList.add("active");
    if (this.activeTimeouts[id]) clearTimeout(this.activeTimeouts[id]);
    this.activeTimeouts[id] = setTimeout(() => {
      if (id !== "pianist") cardEl.classList.remove("active");
    }, 420);
  }

  spawnNoteParticle() {
    if (!this.stageEl) return;
    const particle = document.createElement("div");
    particle.className = "note-particle";
    particle.innerText = ["♪", "♫", "♬", "♭", "♯"][Math.floor(Math.random() * 5)];
    particle.style.left = `${15 + Math.random() * 70}%`;
    particle.style.bottom = `${25 + Math.random() * 25}%`;
    this.stageEl.appendChild(particle);
    setTimeout(() => particle.remove(), 1400);
  }

  clearAllActiveStates() {
    this.isPlaying = false;
    this.stopStageDanceLoop();
    if (this.stageEl) this.stageEl.classList.remove("is-live", "flash");
    this.musicians.forEach((m) => {
      if (!m.isPrimary) {
        const el = document.getElementById(`musician-${m.id}`);
        if (el) el.classList.remove("active");
      }
    });
  }
}

window.bandAnimator = new BandAnimator();
