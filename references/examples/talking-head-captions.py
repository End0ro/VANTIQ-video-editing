"""Talking-head caption template (approved by Ahmed 2026-09-19).

Style spec: references/video-editing-styles.md -> "Talking head videos".
Worked example from the "нейросети и работа" reel (41.8s, 1080x1920).

HOW TO REUSE on a new video:
  1. Copy this file into <videos_dir>/edit/ and set up edit/fonts/ (see the
     style doc: download the Manrope + Playfair Italic variable fonts, then
     instance them to static files with fontTools).
  2. Replace END, CAPTIONS and the body of cards() with the new video's
     words. Timestamps are word starts from edit/transcripts/<name>.json.
  3. Check CAP_BOTTOM against a frame: captions must sit above the head.
  4. python build_captions.py -> captions.ass, then burn it with
     ffmpeg -vf "ass=captions.ass:fontsdir=fonts" (see the style doc).
Keep the engine (metrics, layout, word_events, card, strike) as is.

Engine notes:
Every word is its own ASS event so it can fade in exactly when spoken.
Word layout is measured with PIL using libass's font-size convention
(\\fs = winAscent + winDescent in px).

Caption edits in this example: fillers dropped, 35.04s "не в том".
"""
from pathlib import Path
from fontTools.ttLib import TTFont
from PIL import ImageFont

EDIT = Path(__file__).parent
FONTS = EDIT / "fonts"
END = 41.77
W = 1080

FONT = {
    "sans": ("VQ Manrope XB", FONTS / "VQ-Manrope-XB.ttf"),
    "serif": ("VQ Playfair It", FONTS / "VQ-Playfair-It.ttf"),
}

# colors (ASS is &HBBGGRR&)
WHITE, INK, GRAY = "&HFFFFFF&", "&H161616&", "&H7E8288&"
RED, GREEN, CARD = "&H3B43D9&", "&H5B9D2E&", "&HF2F5F7&"

# ---------------------------------------------------------------- metrics
_metrics, _pil = {}, {}


def metrics(kind):
    if kind not in _metrics:
        f = TTFont(FONT[kind][1])
        os2 = f["OS/2"]
        tot = os2.usWinAscent + os2.usWinDescent
        _metrics[kind] = (f["head"].unitsPerEm / tot, os2.usWinAscent / tot)
    return _metrics[kind]


def width(word, kind, fs):
    em_ratio, _ = metrics(kind)
    em = round(fs * em_ratio * 4)
    key = (kind, em)
    if key not in _pil:
        _pil[key] = ImageFont.truetype(str(FONT[kind][1]), em)
    return _pil[key].getlength(word) / 4 * 1.0


def ascent(kind, fs):
    return fs * metrics(kind)[1]


# ---------------------------------------------------------------- ass utils
def ts(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


EVENTS = []


def ev(layer, t0, t1, tags, text):
    EVENTS.append(f"Dialogue: {layer},{ts(t0)},{ts(t1)},Base,,0,0,0,,{{{tags}}}{text}")


def rrect(w, h, r):
    k = r * 0.5523
    return (f"m {r} 0 l {w-r} 0 b {w-r+k} 0 {w} {r-k} {w} {r} l {w} {h-r} "
            f"b {w} {h-r+k} {w-r+k} {h} {w-r} {h} l {r} {h} b {r-k} {h} 0 {h-r+k} 0 {h-r} "
            f"l 0 {r} b 0 {r-k} {r-k} 0 {r} 0")


# ---------------------------------------------------------------- layout
def layout(lines, cx, top, gap=0.18):
    """lines: [[(text, t, kind, fs, color), ...], ...] -> placed words + block height.
    Each word: dict(text, t, kind, fs, color, x, y_top). Lines centered on cx."""
    placed, y = [], top
    for line in lines:
        base_asc = max(ascent(k, fs) for _, _, k, fs, _ in line)
        line_h = max(fs for _, _, _, fs, _ in line)
        space = [width(" ", k, fs) * 1.05 for _, _, k, fs, _ in line]
        ws = [width(w, k, fs) + (fs * 0.06 if k == "serif" else 0) for w, _, k, fs, _ in line]
        total = sum(ws) + sum(space[:-1])
        x = cx - total / 2
        baseline = y + base_asc
        for (w, t, k, fs, c), wd, sp in zip(line, ws, space):
            placed.append(dict(text=w, t=t, kind=k, fs=fs, color=c, x=x,
                               y_top=baseline - ascent(k, fs), w=wd, baseline=baseline))
            x += wd + sp
        y += line_h * (1 + gap)
    return placed, y - top - max(fs for _, _, _, fs, _ in lines[-1]) * gap


def word_events(words, t_end, shadow=True, rise=12, first_rise=None, t_block=None):
    """Fade + unblur + small rise per word, all words fade out together at t_end."""
    for wd in words:
        t0 = max(wd["t"] - 0.06, t_block if t_block is not None else 0)
        if t0 >= t_end - 0.1:
            t0 = t_end - 0.3
        dur = int((t_end - t0) * 1000)
        r = first_rise if (first_rise and t_block is not None and t0 <= t_block + 0.01) else rise
        mv_ms = 420 if r > rise else 320
        x, y = round(wd["x"], 1), round(wd["y_top"], 1)
        fn, fs = FONT[wd["kind"]][0], wd["fs"]
        fade = rf"\fad(280,200)"
        blur = rf"\blur6\t(0,300,\blur0)\t({max(dur-200,0)},{dur},\blur6)"
        common = rf"\an7\fn{fn}\fs{fs}\bord0\shad0"
        if shadow:
            ev(1, t0, t_end, rf"{common}\move({x},{y+r+4},{x},{y+4},0,{mv_ms})\1c&H000000&\alpha&H98&\blur16{fade}", wd["text"])
        ev(2, t0, t_end, rf"{common}\move({x},{y+r},{x},{y},0,{mv_ms})\1c{wd['color']}{blur}{fade}", wd["text"])


# ---------------------------------------------------------------- captions
S, A = 96, 116          # sans size, accent serif size
CAP_BOTTOM = 590        # captions sit above the head


def s(t, w, c=WHITE, fs=S): return (w, t, "sans", fs, c)
def a(t, w, c=WHITE, fs=A): return (w, t, "serif", fs, c)


CAPTIONS = [  # (lines) ; phrase ends when the next block starts
    [[s(0.08, "Многие"), s(0.58, "думают,")]],
    [[s(1.20, "что"), s(1.38, "нейросети")], [s(1.94, "заберут"), s(2.30, "их"), a(2.46, "работу.")]],
    [[s(2.98, "И"), s(3.04, "на"), s(3.20, "самом"), s(3.50, "деле")]],
    [[s(4.24, "ничего"), s(4.62, "такого")], [s(4.98, "не"), a(5.10, "произойдет.")]],
    [[s(5.96, "Всемирный")], [s(6.40, "экономический"), a(7.06, "форум")]],
    [[s(7.76, "посчитал,"), s(8.48, "что"), s(8.72, "к")], [a(8.78, "2030"), s(10.20, "году")]],
    [[s(11.08, "ИИ"), s(11.24, "заберет")], [s(12.32, "всего"), s(12.66, "лишь-то"), s(13.08, "каких-то")]],
    "CARDS_AB",
    [[s(18.60, "И"), s(18.68, "почему"), s(19.02, "так")], [a(19.18, "происходит?")]],
    [[s(20.18, "Потому"), s(20.56, "что")], [a(20.98, "нейросеть")]],
    [[s(21.92, "это"), s(22.26, "не"), s(22.40, "замена")], [a(22.84, "людям,")]],
    "CARD_C",
    [[s(25.50, "который"), s(26.08, "позволяет")], [s(26.76, "делать"), a(27.16, "больше,")]],
    [[s(27.62, "работая")], [a(28.20, "меньше.")]],
    [[s(29.66, "Ты"), s(29.76, "не"), s(29.90, "теряешь"), s(30.40, "работу")], [s(30.88, "из-за"), a(31.14, "этого,")]],
    [[s(31.40, "ты"), s(31.52, "теряешь"), s(31.94, "работу")], [s(32.28, "из-за"), a(32.42, "того,")]],
    [[s(32.68, "что"), s(32.82, "пока"), s(33.02, "другие")], [a(33.54, "учатся,")]],
    [[s(33.86, "ты"), s(33.96, "сидишь")], [a(34.20, "на"), a(34.32, "месте.")]],
    "CARDS_DE",
]
BLOCK_START = {"CARDS_AB": 13.94, "CARD_C": 23.38, "CARDS_DE": 35.04}


def block_start(b):
    return BLOCK_START[b] if isinstance(b, str) else b[0][0][1]


def captions():
    for i, blk in enumerate(CAPTIONS):
        if isinstance(blk, str):
            continue
        nxt = block_start(CAPTIONS[i + 1]) if i + 1 < len(CAPTIONS) else END
        t_end = nxt - 0.04
        # measure block height to bottom-anchor it
        _, h = layout(blk, W / 2, 0)
        words, _ = layout(blk, W / 2, CAP_BOTTOM - h)
        word_events(words, t_end)


# ---------------------------------------------------------------- cards
def card(lines, cx, top, t_in, t_out, pad=(46, 34), radius=34, min_w=0):
    words, h = layout(lines, cx, top + pad[1], gap=0.12)
    content_w = max(wd["x"] + wd["w"] for wd in words) - min(wd["x"] for wd in words)
    w = max(content_w + 2 * pad[0], min_w)
    h = h + 2 * pad[1]
    x0 = cx - w / 2
    dur = int((t_out - t_in) * 1000)
    path = rrect(round(w), round(h), radius)
    mv = lambda dy: rf"\move({x0:.1f},{top+dy+24:.1f},{x0:.1f},{top+dy:.1f},0,420)"
    anim = rf"\fad(300,220)\blur8\t(0,320,\blur0)\t({dur-220},{dur},\blur8)"
    # soft drop shadow, then the card
    ev(0, t_in, t_out, rf"\an7{mv(14)}\bord0\shad0\1c&H000000&\alpha&HB4&\blur22\fad(300,220)\p1", path)
    ev(0, t_in, t_out, rf"\an7{mv(0)}\bord0\shad0\1c{CARD}\alpha&H08&{anim}\p1", path)
    word_events(words, t_out, shadow=False, rise=10, first_rise=24, t_block=t_in)
    return words, (x0, top, w, h)


def strike(words, t0, t1):
    """Red line drawn left-to-right through each text line of a card."""
    lines = {}
    for wd in words:
        if wd["color"] == GRAY:
            continue
        lines.setdefault(round(wd["baseline"]), []).append(wd)
    dur = int((t1 - t0) * 1000)
    for i, (bl, ws) in enumerate(sorted(lines.items())):
        x0 = min(w["x"] for w in ws) - 8
        x1 = max(w["x"] + w["w"] for w in ws) + 8
        fs = ws[0]["fs"]
        y = bl - fs * 0.27
        d = 60 * i
        ev(3, t0, t1, rf"\an7\pos({x0:.0f},{y-4:.0f})\bord0\shad0\1c{RED}\clip({x0:.0f},0,{x0:.0f},1920)"
                      rf"\t({d},{d+320},0.6,\clip({x0:.0f},0,{x1:.0f},1920))\fad(0,220)\p1",
           rrect(round(x1 - x0), 8, 4))


def cards():
    # A + B side by side: the numbers comparison
    g = lambda t, w, fs=48: (w, t, "sans", fs, GRAY)
    card([[g(13.94, "заберет")],
          [("−92", 13.94, "serif", 120, RED), ("млн", 14.30, "serif", 120, RED)],
          [("рабочих", 14.86, "sans", 50, INK), ("мест", 15.28, "sans", 50, INK)]],
         cx=285, top=300, t_in=13.94, t_out=18.56, min_w=440)
    card([[g(15.94, "создаст")],
          [("+180", 16.68, "serif", 120, GREEN), ("млн", 17.44, "serif", 120, GREEN)],
          [("новых", 17.88, "sans", 50, INK)]],
         cx=795, top=300, t_in=15.94, t_out=18.56, min_w=440)
    # C: the reframe
    card([[g(23.38, "это"), g(23.54, "всего"), g(23.82, "лишь")],
          [("инструмент", 24.60, "serif", 120, INK)]],
         cx=540, top=330, t_in=23.38, t_out=25.46)
    # D: wrong question, struck through
    d_words, _ = card([[g(35.04, "И"), g(35.10, "вопрос"), g(35.40, "не"), g(35.46, "в"), g(35.50, "том,")],
                       [("что", 35.80, "sans", 72, INK), ("не", 36.26, "sans", 72, INK), ("заменит", 36.38, "sans", 72, INK)],
                       [("ли", 36.92, "sans", 72, INK), ("тебя", 37.42, "sans", 72, INK), ("нейросеть?", 37.68, "serif", 88, INK)]],
                      cx=540, top=290, t_in=35.04, t_out=38.90)
    strike(d_words, 38.20, 38.90)
    # E: the real question (enters in the pause after "а вопрос в том")
    card([[g(38.95, "а"), g(38.95, "вопрос"), g(38.95, "в"), g(38.95, "том:")],
          [("используешь", 39.34, "serif", 112, INK)],
          [("ли", 40.30, "sans", 72, INK), ("ты", 40.44, "sans", 72, INK), ("их", 40.64, "sans", 72, INK),
           ("или", 41.06, "sans", 72, INK), ("нет?", 41.26, "sans", 72, INK)]],
         cx=540, top=290, t_in=38.95, t_out=END)


def main():
    captions()
    cards()
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Base,VQ Manrope XB,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,204

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    out = EDIT / "captions_v2.ass"
    out.write_text(head + "\n".join(EVENTS) + "\n", encoding="utf-8-sig")
    print(f"wrote {out} ({len(EVENTS)} events)")


if __name__ == "__main__":
    main()
