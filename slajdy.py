"""Generator slajdów: python3 slajdy.py  ->  slajdy.html (otwórz w przeglądarce).

Każdy slajd = tytuł + rysunek (SVG) + notatki prelegenta (klawisz n) z tekstem do wygłoszenia.
"""
import html
import math
import pathlib

ROOT = pathlib.Path(__file__).parent

# ---------- paleta (te same kolory klas co w demo) ----------
DARK, LIGHT, INK, PAPER = '#14161B', '#FAF7F1', '#1E2024', '#F2EFE9'
MUTED, MUTED_D, GRAY, LINE = '#5B6168', '#A7AEB5', '#8B939C', '#E3E0D6'
ORANGE, CYAN, YELLOW = '#D9481F', '#2BB8C4', '#E8C547'
SKIN, HAIR, BROW, CLOTH = '#D9A066', '#7A3B5E', '#5B3A29', '#6E7F5B'
CARD, CARD_D = '#FFFFFF', '#1B1E24'
F_H, F_B, F_M = "'Space Grotesk', sans-serif", "'IBM Plex Sans', sans-serif", "'JetBrains Mono', monospace"
FONTS = ('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400..700'
         '&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap')


# ---------- prymitywy SVG ----------
def S(*parts, w=1600, h=620):
    return (f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:100%;overflow:visible" '
            f'font-family="{F_B}">' + ''.join(parts) + '</svg>')


def g(inner, x=0, y=0, k=1, flip=False, extra=''):
    sx = -k if flip else k
    return f'<g transform="translate({x} {y}) scale({sx} {k})" {extra}>{inner}</g>'


def r(x, y, w, h, fill='none', st=None, sw=3, rx=0, dash=None, op=None):
    s = f' stroke="{st}" stroke-width="{sw}"' if st else ''
    s += f' stroke-dasharray="{dash}"' if dash else ''
    s += f' opacity="{op}"' if op is not None else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{s}/>'


def c(x, y, rad, fill='none', st=None, sw=3, op=None):
    s = f' stroke="{st}" stroke-width="{sw}"' if st else ''
    s += f' opacity="{op}"' if op is not None else ''
    return f'<circle cx="{x}" cy="{y}" r="{rad}" fill="{fill}"{s}/>'


def e(x, y, rx, ry, fill='none', st=None, sw=3, op=None):
    s = f' stroke="{st}" stroke-width="{sw}"' if st else ''
    s += f' opacity="{op}"' if op is not None else ''
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}"{s}/>'


def p(d, fill='none', st=None, sw=3, dash=None, op=None, extra=''):
    s = f' stroke="{st}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"' if st else ''
    s += f' stroke-dasharray="{dash}"' if dash else ''
    s += f' opacity="{op}"' if op is not None else ''
    return f'<path d="{d}" fill="{fill}"{s} {extra}/>'


def l(x1, y1, x2, y2, st=GRAY, sw=3, dash=None):
    s = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{st}" stroke-width="{sw}" stroke-linecap="round"{s}/>'


def t(x, y, s, size=28, fill='currentColor', a='middle', w=400, f=None, op=None):
    o = f' opacity="{op}"' if op is not None else ''
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{a}" '
            f'font-weight="{w}" font-family="{f or F_B}"{o}>{s}</text>')


def tm(x, y, lines, size=28, lh=1.3, **kw):
    return ''.join(t(x, y + i * size * lh, s, size, **kw) for i, s in enumerate(lines))


def arr(x1, y1, x2, y2, col=GRAY, sw=5, hd=22, dash=None):
    a = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - hd * math.cos(a), y2 - hd * math.sin(a)
    dx, dy = hd * 0.55 * math.sin(a), hd * 0.55 * math.cos(a)
    pts = f'{x2:.1f},{y2:.1f} {bx + dx:.1f},{by - dy:.1f} {bx - dx:.1f},{by + dy:.1f}'
    return l(x1, y1, bx, by, col, sw, dash) + f'<polygon points="{pts}" fill="{col}"/>'


def grid(x, y, cs, rows, cmap, gap=0, st=None, nums=None, nsize=None, ncol=None, rx=0):
    """rows: lista napisów, każdy znak -> kolor z cmap; nums: ta sama siatka z tekstem do wpisania."""
    o = []
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            fill = cmap(i, j, ch) if callable(cmap) else cmap[ch]
            o.append(r(x + i * cs, y + j * cs, cs - gap, cs - gap, fill, st, 1, rx))
            if nums:
                n = nums[j][i] if isinstance(nums[j], (list, tuple)) else nums[j][i]
                nc = ncol(fill) if callable(ncol) else (ncol or INK)
                o.append(t(x + i * cs + (cs - gap) / 2, y + j * cs + (cs - gap) / 2 + (nsize or cs * .4) * .36,
                           n, nsize or cs * .4, nc, f=F_M))
    return ''.join(o)


def legend(x, y, items, size=26, sw=30, gap=48, fill='currentColor'):
    o = []
    for i, (col, name) in enumerate(items):
        o.append(r(x, y + i * gap, sw, sw, col, rx=6))
        o.append(t(x + sw + 16, y + i * gap + sw * .78, name, size, fill, 'start'))
    return ''.join(o)


def img(src, w, h, extra=''):
    return f'<img src="{src}" alt="" style="width:{w}px;height:{h}px;object-fit:contain;{extra}">'


def lum(hexcol):
    rr, gg, bb = (int(hexcol[i:i + 2], 16) for i in (1, 3, 5))
    return round(0.299 * rr + 0.587 * gg + 0.114 * bb)


def blur(id_, sd):
    return f'<defs><filter id="{id_}" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="{sd}"/></filter></defs>'


# ---------- postacie ----------
NAT = dict(bg='#C9D3DA', hair='#3B2A22', skin='#E3B48F', brow='#3B2A22', eye='#2A2D34',
           lip='#B5575A', gl='#1E2024', cloth='#3E5C76', nose='#C99673')
CLS = dict(bg='#2A2D34', hair=HAIR, skin=SKIN, brow=BROW, eye=PAPER, lip=ORANGE, gl=CYAN,
           cloth=CLOTH, nose=None)


def face(x, y, k=1, col=NAT, glasses=True, bg=True, glw=7, **over):
    """Portret en face, środek głowy w (x,y); przy k=1 zajmuje 360x460 (od -180,-200)."""
    cc = {**col, **over}
    sk = cc['skin']
    nk, er = cc.get('neck') or sk, cc.get('ear') or sk
    o = []
    if bg:
        o.append(r(-180, -200, 360, 460, cc['bg']))
    o.append(p('M-120 30 Q-132 -152 0 -160 Q132 -152 120 30 L124 120 Q60 100 0 100 Q-60 100 -124 120 Z', cc['hair']))
    o.append(p('M-180 260 L-180 222 Q-172 152 -52 134 L52 134 Q172 152 180 222 L180 260 Z', cc['cloth']))
    o.append(r(-36, 80, 72, 62, nk))
    o += [e(-95, 4, 13, 24, er), e(95, 4, 13, 24, er), e(0, 0, 95, 122, sk)]
    o.append(p('M-104 -6 Q-114 -152 0 -152 Q114 -152 104 -6 Q98 -78 46 -96 Q-6 -72 -66 -90 Q-100 -62 -104 -6 Z',
               cc['hair']))
    for s in (-1, 1):
        o.append(p(f'M{-66 * s} -40 Q{-44 * s} -54 {-20 * s} -43', st=cc['brow'], sw=9))
        o.append(e(-42 * s, -12, 12, 7, cc['eye']))
    if cc.get('nose'):
        o.append(p('M2 -2 L-9 36 Q0 42 10 36', st=cc['nose'], sw=4))
    o.append(e(0, 64, 27, 10, cc['lip']))
    if glasses:
        gc = cc['gl']
        o += [r(-75, -33, 59, 42, st=gc, sw=glw, rx=13), r(16, -33, 59, 42, st=gc, sw=glw, rx=13),
              l(-16, -15, 16, -15, gc, glw), l(-75, -18, -96, -22, gc, glw), l(75, -18, 96, -22, gc, glw)]
    return g(''.join(o), x, y, k)


def mono(col, bgc, **over):
    """Paleta twarzy, w której wszystko ma jeden kolor (np. maska 'osoba')."""
    d = {k_: col for k_ in CLS}
    d.update(bg=bgc, nose=None, **over)
    return d


def hand(x, y, k=1, fill='#E3B48F'):
    d = 'M-30 60 L-34 -10 Q-36 -30 -22 -30 L-20 -60 Q-18 -74 -6 -72 L-4 -82 Q0 -94 12 -90 L14 -80 Q26 -84 28 -70 L28 -54 Q40 -56 40 -42 L38 20 Q36 50 22 60 Z'
    return g(p(d, fill), x, y, k)


def person(x, y, k=1, fill=ORANGE):
    """Sylwetka: głowa + tułów, stopy w (x, y)."""
    return g(c(0, -150, 34, fill) + p('M-58 0 L-50 -88 Q-46 -110 -20 -112 L20 -112 Q46 -110 50 -88 L58 0 Z', fill), x, y, k)


def sheep(x, y, k=1, wool='#F2EFE9', head='#2A2D34', leg=None, flip=False):
    leg = leg or head
    o = [r(-40, 14, 11, 40, leg, rx=4), r(-16, 18, 11, 38, leg, rx=4), r(14, 18, 11, 38, leg, rx=4),
         r(36, 14, 11, 40, leg, rx=4)]
    for cx, cy, rr in [(-42, -6, 30), (-14, -24, 32), (18, -24, 32), (44, -6, 30), (-26, 14, 28), (2, 16, 30),
                       (30, 14, 28), (0, -4, 40)]:
        o.append(c(cx, cy, rr, wool))
    o += [e(-74, -20, 19, 25, head), e(-88, -38, 11, 6, head)]
    return g(''.join(o), x, y, k, flip)


SHEEP_POS = [(260, 390), (720, 400), (880, 376)]


def pasture(mode='nat', W=1200, H=560, nums=True):
    """Trzy owce na trawie; mode: nat | sem | inst | pan."""
    sky, grass = {'nat': ('#BFD7E6', '#86A866'), 'sem': ('#4C6E91', CLOTH), 'inst': ('#C7C2B8', '#C7C2B8'),
                  'pan': ('#4C6E91', CLOTH)}[mode]
    o = [r(0, 0, W, H * .38, sky), r(0, H * .38, W, H * .62, grass)]
    if mode == 'nat':
        o += [c(1060, 80, 46, '#F4D35E'), e(260, 90, 90, 26, '#FFFFFF', op=.8), e(560, 60, 70, 20, '#FFFFFF', op=.8)]
    insts = [ORANGE, CYAN, YELLOW]
    for i, (sx, sy) in enumerate(SHEEP_POS):
        sy = sy * H / 560
        if mode == 'nat':
            o.append(sheep(sx, sy, 1.7))
        else:
            col = '#F2EFE9' if mode == 'sem' else insts[i]
            o.append(sheep(sx, sy, 1.7, col, col))
            if mode in ('inst', 'pan') and nums:
                o.append(t(sx + 10, sy + 14, str(i + 1), 64, INK, w=700, f=F_H))
    return ''.join(o)


_CLIP = [0]


def panel(inner, x, y, w, h, vw, vh, st=LINE, rx=16):
    """Wstawia rysunek o rozmiarze vw x vh w prostokąt (x,y,w,h), z ramką."""
    k = min(w / vw, h / vh)
    ox, oy = x + (w - vw * k) / 2, y + (h - vh * k) / 2
    _CLIP[0] += 1
    clip = f'clip{_CLIP[0]}'  # id musi być unikalne w całym dokumencie (ukryte slajdy psują odwołania)
    return (f'<defs><clipPath id="{clip}"><rect x="{ox}" y="{oy}" width="{vw * k}" height="{vh * k}" rx="{rx}"/></clipPath></defs>'
            f'<g clip-path="url(#{clip})">' + g(inner, ox, oy, k) + '</g>'
            + (r(ox, oy, vw * k, vh * k, st=st, sw=2, rx=rx) if st else ''))


# mozaika z okładki: 12x15, '.' = tło (szachownica)
MOSAIC = ["...hhhhhh...", "..hhhhhhhh..", ".hhhhhhhhhh.", ".hhsssssshh.", ".hssssssssh.", ".hsbbssbbsh.",
          ".hgggssgggh.", ".gg.gggg.gg.", ".hgggssgggh.", ".hsssoosssh.", "..ssssssss..", "..ssmmmmss..",
          "...ssssss...", "....ssss....", ".cccccccccc."]
MCOL = dict(h=HAIR, s=SKIN, b=BROW, g=CYAN, o='#C98B5A', m=ORANGE, c=CLOTH)


def mosaic_col(i, j, ch):
    return MCOL.get(ch) or ('#1A1C22' if (i + j) % 2 == 0 else DARK)


# ---------- składanie strony ----------
def render(sd, n, total):
    bg, fg, mut = (DARK, PAPER, MUTED_D) if sd['dark'] else (LIGHT, INK, MUTED)
    if sd['raw']:
        body = sd['raw']
    else:
        body = (f'<h2 style="font-family:{F_H};font-weight:600;font-size:{sd["ts"]}px;line-height:1.15;color:{fg}">{sd["title"]}</h2>'
                f'<div style="flex:1;min-height:0;display:flex;align-items:center;justify-content:center">{sd["vis"]}</div>')
        if sd['cap']:
            body += f'<p style="font-size:30px;line-height:1.4;color:{fg};text-align:center">{sd["cap"]}</p>'
    foot = (f'<p style="position:absolute;left:128px;bottom:56px;font-size:22px;color:{mut};letter-spacing:1px;text-transform:uppercase">{sd["sec"]}</p>'
            f'<p style="position:absolute;right:128px;bottom:56px;font-family:{F_M};font-size:22px;color:{mut}">{n:02d} / {total}</p>')
    return (f'<section style="background:{bg};color:{fg};font-family:{F_B};padding:100px 128px 120px;'
            f'display:flex;flex-direction:column;gap:32px">{body}{foot}<aside>{html.escape(sd["notes"])}</aside></section>')


VIEWER = """<style>
html,body{margin:0;height:100%;background:#000;overflow:hidden}
section{position:absolute;left:0;top:0;width:1920px;height:1080px;box-sizing:border-box;overflow:hidden;transform-origin:0 0}
section:not(.on){display:none!important}
section p,section h1,section h2,section h3{margin:0}
section aside{display:none}
#n{position:fixed;left:0;right:0;bottom:0;max-height:45%;overflow:auto;background:#000d;color:#eee;font:20px/1.5 sans-serif;padding:16px 24px;white-space:pre-wrap;display:none}
@media print{@page{size:1920px 1080px;margin:0}html,body{overflow:visible;height:auto}
section,section:not(.on){position:relative!important;transform:none!important;display:flex!important;break-after:page}#n{display:none!important}}
</style>
<div id="n"></div>
<script>
const S=[...document.querySelectorAll('section')],N=document.getElementById('n');
let i=(+location.hash.slice(1)||1)-1;
function show(){
  i=Math.max(0,Math.min(S.length-1,i));history.replaceState(null,'','#'+(i+1));
  const k=Math.min(innerWidth/1920,innerHeight/1080);
  S.forEach((s,j)=>{s.classList.toggle('on',j==i);s.style.transform='translate('+(innerWidth-1920*k)/2+'px,'+(innerHeight-1080*k)/2+'px) scale('+k+')'});
  const a=S[i].querySelector('aside');N.textContent=a?a.textContent:'';
}
addEventListener('resize',show);
addEventListener('keydown',e=>{
  if(['ArrowRight','ArrowDown','PageDown',' '].includes(e.key))i++;
  else if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key))i--;
  else if(e.key=='Home')i=0;else if(e.key=='End')i=S.length;
  else if(e.key=='n')N.style.display=N.style.display=='block'?'none':'block';
  else if(e.key=='f')document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();
  else return;
  e.preventDefault();show();
});
addEventListener('click',e=>{if(e.target.closest('#n'))return;i+=e.clientX>innerWidth/3?1:-1;show()});
show();
</script>"""


def build():
    total = len(SLIDES)
    page = (f'<!doctype html><html lang="pl"><meta charset="utf-8"><title>Gdzie kończy się twarz?</title>'
            f'<link rel="stylesheet" href="{FONTS}">'
            + ''.join(render(sd, n + 1, total) for n, sd in enumerate(SLIDES)) + VIEWER + '</html>')
    (ROOT / 'slajdy.html').write_text(page)
    print(f'slajdy.html: {total} slajdów')


# ---------- slajdy ----------
SLIDES = []
SEC = ['']


def section(name):
    SEC[0] = name


def slide(title, vis='', notes='', cap='', dark=False, raw=None, title_size=56):
    SLIDES.append(dict(title=title, vis=vis, notes=notes, cap=cap, dark=dark, raw=raw, sec=SEC[0], ts=title_size))


def statement(text, notes, kicker='', dark=True, size=80):
    fg = PAPER if dark else INK
    raw = (f'<div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:32px">'
           + (f'<p style="font-family:{F_H};font-weight:600;font-size:26px;color:{ORANGE};letter-spacing:4px;text-transform:uppercase">{kicker}</p>' if kicker else '')
           + f'<h1 style="font-family:{F_H};font-weight:700;font-size:{size}px;line-height:1.12;color:{fg};width:1500px">{text}</h1></div>')
    slide('', notes=notes, dark=dark, raw=raw)


# =====================================================================
section('Wstęp')

slide('', dark=True, raw=(
    '<div style="position:absolute;left:1180px;top:150px;width:624px;height:780px">'
    + S(grid(0, 0, 52, MOSAIC, mosaic_col), w=624, h=780) + '</div>'
    f'<div style="display:flex;flex-direction:column;justify-content:center;gap:28px;width:1000px;flex:1">'
    f'<p style="font-family:{F_H};font-weight:600;font-size:26px;color:{ORANGE};letter-spacing:4px;text-transform:uppercase">Wykład · Widzenie komputerowe</p>'
    f'<h1 style="font-family:{F_H};font-weight:700;font-size:104px;line-height:1.08;color:{PAPER}">Gdzie kończy się twarz?</h1>'
    f'<p style="font-size:32px;line-height:1.4;color:#B9C0C6;width:820px">Segmentacja obrazów: od pojedynczego piksela do znaczenia.</p>'
    f'<p style="font-family:{F_M};font-size:24px;color:#6E7A82;letter-spacing:1px">Leon Woźniak · Piotr Kubicki</p></div>'),
    notes="""[ok. 2 min · start 0:00]

Dzień dobry, witam wszystkich serdecznie. Ja nazywam się Leon Woźniak i razem z Piotrkiem Kubickim przygotowaliśmy prezentację na temat segmentacji obrazów.

Zacznę od obrazka po prawej. To 180 kolorowych kwadratów ułożonych w siatkę. Nic więcej. A jednak każdy z was widzi w nich twarz w okularach. Nikt nie podpisał, które kwadraty to włosy, które skóra, a które okulary. Wasz mózg zrobił to sam, w ułamku sekundy.""")

_nums = [[str(lum(mosaic_col(i, j, ch))) for i, ch in enumerate(row)] for j, row in enumerate(MOSAIC)]
slide('Dla komputera zdjęcie to tabela liczb', S(
    grid(100, 0, 40, MOSAIC, mosaic_col),
    t(340, 650, 'to widzicie wy', 28, MUTED),
    arr(630, 300, 740, 300, ORANGE, 6),
    grid(800, 0, 40, MOSAIC, lambda i, j, ch: '#FFFFFF', st=LINE, nums=_nums, nsize=15, ncol=INK),
    t(1040, 650, 'to „widzi” komputer: jasność każdego piksela', 28, MUTED), w=1400, h=670),
    cap='Żeby zobaczył twarz, musi każdemu pikselowi przypisać znaczenie. To jest segmentacja.',
    notes="""Komputer tego nie potrafi. Dla niego zdjęcie to tabela liczb. Żeby zobaczył w nim twarz, włosy czy okulary, musi każdemu pikselowi przypisać znaczenie. To właśnie jest segmentacja obrazu.""")

_A = ["HHHHhkSS", "HHHhkkSS", "HHHHhkkS", "HHhkkSSS", "HHHhkSSS", "HHHHhkSS"]
_B = ["SSSmffmS", "SSmffmSS", "SSmffmSS", "SSSmffmS", "SSmffmSS", "SSSmfmSS"]
_zc = dict(H='#3B2A22', h='#6E4E3C', k='#B08566', S='#E3B48F', f='#1E2024', m='#7A6656')
slide('Gdzie kończy się twarz, a zaczynają włosy?', S(
    face(300, 300, 1.15),
    c(398, 150, 46, st=ORANGE, sw=5), c(355, 285, 46, st=CYAN, sw=5),
    l(444, 150, 760, 100, ORANGE, 3, '8 8'), l(400, 285, 1160, 330, CYAN, 3, '8 8'),
    grid(760, 60, 46, _A, _zc), p('M940 50 L948 340', st=ORANGE, sw=5, dash='10 8'),
    p('M900 50 L912 340', st=ORANGE, sw=5, dash='10 8', op=.5),
    t(944, 390, 'włosy czy skóra?', 30, ORANGE, w=600),
    grid(1160, 220, 46, _B, _zc), p('M1236 210 L1236 500', st=CYAN, sw=5, dash='10 8'),
    p('M1300 210 L1296 500', st=CYAN, sw=5, dash='10 8', op=.5),
    t(1344, 550, 'skóra czy oprawka?', 30, CYAN, w=600)),
    notes="""Pytanie z tytułu, gdzie kończy się twarz, brzmi niewinnie. Ale to dokładnie ten problem, z którym mierzy się każdy taki system: gdzie kończy się twarz, a zaczynają włosy? Gdzie kończy się skóra, a zaczyna oprawka okularów?""")


def _icon_grid(x, y):
    return grid(x - 45, y - 45, 30, ["abb", "aab", "aaa"], dict(a=SKIN, b=HAIR), gap=4)


def _icon_layers(x, y):
    return ''.join(r(x - 60, y - 50 + i * 26, 120, 22, col, rx=4) for i, col in enumerate([CYAN, YELLOW, SKIN, GRAY]))


def _icon_cam(x, y):
    return r(x - 60, y - 36, 90, 72, PAPER, rx=12) + p(f'M{x + 34} {y - 14} L{x + 64} {y - 34} L{x + 64} {y + 34} L{x + 34} {y + 14} Z', PAPER) + c(x - 15, y, 20, ORANGE)


def _icon_phone(x, y):
    return r(x - 34, y - 58, 68, 116, PAPER, rx=12) + r(x - 26, y - 46, 52, 84, CLOTH, rx=4) + c(x, y - 10, 12, SKIN)


_steps = [('Czym jest segmentacja', _icon_grid), ('50 lat historii', _icon_layers),
          ('Pokaz na żywo z kamerą', _icon_cam), ('Na co dzień i czego jeszcze nie umiemy', _icon_phone)]
slide('Plan', S(
    l(200, 260, 1400, 260, '#2A2D34', 6),
    *[c(200 + i * 400, 260, 110, CARD_D, '#2A2D34', 4) + fn(200 + i * 400, 260)
      + t(200 + i * 400, 70, f'0{i + 1}', 30, ORANGE, f=F_M)
      + tm(200 + i * 400, 430, ([name] if len(name) < 24 else ['Na co dzień', 'i czego jeszcze nie umiemy']), 32,
           fill=PAPER, w=600, f=F_H) for i, (name, fn) in enumerate(_steps)]), dark=True,
    notes="""Plan jest prosty. Najpierw czym jest segmentacja. Potem jak przez pięćdziesiąt lat uczyliśmy komputery ją robić. W połowie pokaz na żywo z kamerą. A na koniec gdzie spotykacie ją na co dzień i czego jeszcze nie umiemy.""")

slide('Te kolory będą wracać', S(
    face(420, 290, 1.25, CLS),
    legend(900, 90, [(CYAN, 'okulary'), (SKIN, 'skóra'), (HAIR, 'włosy'), (BROW, 'brwi'),
                     (ORANGE, 'usta'), (CLOTH, 'ubranie'), ('#2A2D34', 'tło')], 40, 52, 70)),
    notes="""Jedna wskazówka na resztę wykładu: kolory z tego obrazka będą wracać. Turkus to zawsze okulary, beż to skóra, fiolet to włosy.""")

# =====================================================================
section('Problem')

slide('Dwie twarze, czy wazon?', img('grafiki/rubin_vase.png', 1000, 667),
      notes="""[ok. 3 min · start 0:02]

Ten obrazek pewnie znacie. To wazon Rubina, nazwany od duńskiego psychologa, który opisał go ponad sto lat temu. Jedni widzą tu wazon, inni dwie twarze patrzące na siebie. Można się przełączać, ale nie da się zobaczyć obu naraz.""")

_vz = ["11110000", "11100000", "11000000", "11100000", "11110000", "11111000"]
slide('Każdy piksel jest jednoznaczny', (
    '<div style="display:flex;align-items:center;gap:72px">'
    + '<div style="position:relative">' + img('grafiki/rubin_vase.png', 720, 480)
    + f'<div style="position:absolute;left:300px;top:250px;width:90px;height:90px;border:5px solid {ORANGE};border-radius:8px"></div></div>'
    + '<div style="width:640px;height:620px">' + S(
        grid(80, 20, 62, _vz, {'1': '#FAF7F1', '0': '#14161B'}, st=LINE, nums=_vz, nsize=26,
             ncol=lambda f: INK if f == '#FAF7F1' else PAPER),
        t(328, 450, 'tylko dwie wartości: 0 albo 1', 30, INK, w=600),
        t(328, 520, 'Niejednoznaczne jest dopiero:', 30, MUTED),
        t(328, 566, 'co jest obiektem, a co tłem?', 34, ORANGE, w=600), w=656, h=620) + '</div></div>'),
    notes="""Zwróćcie uwagę, że sam obrazek jest banalnie prosty: tylko czerń i jasne tło. Każdy piksel jest jednoznaczny. Niejednoznaczne jest dopiero to, co uznamy za obiekt, a co za tło.""")


def _col(src, label, sub, col):
    return (f'<div style="display:flex;flex-direction:column;align-items:center;gap:18px">'
            + img(src, 440, 293, 'border-radius:12px') +
            f'<p style="font-family:{F_H};font-weight:600;font-size:32px;color:{col}">{label}</p>'
            f'<p style="font-size:26px;color:{MUTED}">{sub}</p></div>')


slide('Ktoś musi zdecydować, co jest obiektem', (
    '<div style="display:flex;align-items:center;gap:40px">'
    + _col('grafiki/rubin_vase_decided.png', 'Osoba A zaznacza wazon', 'obiekt = środek', CYAN)
    + f'<p style="font-family:{F_H};font-size:64px;color:{GRAY}">+</p>'
    + _col('grafiki/rubin_vase_faces.png', 'Osoba B zaznacza twarze', 'obiekt = boki', CYAN)
    + f'<p style="font-family:{F_H};font-size:64px;color:{GRAY}">→</p>'
    + '<div style="display:flex;flex-direction:column;align-items:center;gap:18px">'
    + '<div style="position:relative;width:440px;height:293px">'
    + img('grafiki/rubin_vase_decided.png', 440, 293, 'border-radius:12px;position:absolute;left:0;top:0;opacity:.5')
    + img('grafiki/rubin_vase_faces.png', 440, 293, 'border-radius:12px;position:absolute;left:0;top:0;opacity:.5')
    + f'<p style="position:absolute;left:0;top:70px;width:440px;text-align:center;font-family:{F_H};font-weight:700;font-size:130px;color:{ORANGE}">?</p></div>'
    + f'<p style="font-family:{F_H};font-weight:600;font-size:32px;color:{ORANGE}">Model</p>'
    + f'<p style="font-size:26px;color:{MUTED}">sprzeczne wskazówki</p></div></div>'),
    cap='Zanim komputer cokolwiek zaznaczy, ludzie ręcznie zaznaczają obiekty na tysiącach zdjęć.',
    notes="""I to jest pierwsza ważna lekcja o segmentacji. Zanim komputer cokolwiek zaznaczy, ktoś musi zdecydować, co w ogóle jest obiektem. W praktyce robią to ludzie, którzy ręcznie zaznaczają obiekty na tysiącach zdjęć, żeby model miał się na czym uczyć. Jeśli jedna osoba zaznaczy wazon, a druga twarze, model dostanie sprzeczne wskazówki i będzie tak samo zdezorientowany jak my.

Do tego wazonu jeszcze wrócimy, na samym końcu.""")

# =====================================================================
section('Definicja')

_pix = ''.join(l(120 + i * 36, 70, 120 + i * 36, 530, '#FFFFFF', 1) for i in range(1, 10)) + \
       ''.join(l(120, 70 + j * 36, 480, 70 + j * 36, '#FFFFFF', 1) for j in range(1, 13))
slide('Segmentacja: każdemu pikselowi etykieta', S(
    f'<defs><clipPath id="fc"><rect x="120" y="70" width="360" height="460"/></clipPath></defs>',
    f'<g clip-path="url(#fc)">' + face(300, 270, 1) + f'<g opacity=".55">{_pix}</g></g>',
    r(372, 70 + 36 * 2, 36, 36, st=ORANGE, sw=5),
    t(300, 590, 'zdjęcie = siatka pikseli', 28, MUTED),
    arr(420, 160, 620, 220, ORANGE, 5),
    t(640, 200, 'f( x, y )  →  c', 64, INK, 'start', 500, F_M),
    t(640, 290, 'f( 7, 2 )  =  2   włosy', 52, HAIR, 'start', 600, F_M),
    t(640, 370, 'x, y — położenie piksela,  c — numer kategorii', 30, MUTED, 'start'),
    legend(640, 420, [('#2A2D34', '0 = tło'), (SKIN, '1 = twarz'), (HAIR, '2 = włosy')], 30, 34, 52)),
    notes="""[ok. 5 min · start 0:05]

Powiedzmy dokładnie, co robi segmentacja. Zdjęcie to siatka pikseli. Segmentacja polega na tym, żeby każdemu pikselowi przypisać etykietę: to jest tło, to twarz, to włosy. Można to zapisać jako funkcję, którą widać na slajdzie: bierze położenie piksela i zwraca numer kategorii.""")


def _house(fill, stroke, labels, lcol, lbg=None):
    sky, sun, roof, wall, door, grass = fill
    o = [r(0, 0, 560, 400, sky, stroke, 4), c(470, 80, 46, sun, stroke, 4),
         p('M90 190 L230 80 L370 190 Z', roof, stroke, 4), r(110, 190, 240, 150, wall, stroke, 4),
         r(200, 250, 60, 90, door, stroke, 4), p('M0 340 Q140 320 280 338 T560 334 L560 400 L0 400 Z', grass, stroke, 4)]
    for (x, y), s in zip([(70, 60), (470, 92), (230, 160), (160, 280), (230, 304), (460, 380)], labels):
        if lbg:
            o.append(c(x, y - 11, 24, lbg))
        o.append(t(x, y, s, 32, lcol, w=700, f=F_H))
    return ''.join(o)


_fills = ['#BFD7E6', '#F4D35E', ORANGE, SKIN, BROW, '#86A866']
slide('Kolorowanka z numerkami, tylko odwrotnie', S(
    t(300, 30, 'Kolorowanka: numer → kolor', 32, INK, w=600, f=F_H),
    g(_house(['#FFFFFF'] * 6, INK, '123456', INK), 20, 60),
    legend(20, 490, [(col, f'{i + 1}') for i, col in enumerate(_fills[:3])], 26, 30, 40),
    legend(160, 490, [(col, f'{i + 4}') for i, col in enumerate(_fills[3:])], 26, 30, 40),
    arr(640, 260, 940, 260, ORANGE, 6), t(790, 230, 'odwrotnie', 30, ORANGE, w=600),
    t(1280, 30, 'Segmentacja: kolor → numer', 32, INK, w=600, f=F_H),
    g(_house(_fills, None, '??????', '#FFFFFF', ORANGE), 1000, 60),
    t(1280, 520, 'setki tysięcy pól, nikt nie narysował konturów', 28, MUTED)),
    notes="""Najłatwiej wyobrazić sobie kolorowankę z numerkami. Każde pole ma numer, a numer mówi, jakim kolorem je pomalować. Segmentacja to zadanie odwrotne: dostajemy gotowy, pomalowany obrazek i musimy sami wpisać numer do każdego pola. Tyle że pól jest kilkaset tysięcy, a nikt nie narysował konturów.""")

_g6 = ["000000", "000000", "001100", "011110", "001100", "000000"]
slide('Najprostszy przykład: 6 × 6 pikseli, dwie kategorie', S(
    grid(160, 20, 96, _g6, {'0': '#2A2D34', '1': SKIN}, gap=4, nums=_g6, nsize=40,
         ncol=lambda f: PAPER if f == '#2A2D34' else INK),
    legend(900, 200, [('#2A2D34', '0 = tło'), (SKIN, '1 = obiekt')], 44, 56, 90)),
    notes="""Po lewej najprostszy przykład: obraz sześć na sześć pikseli i dwie kategorie. Zero to tło, jedynka to obiekt.""")


def _three(items):
    """Trzy panele z podpisami; items: (rysunek 360x460, tytuł, podpis)."""
    o = []
    for i, (inner, title, sub) in enumerate(items):
        x = 40 + i * 530
        o += [panel(inner, x, 0, 460, 470, 360, 460), t(x + 230, 530, title, 34, INK, w=600, f=F_H),
              t(x + 230, 580, sub, 26, MUTED)]
    return S(*o, h=600)


slide('Rozpoznawanie, wykrywanie, segmentacja', _three([
    (g(face(0, 0) + r(-60, -180, 120, 44, ORANGE, rx=22) + t(0, -148, 'twarz', 26, '#FFFFFF', w=600), 180, 200),
     'Rozpoznawanie', '„na zdjęciu jest twarz”'),
    (g(face(0, 0) + r(-112, -132, 224, 274, st=ORANGE, sw=6, rx=6), 180, 200),
     'Wykrywanie', '„twarz jest w tym prostokącie”'),
    (g(face(0, 0, 1, NAT) + g(e(0, 0, 95, 122, ORANGE) + e(-95, 4, 13, 24, ORANGE) + e(95, 4, 13, 24, ORANGE), extra='opacity=".75"'), 180, 200),
     'Segmentacja', '„twarz to dokładnie te piksele”')]),
    notes="""Porównajmy to z dwoma zadaniami, które pewnie już znacie. Rozpoznawanie obrazu mówi: na tym zdjęciu jest twarz. Wykrywanie obiektów mówi: twarz jest w tym prostokącie. Segmentacja mówi: twarz to dokładnie te piksele, co do jednego.""")


def _ct(x, y, k=1, tumor=26, outline=True):
    o = [e(0, 0, 230, 170, '#2A2D34'), e(0, 0, 214, 156, '#5B6168'), e(-80, -10, 70, 90, '#7D858D'),
         e(80, -10, 70, 90, '#7D858D'), e(0, 90, 40, 34, '#B9C0C6'), c(-60, -30, tumor, '#C9CED3')]
    if outline:
        o.append(c(-60, -30, tumor + 4, st=ORANGE, sw=5))
    return g(''.join(o), x, y, k)


slide('Czego prostokąt nie umożliwi', S(
    panel(r(0, 0, 600, 400, '#9DB4C0') + r(40, 40, 180, 140, '#C9D3DA') + r(380, 60, 160, 340, '#7C6A58')
          + person(300, 400, 1.6, '#3E5C76'), 0, 40, 360, 240, 600, 400),
    arr(375, 160, 425, 160, ORANGE, 5),
    panel(r(0, 0, 600, 400, '#F4D35E') + r(0, 220, 600, 180, '#E9C98F') + c(480, 70, 40, '#FFFFFF')
          + p('M0 220 Q150 190 300 215 T600 210 L600 230 L0 230 Z', '#4C9DB8') + person(300, 400, 1.6, '#3E5C76'),
          440, 40, 360, 240, 600, 400),
    t(400, 360, 'podmienić tło za osobą', 34, INK, w=600, f=F_H),
    _ct(1040, 160, .75), t(1040, 310, 'przed leczeniem', 26, MUTED),
    _ct(1440, 160, .75, tumor=14), t(1440, 310, 'po leczeniu', 26, MUTED),
    arr(1215, 160, 1265, 160, ORANGE, 5),
    t(1240, 360, 'zmierzyć wielkość guza', 34, INK, w=600, f=F_H),
    t(800, 470, 'Do obu potrzeba granicy co do piksela, a nie prostokąta.', 30, MUTED), h=500),
    notes="""Dlatego można dzięki niej zrobić rzeczy, których prostokąt nie umożliwi: podmienić tło za osobą albo zmierzyć wielkość guza na zdjęciu z tomografu.""")

slide('Jedynka mówi „obiekt”, ale nie mówi który', S(
    r(300, 20, 1000, 500, '#2A2D34', rx=16),
    person(680, 520, 2.3, SKIN), person(900, 520, 2.3, SKIN),
    t(680, 360, '1', 72, INK, w=700, f=F_M), t(900, 360, '1', 72, INK, w=700, f=F_M),
    t(800, 590, 'Dwie osoby, ta sama etykieta. Która to która?', 32, ORANGE, w=600), h=620),
    notes="""Jest jeden haczyk. Jedynka mówi „obiekt”, ale nie mówi, który. Jeśli na zdjęciu są dwie osoby, obie dostaną tę samą etykietę. O tym następny slajd.""")

# =====================================================================
section('Rodzaje segmentacji')

slide('Ten sam obrazek: trzy owce na trawie', S(panel(pasture('nat'), 200, 0, 1200, 560, 1200, 560), h=580),
      notes="""[ok. 5 min · start 0:10]

Ten sam obrazek, trzy owce na trawie, i trzy sposoby, żeby go posegmentować.""")


def _tax(mode, lg, cap_):
    return S(panel(pasture('nat'), 0, 0, 380, 177, 1200, 560), t(190, 214, 'oryginał', 24, MUTED),
             panel(pasture(mode), 420, 0, 1180, 551, 1200, 560),
             legend(0, 290, lg, 28, 32, 52), h=560)


slide('1. Semantyczna: liczy się tylko rodzaj rzeczy', _tax('sem', [('#F2EFE9', 'owca'), (CLOTH, 'trawa'), ('#4C6E91', 'niebo')], ''),
      cap='Wszystkie owce mają jeden kolor. Dwie z prawej zlały się w jedną plamę: ile ich jest?',
      notes="""Pierwszy, po lewej, to segmentacja semantyczna. Liczy się tylko rodzaj rzeczy. Wszystkie owce dostają ten sam kolor, bo wszystkie są owcami. Jeśli stoją blisko siebie, zlewają się w jedną białą plamę i nie da się ich policzyć.""")

slide('2. Instancyjna: każda owca osobno', _tax('inst', [(ORANGE, 'owca 1'), (CYAN, 'owca 2'), (YELLOW, 'owca 3'), ('#C7C2B8', 'bez etykiety')], ''),
      cap='Wiemy, że są trzy i gdzie stoi każda. Trawa nikogo nie obchodzi.',
      notes="""Drugi, w środku, to segmentacja instancyjna. Tu każda owca dostaje własny kolor, więc wiemy, że są trzy i gdzie dokładnie stoi każda z nich. Za to trawa nikogo nie obchodzi i zostaje nieoznaczona.""")

slide('3. Panoptyczna: wszystko naraz', _tax('pan', [(ORANGE, 'owca 1'), (CYAN, 'owca 2'), (YELLOW, 'owca 3'), (CLOTH, 'trawa'), ('#4C6E91', 'niebo')], ''),
      cap='Rzeczy policzalne (owce, ludzie, auta) osobno + niepoliczalne (trawa, niebo, droga) jako tło.',
      notes="""Trzeci, po prawej, to segmentacja panoptyczna, czyli wszystko naraz: każda owca osobno, a do tego trawa jako tło. Rozróżniamy tu rzeczy, które da się policzyć, jak owce, ludzie czy samochody, oraz takie, których się nie liczy, jak trawa, niebo czy droga.""")


def _street(mode='pan', W=800, H=500):
    """Ulica z góry-z przodu: droga jako jeden obszar, piesi osobno."""
    o = [r(0, 0, W, 180, '#4C6E91' if mode != 'nat' else '#BFD7E6'),
         r(0, 180, W, 320, '#6B6B6B' if mode != 'nat' else '#9A9A9A'),
         p(f'M0 500 L{W * .38} 180 L{W * .62} 180 L{W} 500 Z', '#7E5A86' if mode != 'nat' else '#55585C'),
         p(f'M0 500 L{W * .30} 180 L{W * .38} 180 L{W * .08} 500 Z', '#C986B8' if mode != 'nat' else '#B5B5B5'),
         p(f'M{W} 500 L{W * .70} 180 L{W * .62} 180 L{W * .92} 500 Z', '#C986B8' if mode != 'nat' else '#B5B5B5')]
    peds = [(170, 420, ORANGE, -1), (330, 300, CYAN, 1), (620, 380, YELLOW, -1)]
    for x, y, col, d in peds:
        o.append(person(x, y, .7, col if mode == 'pan' else '#DC143C'))
        if mode == 'pan':
            o.append(arr(x, y - 50, x + d * 90, y - 50, col, 6, 20))
    o.append(r(430, 330, 150, 80, '#2A3A8E', rx=14))
    return ''.join(o)


def _call(W=800, H=500):
    return (r(0, 0, W, H, '#2A2D34') + g(face(0, 0, 1, mono(ORANGE, '#2A2D34'), glasses=False), W / 2, 250, 1.05)
            + legend(30, 30, [(ORANGE, 'osoba'), ('#2A2D34', 'tło')], 30, 34, 50, PAPER))


slide('Który sposób wybrać? Zależy, do czego to służy', S(
    panel(_call(), 40, 0, 700, 438, 800, 500),
    t(390, 500, 'Rozmycie tła w wideorozmowie', 32, INK, w=600, f=F_H),
    t(390, 548, 'semantyczna wystarczy: osoba albo tło', 28, MUTED),
    panel(_street(), 860, 0, 700, 438, 800, 500),
    t(1210, 500, 'Samochód autonomiczny', 32, INK, w=600, f=F_H),
    t(1210, 548, 'panoptyczna: droga jako całość, każdy pieszy osobno', 28, MUTED), h=580),
    notes="""Który sposób wybrać, zależy od tego, do czego to ma służyć. Rozmycie tła w wideorozmowie? Wystarczy pierwszy: osoba albo tło. Samochód autonomiczny? Potrzebuje trzeciego. Drogę może traktować jako jedną płaszczyznę, ale każdego pieszego musi śledzić osobno, bo każdy idzie w inną stronę.""")

# =====================================================================
section('Historia')


def _wave(y0, i, W=1300):
    return ' '.join(f'L{x} {y0 + 12 * math.sin(x / 110 + i * 1.7):.1f}' for x in range(0, W + 1, 20))


_layers = [('2015', 'sieć uczy się segmentacji sama', CYAN), ('2012', 'sieci neuronowe jako pomocnik', YELLOW),
           ('2000', 'cały obraz naraz: GrabCut', SKIN), ('1990', 'aktywne kontury, wododziały', '#A7AEB5'),
           ('1970', 'progowanie', '#6E7A82')]
_st = []
for i, (yr, name, col) in enumerate(_layers):
    y0, y1 = 40 + i * 112, 40 + (i + 1) * 112
    top = _wave(y0, i).replace('L', 'M', 1)
    bot = ' '.join(reversed([f'L{x} {y1 + 12 * math.sin(x / 110 + (i + 1) * 1.7):.1f}' for x in range(0, 1301, 20)]))
    _st += [p(f'{top} {bot} Z', col), t(60, y0 + 70, yr, 36, DARK, 'start', 500, F_M),
            t(200, y0 + 70, name, 34, DARK, 'start', 600, F_H)]
slide('Krótka historia, ułożona jak warstwy skał', S(
    g(''.join(_st), 150, 0), t(1500, 70, 'najnowsze', 26, MUTED_D, 'start'), arr(1480, 100, 1480, 560, MUTED_D, 4),
    t(1500, 580, 'najstarsze', 26, MUTED_D, 'start'), h=640), dark=True,
    notes="""[ok. 4 min · start 0:15]

Teraz krótka historia, ułożona jak warstwy skał. Nowe metody nie wyrzuciły starych, tylko się na nich nadbudowały.""")

_prod = [c(0, 0, 50, '#C9CED3'), c(0, 0, 50, '#C9CED3'),
         p('M0 0 L50 -18 A50 50 0 1 0 50 18 Z', '#C9CED3'), c(0, 0, 50, '#C9CED3')]
_bin = [c(0, 0, 50, '#FFFFFF'), c(0, 0, 50, '#FFFFFF'), p('M0 0 L50 -18 A50 50 0 1 0 50 18 Z', '#FFFFFF'),
        c(0, 0, 50, '#FFFFFF')]
slide('Najstarsze warstwy wciąż pracują: kamera nad taśmą', S(
    r(330, 30, 120, 80, '#3C4248', rx=12), r(370, 110, 40, 30, '#3C4248'),
    p('M390 140 L120 380 L680 380 Z', YELLOW, op=.18),
    r(60, 390, 700, 40, '#3C4248', rx=20), *[c(80 + i * 66, 410, 14, GRAY) for i in range(11)],
    *[g(sh, 140 + i * 175, 330) for i, sh in enumerate(_prod)],
    arr(800, 230, 900, 230, ORANGE, 6),
    r(940, 60, 620, 340, '#000000', rx=12),
    *[g(sh, 1020 + i * 150, 230) for i, sh in enumerate(_bin)],
    *[t(1020 + i * 150, 350, m, 48, col, w=700) for i, (m, col) in enumerate([('✓', '#7FBF6A'), ('✓', '#7FBF6A'), ('✗', ORANGE), ('✓', '#7FBF6A')])],
    t(1250, 450, 'próg jasności: produkt albo tło', 28, MUTED), h=500),
    notes="""Najstarsze wciąż się przydają, na przykład w fabrykach, gdzie kamera nad taśmą sprawdza, czy produkt ma właściwy kształt.""")


def _mug(fill='#3A3F47', handle=True):
    return (p('M-70 -80 L70 -80 L60 80 Q0 96 -60 80 Z', fill)
            + (p('M66 -40 Q130 -40 120 10 Q112 50 60 46', st=fill, sw=22) if handle else ''))


_bars = []
for k_ in range(32):
    v = k_ * 8 + 4
    hgt = 260 * math.exp(-((v - 55) / 22) ** 2) * .45 + 260 * math.exp(-((v - 205) / 20) ** 2)
    _bars.append(r(640 + k_ * 12, 470 - hgt, 10, hgt, '#3A3F47' if v < 130 else '#C9BFA8'))
slide('Progowanie: jedna liczba dzieli obraz na dwie części', S(
    panel(r(0, 0, 420, 420, '#E9E2D3') + e(210, 300, 120, 22, '#D5CCB9') + g(_mug(), 200, 210), 40, 40, 420, 420, 420, 420),
    t(250, 520, 'ciemny kubek na jasnym stole', 28, MUTED),
    *_bars, l(640, 472, 1030, 472, INK, 2), l(640 + 16 * 12, 120, 640 + 16 * 12, 480, ORANGE, 5, '12 8'),
    t(832, 100, 'próg', 30, ORANGE, w=600), t(700, 510, 'ciemne', 24, MUTED), t(980, 510, 'jasne', 24, MUTED),
    t(835, 560, 'histogram jasności', 28, MUTED),
    arr(1060, 260, 1140, 260, ORANGE, 6),
    panel(r(0, 0, 420, 420, '#14161B') + g(_mug('#FFFFFF'), 200, 210), 1160, 40, 420, 420, 420, 420),
    t(1370, 520, 'ciemniejsze od progu = obiekt', 28, MUTED), h=580),
    notes="""Najgłębsza warstwa, lata siedemdziesiąte: progowanie. Mówimy komputerowi, że wszystko jaśniejsze od pewnej wartości to obiekt, a reszta to tło. Świetnie działa, gdy ciemny przedmiot leży na jasnym stole.""")

_th = {k_: ('#14161B' if (v and lum(v) < 140) else '#FFFFFF') for k_, v in NAT.items()}
slide('Gorzej, gdy świat jest bardziej skomplikowany', S(
    panel(g(r(-180, -200, 180, 460, '#6E7A82') + r(0, -200, 180, 460, '#C9D3DA') + face(0, 0, 1, NAT, bg=False), 180, 200), 120, 0, 360, 460, 360, 460, rx=12),
    t(300, 510, 'zdjęcie z cieniem po lewej', 28, MUTED),
    arr(560, 230, 680, 230, ORANGE, 6), t(620, 200, 'próg', 26, ORANGE),
    panel(g(r(-180, -200, 180, 460, '#14161B') + r(0, -200, 180, 460, '#FFFFFF') + face(0, 0, 1, _th, bg=False), 180, 200), 740, 0, 360, 460, 360, 460, rx=12),
    t(920, 510, 'wynik progowania', 28, MUTED),
    tm(1160, 120, ['Włosy zlały się z cieniem.', 'Okulary, brwi i ubranie', 'to „to samo”.', 'Usta wypadły z twarzy.'],
       32, 1.5, fill=INK, a='start'), h=540),
    notes="""Gorzej, gdy świat jest bardziej skomplikowany.""")

_pear = 'M0 -150 C70 -150 90 -80 70 -30 C130 10 140 120 60 150 C20 165 -20 165 -60 150 C-140 120 -130 10 -70 -30 C-90 -80 -70 -150 0 -150 Z'


def _band(scale=None, circle=False):
    o = p(_pear, '#C9A27E')
    if circle:
        o += c(0, 0, 215, st=ORANGE, sw=10)
    else:
        o += g(p(_pear, st=ORANGE, sw=10, extra='vector-effect="non-scaling-stroke"'), 0, 0, scale)
    return o


slide('Aktywne kontury: gumka recepturka', S(
    g(_band(circle=True) + ''.join(arr(math.cos(a) * 200, math.sin(a) * 200, math.cos(a) * 160, math.sin(a) * 160, ORANGE, 4, 16)
                                    for a in [i * math.pi / 3 for i in range(6)]), 270, 260),
    g(_band(1.3), 800, 260), g(_band(1.0), 1330, 260),
    arr(520, 260, 580, 260, GRAY, 5), arr(1050, 260, 1110, 260, GRAY, 5),
    t(270, 560, 'rzucamy gumkę wokół obiektu', 30, INK, w=600, f=F_H),
    t(800, 560, 'sama się zaciska', 30, INK, w=600, f=F_H),
    t(1330, 560, 'przylega do krawędzi', 30, INK, w=600, f=F_H), h=600),
    notes="""Przełom lat osiemdziesiątych i dziewięćdziesiątych: aktywne kontury. Wyobraźcie sobie gumkę recepturkę, którą rzucamy wokół obiektu i która sama zaciska się na jego krawędziach.""")


def _terrain(x):
    return 330 + 140 * math.cos(2 * math.pi * (x - 250) / 450) + 40 * math.sin(x / 200)


_tpts = ' '.join(f'L{x} {_terrain(x):.1f}' for x in range(0, 1401, 10))
_lvl = 250
slide('Wododziały: obraz jako górzysty teren zalewany wodą', S(
    g(r(0, _lvl, 1400, 600 - _lvl, '#4C9DB8') + p(f'M0 600 {_tpts} L1400 600 Z', '#8A6F55')
      + ''.join(l(x, _terrain(x) - 4, x, 90, ORANGE, 6, '12 8') + t(x, 70, 'granica', 28, ORANGE, w=600)
                for x in (475, 925)) + l(0, _lvl, 1400, _lvl, '#2F7C96', 2)
      + ''.join(t(x, 420, 'jezioro', 26, '#FFFFFF', w=600) for x in (250, 1150))
      + t(700, _lvl + 50, 'poziom wody rośnie ↑', 26, '#FFFFFF', w=600), 100, 0),
    t(800, 640, 'jasne piksele = góry, ciemne = doliny. Gdzie spotykają się jeziora, tam jest granica.', 28, MUTED), h=660),
    notes="""Albo metoda wododziałów: traktujemy obraz jak mapę górzystego terenu, zalewamy ją wodą i patrzymy, gdzie spotykają się jeziora.""")

_gp = ["..ooo..", ".ooooo.", ".ooooo.", "..ooo..", "...o..."]
_ge, _gx, _gy, _gs = [], 300, 60, 110
for j, row in enumerate(_gp):
    for i, ch in enumerate(row):
        for di, dj in ((1, 0), (0, 1)):
            ii, jj = i + di, j + dj
            if jj < len(_gp) and ii < len(row):
                same = _gp[jj][ii] == ch
                x1, y1, x2, y2 = _gx + i * _gs, _gy + j * _gs, _gx + ii * _gs, _gy + jj * _gs
                _ge.append(l(x1, y1, x2, y2, '#8B939C' if same else '#C9CED3', 10 if same else 2))
                if not same:
                    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                    _ge.append(l(mx - dj * 50, my - di * 50, mx + dj * 50, my + di * 50, ORANGE, 6))
_gn = [c(_gx + i * _gs, _gy + j * _gs, 28, SKIN if ch == 'o' else '#3C4248') for j, row in enumerate(_gp) for i, ch in enumerate(row)]
slide('Lata 2000: komputer patrzy na cały obraz naraz', S(
    *_ge, *_gn,
    l(1100, 120, 1180, 120, '#8B939C', 10), t(1200, 130, 'podobni sąsiedzi: mocne połączenie', 28, INK, 'start'),
    l(1100, 200, 1180, 200, '#C9CED3', 2), t(1200, 210, 'różni sąsiedzi: słabe', 28, INK, 'start'),
    l(1100, 280, 1180, 280, ORANGE, 6), t(1200, 290, 'cięcie przez najsłabsze', 28, INK, 'start'),
    r(1090, 370, 480, 110, '#FFFFFF', LINE, 2, 14),
    t(1330, 418, 'Tak działa GrabCut (2004)', 30, INK, w=600, f=F_H), t(1330, 458, 'zobaczycie go za chwilę na żywo', 26, MUTED), h=560),
    notes="""Lata dwutysięczne: komputer zaczyna patrzeć na cały obraz naraz i szuka takiego podziału, w którym podobne sąsiednie piksele trafiają do tej samej grupy. Na tym działa GrabCut z 2004 roku, który za chwilę zobaczycie na żywo.""")


def _net(x, y, w=180, h=200, col='#3C4248', label=None):
    o = ''.join(r(x + i * (w / 4), y + i * 14, w / 5, h - i * 28, col, rx=6, op=1 - i * .12) for i in range(4))
    return o + (t(x + w / 2, y + h + 44, label, 26, MUTED) if label else '')


slide('Około 2012: sieć neuronowa na razie tylko pomaga', S(
    panel(g(face(0, 0), 180, 200), 0, 120, 200, 255, 360, 460), t(100, 430, 'fragment obrazu', 26, MUTED),
    arr(220, 250, 300, 250, GRAY, 5),
    _net(320, 150, 200, 200, '#6B7681', 'sieć opisuje fragment'),
    arr(560, 250, 640, 250, GRAY, 5),
    *[r(670, 120 + i * 30, 30 + (37 * i) % 90, 22, YELLOW, rx=4) for i in range(9)],
    t(720, 430, 'opis: liczby', 26, MUTED),
    arr(800, 250, 880, 250, GRAY, 5),
    r(900, 160, 320, 180, '#FFFFFF', INK, 3, 16), tm(1060, 240, ['klasyczny', 'algorytm'], 34, 1.2, fill=INK, w=600, f=F_H),
    t(1060, 430, 'on podejmuje decyzję', 26, MUTED),
    arr(1240, 250, 1320, 250, GRAY, 5),
    r(1340, 210, 200, 80, SKIN, rx=40), t(1440, 262, 'skóra', 32, INK, w=600), h=480),
    notes="""Około 2012 roku pojawiają się sieci neuronowe, ale na początku tylko jako pomocnik, który opisuje fragmenty obrazu. Decyzję wciąż podejmuje klasyczny algorytm.""")

slide('2015: sieć uczy się segmentacji sama, od początku do końca', S(
    panel(g(face(0, 0), 180, 200), 80, 60, 330, 420, 360, 460), t(245, 540, 'zdjęcie', 28, MUTED),
    arr(450, 270, 560, 270, ORANGE, 6),
    p('M600 90 L1000 190 L1000 350 L600 450 Z', '#3C4248'), tm(800, 260, ['jedna sieć', 'uczona na przykładach'], 32, 1.3, fill=PAPER, w=600, f=F_H),
    arr(1040, 270, 1150, 270, ORANGE, 6),
    panel(g(face(0, 0, 1, CLS), 180, 200), 1190, 60, 330, 420, 360, 460), t(1355, 540, 'maska', 28, MUTED), h=580),
    notes="""A w 2015 roku przychodzi przełom: sieć, która uczy się segmentacji sama, od początku do końca. O niej następny slajd.""")

# ---------- FCN ----------
CAT = '#D98E4A'


def cat(x, y, k=1, fill=CAT, det=True):
    o = [p('M110 50 Q175 20 150 -50', st=fill, sw=20), e(20, 40, 95, 60, fill), c(-75, -25, 52, fill),
         p('M-122 -40 L-115 -105 L-82 -72 Z', fill), p('M-68 -76 L-35 -105 L-30 -42 Z', fill)]
    if det:
        o += [c(-95, -32, 7, INK), c(-58, -32, 7, INK), p('M-82 -14 L-72 -14 L-77 -8 Z', INK)]
    return g(''.join(o), x, y, k)


def cat_in(px, py):
    return ((px - 20) / 95) ** 2 + ((py - 40) / 60) ** 2 <= 1 or (px + 75) ** 2 + (py + 25) ** 2 <= 52 ** 2


def cat_grid(x, y, w, h, nx, ny, on=CAT, off='#C9CED3', st=None):
    """Kot próbkowany na siatce nx x ny w obszarze (-150..170, -110..110)."""
    cw, ch = w / nx, h / ny
    o = []
    for j in range(ny):
        for i in range(nx):
            px, py = -150 + (i + .5) * 320 / nx, -110 + (j + .5) * 220 / ny
            o.append(r(x + i * cw, y + j * ch, cw + .5, ch + .5, on if cat_in(px, py) else off, st, 1))
    return ''.join(o)


slide('FCN: odpowiedź dla każdego fragmentu obrazu', S(
    panel(r(0, 0, 340, 240, '#E9E2D3') + cat(170, 125, .9), 40, 20, 300, 212, 340, 240),
    arr(370, 126, 430, 126, GRAY, 5), p('M460 40 L760 110 L760 142 L460 212 Z', '#6B7681'),
    t(610, 270, 'ściska wiedzę w jedną odpowiedź', 26, MUTED), arr(790, 126, 850, 126, GRAY, 5),
    r(880, 86, 160, 80, CAT, rx=40), t(960, 138, 'kot', 34, INK, w=600),
    t(1300, 136, 'zwykła sieć (2012–2014)', 28, MUTED),
    l(40, 310, 1560, 310, LINE, 2),
    panel(r(0, 0, 340, 240, '#E9E2D3') + cat(170, 125, .9), 40, 350, 300, 212, 340, 240),
    arr(370, 456, 430, 456, GRAY, 5), r(460, 370, 300, 172, '#6B7681', rx=10),
    t(610, 600, 'przebudowana końcówka', 26, MUTED), arr(790, 456, 850, 456, GRAY, 5),
    cat_grid(880, 350, 300, 206, 12, 8, st='#FFFFFF'),
    t(1300, 440, 'FCN (2015):', 30, INK, 'start', 600, F_H), t(1300, 480, 'mapa „kot / tło”', 28, MUTED, 'start'), h=620),
    notes="""[ok. 3,5 min · start 0:19]

W 2015 roku trzech badaczy z Berkeley zauważyło coś prostego. Istniały już sieci neuronowe, które świetnie rozpoznawały, co jest na zdjęciu, ale na końcu ściskały całą swoją wiedzę w jedną odpowiedź, na przykład „kot”. Wystarczyło przebudować końcówkę sieci tak, żeby zamiast jednej odpowiedzi dawała odpowiedź dla każdego fragmentu obrazu. Tak powstały sieci w pełni konwolucyjne, w skrócie FCN.""")

_sz = [512, 256, 128, 64, 32, 16]
_sx, _so = 40, []
for i, n_ in enumerate(_sz):
    w_ = n_ * .78
    _so += [r(_sx, 460 - w_, w_, w_, ['#AAB4BD', '#97A2AC', '#838F9A', '#6B7681', '#56616C', ORANGE][i], rx=6),
            t(_sx + w_ / 2, 510, f'{n_}×{n_}', 28, INK, f=F_M)]
    if i < 5:
        _so.append(arr(_sx + w_ + 14, 440, _sx + w_ + 70, 440, GRAY, 4, 16))
    _sx += w_ + 84
slide('Po drodze sieć wielokrotnie zmniejsza obraz', S(*_so, h=560),
      cap='Zdjęcie 512 na 512 kurczy się do 16 na 16. Tak łatwiej uchwycić całość.',
      notes="""Problem widać na diagramie. Po drodze sieć wielokrotnie zmniejsza obraz, bo tak łatwiej jej uchwycić całość. Zdjęcie 512 na 512 pikseli kurczy się do 16 na 16.""")


def _city(W, H):
    def cls(x, y):
        xr = W * (.45 + .12 * math.sin(y / H * math.pi * 1.4))
        if abs(x - xr) < W * .06:
            return '#4C9DB8'
        if math.hypot(x - W * .66, y - H * .45) < W * .17:
            return '#6B6B6B'
        if math.hypot(x - W * .2, y - H * .28) < W * .12:
            return '#7FA35F'
        return '#C9C2B4'
    return cls


def _city_coarse(W=480, H=480, n=16):
    cls, cs = _city(W, H), W / n
    return ''.join(r(i * cs, j * cs, cs + .5, cs + .5, cls((i + .5) * cs, (j + .5) * cs)) for j in range(n) for i in range(n))


def _city_fine(W=480, H=480):
    cls = _city(W, H)
    o = [r(0, 0, W, H, '#EDE8DD')]
    o += [r(i * 24 + 3, j * 24 + 3, 18, 18, {'#C9C2B4': '#ADA392'}.get(cls(i * 24 + 12, j * 24 + 12), cls(i * 24 + 12, j * 24 + 12)), rx=2)
          for j in range(20) for i in range(20)]
    pts = ' '.join(f'L{W * (.45 + .12 * math.sin(y / H * math.pi * 1.4)):.1f} {y}' for y in range(0, H + 1, 8)).replace('L', 'M', 1)
    o.append(p(pts, st='#4C9DB8', sw=W * .1))
    o += [l(W * .30, y, W * .70, y, '#8B939C', 5) for y in (140, 330)]
    return ''.join(o)


slide('Jak oglądanie Warszawy z samolotu', S(
    panel(_city_coarse(), 160, 0, 480, 480, 480, 480), t(400, 540, 'z samolotu (16 × 16): rzeka, centrum, park', 28, MUTED),
    panel(_city_fine(), 960, 0, 480, 480, 480, 480), t(1200, 540, 'z ziemi (512 × 512): ulice, mosty, kwartały', 28, MUTED),
    h=580), cap='Widać, gdzie jest rzeka, a gdzie centrum, ale pojedynczych ulic już nie.',
    notes="""To jak oglądanie Warszawy z samolotu: widać, gdzie jest rzeka, a gdzie centrum, ale pojedynczych ulic już nie.""")

slide('Odtwarzanie pełnej mapy: najpierw rozmazane plamy', S(
    blur('b1', 14), blur('b2', 3),
    panel(r(0, 0, 340, 240, '#C9CED3') + cat(170, 125, .9, det=False), 40, 40, 440, 310, 340, 240),
    t(260, 410, 'prawdziwy kształt', 30, INK, w=600, f=F_H),
    panel(f'<g filter="url(#b1)">' + cat_grid(-20, -20, 380, 280, 6, 4) + '</g>', 580, 40, 440, 310, 340, 240),
    t(800, 410, 'z samego dołu sieci', 30, INK, w=600, f=F_H), t(800, 450, 'rozmazana plama', 26, MUTED),
    panel(f'<g filter="url(#b2)">' + cat_grid(-10, -10, 360, 260, 34, 24) + '</g>', 1120, 40, 440, 310, 340, 240),
    t(1340, 410, '+ wcześniejsze etapy', 30, INK, w=600, f=F_H), t(1340, 450, 'gdy obraz był duży i ostry', 26, MUTED), h=500),
    notes="""Potem sieć musi z tego małego obrazka odtworzyć mapę w pełnym rozmiarze. Pierwsze wyniki wyglądały jak rozmazane plamy. Autorzy poprawili to, dorzucając informacje z wcześniejszych etapów, kiedy obraz był jeszcze duży i ostry.""")

slide('Napięcie, które będzie wracać', S(
    arr(200, 520, 1400, 520, INK, 4), arr(200, 520, 200, 40, INK, 4),
    t(800, 580, 'jak głęboko sieć patrzy →', 30, MUTED),
    p('M220 470 C600 440 900 200 1360 90', st=CYAN, sw=10), t(1350, 60, 'rozumie, CO widzi', 34, CYAN, 'end', 600, F_H),
    p('M220 90 C600 120 900 360 1360 470', st=ORANGE, sw=10), t(240, 70, 'wie, GDZIE to jest', 34, ORANGE, 'start', 600, F_H), h=600),
    notes="""I tu pojawia się napięcie, które będzie wracać przez całą tę historię: im głębiej sieć patrzy, tym lepiej rozumie, co widzi, ale tym gorzej wie, gdzie dokładnie to jest.""")

# ---------- U-Net ----------
section('Historia: U-Net')
import random


def cells(W=400, H=400, seed=1, n=13):
    rnd = random.Random(seed)
    o = [r(0, 0, W, H, '#F3E6EE')]
    for _ in range(n):
        x, y, a = rnd.uniform(40, W - 40), rnd.uniform(40, H - 40), rnd.uniform(0, 180)
        rx_, ry_ = rnd.uniform(30, 50), rnd.uniform(22, 36)
        o.append(f'<g transform="rotate({a:.0f} {x:.0f} {y:.0f})">' + e(x, y, rx_, ry_, '#D9A3C2', '#7A3B5E', 3)
                 + e(x + 6, y, rx_ * .3, ry_ * .35, '#7A3B5E') + '</g>')
    return ''.join(o)


slide('Biologia: komórki z mikroskopu i tylko 30 zdjęć', S(
    panel(cells(), 80, 20, 460, 460, 400, 400, st=INK, rx=230), t(310, 540, 'zdjęcie z mikroskopu', 28, MUTED),
    *[panel(cells(seed=k_ + 2), 720 + (k_ % 6) * 135, 30 + (k_ // 6) * 92, 120, 80, 400, 400, rx=8) for k_ in range(30)],
    t(1120, 540, 'tyle obrazów z zaznaczeniami było do nauki: 30', 28, MUTED), h=580),
    notes="""[ok. 3,5 min · start 0:22]

Ten sam rok, ale zupełnie inny świat: biologia i medycyna. Grupa z Fryburga chciała segmentować komórki na zdjęciach z mikroskopu. Kłopot w tym, że takich zdjęć z gotowymi zaznaczeniami było bardzo mało. W jednym z konkursów, w których startowali, dostali do nauki zaledwie 30 obrazów.""")


def unet(skips=False, labels=True):
    o, res = [], [512, 256, 128, 64]
    enc = [(80 + i * 150, 30 + i * 115, 200 - i * 30, 90) for i in range(4)]
    dec = [(1600 - x - w, y, w, h) for x, y, w, h in enc]
    bott = (690, 490, 220, 80)
    for i, (x, y, w, h) in enumerate(enc):
        o += [r(x, y, w, h, ['#AAB4BD', '#97A2AC', '#838F9A', '#6B7681'][i], rx=8), t(x + w / 2, y + h / 2 + 10, res[i], 28, INK, f=F_M)]
    for i, (x, y, w, h) in enumerate(dec):
        o += [r(x, y, w, h, [YELLOW, '#E3B460', SKIN, '#D98A5A'][i], rx=8), t(x + w / 2, y + h / 2 + 10, res[i], 28, INK, f=F_M)]
    o += [r(*bott, ORANGE, rx=8), t(800, 540, '32', 28, '#FFFFFF', f=F_M)]
    chain = enc + [bott]
    for a, b in zip(chain, chain[1:]):
        o.append(arr(a[0] + a[2] / 2, a[1] + a[3], b[0] + (b[2] / 2 if b != bott else 30), b[1], GRAY, 5))
    chain = [bott] + dec[::-1]
    for a, b in zip(chain, chain[1:]):
        o.append(arr(a[0] + (a[2] - 30 if a == bott else a[2] / 2), a[1], b[0] + b[2] / 2, b[1] + b[3], GRAY, 5))
    if skips:
        for (x, y, w, h), (x2, _, _, _) in zip(enc, dec):
            o.append(arr(x + w + 10, y + h / 2, x2 - 10, y + h / 2, CYAN, 6, 22, '16 10'))
    if labels:
        o += [tm(60, 520, ['w dół: obraz coraz mniejszy,', 'sieć coraz lepiej rozumie'], 26, fill=MUTED, a='start'),
              t(800, 610, 'najwęższe miejsce', 26, ORANGE, w=600),
              tm(1540, 520, ['w górę: z powrotem', 'do pełnego rozmiaru'], 26, fill=MUTED, a='end')]
    return ''.join(o)


slide('U-Net: sieć w kształcie litery U', S(unet(), h=640),
      notes="""Ich sieć ma kształt litery U, stąd nazwa U-Net. Lewa strona schodzi w dół: obraz robi się coraz mniejszy, a sieć coraz lepiej rozumie, co na nim jest. Na dole jest najwęższe miejsce. Prawa strona wraca w górę, do pełnego rozmiaru.""")


def plane(x, y, k=1, col='#3C4248'):
    return g(e(0, 0, 90, 16, col) + p('M-10 -6 L30 -6 L-20 -80 L-40 -80 Z', col) + p('M-10 6 L30 6 L-20 80 L-40 80 Z', col)
             + p('M-70 -4 L-60 -4 L-82 -34 L-92 -34 Z', col) + p('M-70 4 L-60 4 L-82 34 L-92 34 Z', col), x, y, k)


slide('Skróty przenoszą szczegóły prosto na drugą stronę', S(
    g(unet(skips=True, labels=False), 0, 40, .66),
    t(528, 500, 'turkusowe linie: skróty z lewej na prawą', 28, CYAN, w=600),
    r(1120, 0, 460, 560, '#FFFFFF', LINE, 2, 16),
    plane(1350, 80, .8), t(1350, 160, 'pilot widzi miasto z góry', 26, MUTED),
    panel(_city_coarse(160, 160, 8), 1285, 175, 130, 130, 160, 160, rx=6),
    arr(1350, 385, 1350, 318, CYAN, 6, 22, '14 10'),
    panel(_city_fine(480, 480), 1295, 395, 110, 110, 480, 480, rx=6),
    t(1350, 530, '+ zdjęcia ulic od kogoś na ziemi', 26, CYAN, w=600), h=600),
    notes="""Najważniejsze są te turkusowe przerywane linie. To skróty, które przenoszą szczegóły z lewej strony prosto na prawą. Wracając do samolotu: to tak, jakby pilot, który widzi miasto z góry, dostał jeszcze od kogoś na ziemi zdjęcia konkretnych ulic. Dzięki temu sieć wie jednocześnie, co jest na obrazie i gdzie dokładnie biegną krawędzie, nawet tak cienkie jak pojedynczy włos.""")

_warp = ''.join(f'<filter id="w{k_}"><feTurbulence type="fractalNoise" baseFrequency="{.006 + k_ * .002}" numOctaves="2" seed="{k_ * 7 + 3}"/>'
                f'<feDisplacementMap in="SourceGraphic" scale="{60 + k_ * 15}" xChannelSelector="R" yChannelSelector="G"/></filter>' for k_ in range(4))
slide('Sztuczka: to samo zdjęcie, wyginane na różne sposoby', S(
    f'<defs>{_warp}</defs>',
    panel(cells(seed=5), 40, 120, 300, 300, 400, 400, st=INK, rx=12), t(190, 480, 'oryginał', 28, INK, w=600, f=F_H),
    arr(380, 270, 470, 270, ORANGE, 6),
    *[panel(f'<g filter="url(#w{k_})">' + cells(seed=5) + '</g>', 510 + k_ * 270, 120, 240, 300, 400, 400, st=LINE, rx=12) for k_ in range(4)],
    t(1050, 480, 'sieć widzi więcej wariantów tej samej tkanki', 28, MUTED), h=540),
    notes="""Autorzy dodali też sprytny trik: sztucznie wyginali swoje 30 zdjęć na różne sposoby, żeby sieć zobaczyła więcej wariantów tej samej tkanki.""")

_noise = ''.join(r(i * 20, j * 20, 20, 20, random.Random(i * 31 + j).choice(['#5B6168', '#8B939C', '#B9C0C6', '#3C4248', '#D9D3C4'])) for j in range(12) for i in range(12))
_land = r(0, 0, 240, 240, '#BFD7E6') + c(180, 60, 26, '#F4D35E') + p('M0 200 L70 90 L120 150 L170 80 L240 180 L240 240 L0 240 Z', '#6E7F5B') + r(0, 200, 240, 40, '#86A866')
slide('U-Net dziś: od szpitala po generatory obrazów', S(
    _ct(330, 230, 1.1), c(-60 * 1.1 + 330, -30 * 1.1 + 230, 34, st=CYAN, sw=6),
    t(330, 470, 'Medycyna: standard w zaznaczaniu narządów i zmian', 28, INK, w=600, f=F_H),
    panel(_noise, 820, 110, 240, 240, 240, 240, rx=8), arr(1080, 230, 1140, 230, GRAY, 5),
    p('M1160 120 L1200 120 L1230 300 L1270 300 L1300 120 L1340 120 L1300 340 L1200 340 Z', '#6B7681'),
    arr(1360, 230, 1400, 230, GRAY, 5),
    panel(_land, 1410, 110, 180, 240, 240, 240, rx=8),
    t(1200, 470, 'Stable Diffusion: szum → obraz, krok po kroku', 28, INK, w=600, f=F_H), h=520),
    notes="""Dziś U-Net jest standardem w medycynie, a jego odmiana działa nawet w generatorach obrazów, takich jak Stable Diffusion.""")

# ---------- DeepLab ----------
section('Historia: DeepLab')


def _sizes(x, y, sizes, cols):
    o, cx = [], x
    for s_, col in zip(sizes, cols):
        o.append(r(cx, y - s_ / 2, s_, s_, col, rx=6))
        cx += s_ + 24
    return ''.join(o)


slide('A może w ogóle nie zmniejszać obrazu?', S(
    t(60, 60, 'FCN, U-Net: zmniejsz, a potem z trudem odtwórz', 32, INK, 'start', 600, F_H),
    _sizes(60, 190, [160, 110, 70, 40, 70, 110, 160], ['#AAB4BD', '#97A2AC', '#838F9A', ORANGE, SKIN, '#E3B460', YELLOW]),
    t(60, 380, 'DeepLab (Google): zostań przy dużym obrazie', 32, CYAN, 'start', 600, F_H),
    _sizes(60, 510, [160] * 7, ['#AAB4BD', '#97A2AC', '#838F9A', '#6B7681', '#838F9A', '#97A2AC', CYAN]), h=620),
    notes="""[ok. 3,5 min · start 0:26]

Zespół z Google podszedł do problemu z drugiej strony. Zamiast zmniejszać obraz, a potem z trudem go odtwarzać, zapytali: a może w ogóle go nie zmniejszać?""")

BLUE = '#5B8CC4'
slide('Ale jeden piksel nie powie, czym jest', S(
    panel(r(0, 0, 360, 460, BLUE) + e(100, 120, 80, 30, '#FFFFFF') + e(250, 300, 90, 30, '#FFFFFF'), 40, 40, 360, 460, 360, 460, rx=12),
    r(180, 220, 40, 40, st=ORANGE, sw=5), t(220, 560, 'kawałek nieba?', 30, INK, w=600, f=F_H),
    arr(420, 240, 640, 270, ORANGE, 4),
    r(680, 170, 240, 240, BLUE, INK, 3, 12), t(800, 320, '?', 120, '#FFFFFF', w=700, f=F_H),
    t(800, 460, 'ten sam niebieski piksel', 28, MUTED),
    arr(1180, 240, 960, 270, ORANGE, 4),
    panel(g(face(0, 0, 1, NAT, cloth=BLUE, glasses=False), 180, 200), 1200, 40, 360, 460, 360, 460, rx=12),
    r(1360, 420, 40, 40, st=ORANGE, sw=5), t(1380, 560, 'kawałek koszulki?', 30, INK, w=600, f=F_H), h=600),
    cap='Zmniejszanie było po coś: dzięki niemu sieć widzi szerszy kontekst.',
    notes="""Tylko że zmniejszanie było po coś. Dzięki niemu sieć widzi szerszy kontekst. Jeden piksel nie powie, czy to kawałek nieba, czy niebieskiej koszulki. Trzeba spojrzeć dookoła.""")


def _conv(x, y, dil):
    rows = []
    for j in range(7):
        rows.append(''.join('x' if (abs(i - 3) in ((0, 1) if dil == 1 else (0, 2)) and abs(j - 3) in ((0, 1) if dil == 1 else (0, 2))
                                    and (dil == 1 or (i - 3) % 2 == 0 and (j - 3) % 2 == 0)) else '.' for i in range(7)))
    return grid(x, y, 40, rows, {'x': ORANGE if dil == 1 else CYAN, '.': '#E3E0D6'}, gap=3)


def _netdraw(cx, cy, step, col):
    o = [r(cx - 170, cy - 110, 340, 220, '#CFE3EC', rx=10)]
    for k_ in (-1, 0, 1):
        o += [l(cx - step, cy + k_ * step, cx + step, cy + k_ * step, '#5B6168', 3),
              l(cx + k_ * step, cy - step, cx + k_ * step, cy + step, '#5B6168', 3)]
    o += [c(cx + i * step, cy + j * step, 9, col) for i in (-1, 0, 1) for j in (-1, 0, 1)]
    return ''.join(o)


slide('Filtr rozstawiony szerzej, jak rozciągnięta sieć rybacka', S(
    _conv(240, 0, 1), t(380, 330, 'zwykły filtr: 9 punktów, mały obszar', 28, INK, w=600, f=F_H),
    _netdraw(380, 480, 40, ORANGE),
    _conv(1080, 0, 2), t(1220, 330, 'rozszerzony: te same 9 punktów, duży obszar', 28, INK, w=600, f=F_H),
    _netdraw(1220, 480, 90, CYAN),
    t(800, 480, 'tyle samo sznurka →', 28, MUTED), h=600),
    notes="""Rozwiązanie widać na slajdzie. Po lewej zwykły filtr: patrzy na dziewięć sąsiednich pikseli. Po prawej ten sam filtr, ale rozstawiony szerzej, z przerwami. Nadal patrzy na dziewięć punktów, ale obejmuje dużo większy obszar. Trochę jak sieć rybacka: rozciągamy oczka i ta sama ilość sznurka obejmuje większy kawałek wody.""")


def _dots(cx, cy, step, col):
    return ''.join(c(cx + i * step, cy + j * step, 10, col, '#FFFFFF', 3) for i in (-1, 0, 1) for j in (-1, 0, 1))


slide('Kilka filtrów o różnym rozstawie naraz', S(
    r(200, 0, 1200, 560, '#BFD7E6', rx=16), r(820, 60, 380, 500, '#9A8F84'),
    *[r(860 + i * 80, 100 + j * 80, 40, 50, '#D9E4EA') for i in range(4) for j in range(5)],
    r(200, 440, 1200, 120, '#C9A27E'),
    p('M380 330 L500 330 L490 450 L390 450 Z', '#FFFFFF', INK, 4), p('M500 360 Q550 360 545 400 Q540 430 495 428', st=INK, sw=8),
    _dots(440, 390, 30, ORANGE), _dots(1010, 300, 150, YELLOW), _dots(700, 300, 80, CYAN),
    legend(1440, 180, [(ORANGE, 'mały rozstaw'), (CYAN, 'średni'), (YELLOW, 'duży')], 28, 30, 54), h=580),
    cap='Mały kubek na pierwszym planie i cały budynek w tle — w jednym przejściu.',
    notes="""Drugi pomysł to patrzenie w kilku skalach naraz: kilka takich filtrów o różnym rozstawie działa równolegle. Dzięki temu sieć radzi sobie i z małym kubkiem na pierwszym planie, i z całym budynkiem w tle.""")

slide('Później DeepLab dostał część podobną do U-Netu', S(
    r(80, 160, 520, 200, '#6B7681', rx=16), tm(340, 240, ['DeepLab', 'kilka skal naraz'], 34, 1.3, fill=PAPER, w=600, f=F_H),
    t(800, 270, '+', 90, MUTED, w=300),
    r(1000, 160, 520, 200, YELLOW, rx=16), tm(1260, 240, ['dekoder', 'jak w U-Necie'], 34, 1.3, fill=INK, w=600, f=F_H),
    p('M200 360 Q200 480 800 480 Q1400 480 1400 360', st=CYAN, sw=6, dash='16 10'),
    t(800, 540, 'skrót ze szczegółami, jak w U-Necie', 28, CYAN, w=600), h=600),
    cap='Różne pomysły zaczynają się ze sobą łączyć.',
    notes="""Ciekawe, że w późniejszych wersjach DeepLab dostał też część podobną do U-Netu. Różne pomysły zaczynają się ze sobą łączyć.""")

# ---------- Mask R-CNN ----------
section('Historia: Mask R-CNN')
slide('Wróćmy do owiec: do której należy ten piksel?', S(
    panel(pasture('nat') + c(812, 372, 26, st=ORANGE, sw=6) + l(812, 330, 812, 414, ORANGE, 4) + l(770, 372, 854, 372, ORANGE, 4)
          + r(560, 160, 500, 80, '#FFFFFF', rx=40) + t(810, 212, 'owca 2 czy owca 3?', 40, ORANGE, w=600, f=F_H), 200, 0, 1200, 560, 1200, 560), h=580),
    notes="""[ok. 3,5 min · start 0:29]

Wróćmy do owiec. Do tej pory pytaliśmy, jakiego rodzaju jest piksel. Mask R-CNN z 2017 roku, z laboratorium Facebooka, odpowiada na pytanie, do której konkretnie owcy należy.""")

_boxes = ''.join(r(x - 158, y - 98, 286, 194, st=ORANGE, sw=6, dash='18 10', rx=8) for x, y in SHEEP_POS)
_masks = ''.join(sheep(x, y, 1.7, col, col) + r(x - 158, y - 98, 286, 194, st=INK, sw=5, rx=8)
                 for (x, y), col in zip(SHEEP_POS, [ORANGE, CYAN, YELLOW]))
slide('Dwa kroki: najpierw „gdzie”, potem „jak dokładnie”', S(
    panel(pasture('nat') + _boxes, 20, 0, 760, 355, 1200, 560), t(400, 420, 'Krok 1: prostokąty „tu coś jest”', 32, INK, w=600, f=F_H),
    arr(790, 180, 830, 180, GRAY, 5),
    panel(pasture('nat') + r(0, 0, 1200, 560, '#FFFFFF', op=.45) + _masks, 840, 0, 760, 355, 1200, 560),
    t(1220, 420, 'Krok 2: kształt w każdym prostokącie', 32, INK, w=600, f=F_H), h=460),
    notes="""Działa w dwóch krokach. Najpierw szybko przegląda obraz i zaznacza prostokąty, w których coś prawdopodobnie jest. To widać po lewej. Potem bierze każdy prostokąt osobno, sprawdza, co w nim jest, i dokładnie wycina kształt obiektu w środku. To widać po prawej.""")


def _round_panel(aligned):
    o = [r(0, 0, 600, 400, '#EFEAE0')]
    o += [l(i * 100, 0, i * 100, 400, '#C9C2B4', 2) for i in range(1, 6)] + [l(0, j * 100, 600, j * 100, '#C9C2B4', 2) for j in range(1, 4)]
    o.append(sheep(290, 190, 1.2, '#B9B2A6', '#8B8378'))
    o.append(r(178, 123, 201, 134, st=CYAN, sw=4, dash='10 8'))
    if aligned:
        o.append(f'<g opacity=".75">{sheep(290, 190, 1.2, CYAN, CYAN)}</g>')
    else:
        sx, sy = 200 / 167 / 1, 200 / 112
        o.append(r(200, 100, 200, 200, st=ORANGE, sw=5))
        o.append(f'<g opacity=".75" transform="translate(300 200) scale({sx:.3f} {sy:.3f}) translate(9.5 0)">'
                 + sheep(0, 0, 1, ORANGE, ORANGE) + '</g>')
    return ''.join(o)


slide('Drobiazg: zaokrąglanie do najbliższej kratki', S(
    panel(_round_panel(False), 60, 0, 660, 440, 600, 400), t(390, 500, 'starsze metody: prostokąt dociągnięty do kratek', 28, ORANGE, w=600),
    t(390, 540, 'maska ląduje obok owcy', 26, MUTED),
    panel(_round_panel(True), 880, 0, 660, 440, 600, 400), t(1210, 500, 'Mask R-CNN: dokładne przeliczenie', 28, CYAN, w=600),
    t(1210, 540, 'maska leży na owcy', 26, MUTED), h=570),
    notes="""Najciekawsza historia związana z tym modelem dotyczy drobiazgu. Starsze metody, wycinając prostokąt, zaokrąglały jego położenie do najbliższej kratki. Przy pytaniu „czy to owca?” nie miało to znaczenia. Ale przy wycinaniu dokładnego kształtu maska lądowała lekko obok obiektu. Autorzy zastąpili zaokrąglanie dokładnym przeliczeniem i jakość masek wyraźnie wzrosła.""")

statement('Czasem największy postęp to znalezienie miejsca, w którym system po cichu gubi informację.',
          """To dobra lekcja: czasem największy postęp nie wymaga wielkiego nowego pomysłu, tylko znalezienia miejsca, w którym system po cichu gubi informację. Przy budowie dzisiejszego demo trafiło się coś bardzo podobnego. Opowiem o tym po pokazie.""",
          kicker='Lekcja z Mask R-CNN', size=72)

# ---------- Transformery ----------
section('Historia: transformery')
NEUT = '#E3E0D6'


def part(only, col, base=NEUT, bgc='#F7F4EE'):
    """Paleta twarzy, w której kolor ma tylko jedna część (szuflada)."""
    d = dict(bg=bgc, hair=base, skin=base, brow=base, eye='#C9C2B4', lip='#C9C2B4', gl='#C9C2B4', cloth=base, nose=None)
    for k_ in only:
        d[k_] = col
    return d


_drawers = ''.join(r(940 + i * 150, 120 + j * 100, 136, 86, '#C9A27E', '#8A6F55', 3, 8) + r(990 + i * 150, 158 + j * 100, 36, 10, '#8A6F55', rx=5)
                   for i in range(4) for j in range(3))
slide('Transformery (ok. 2020): odwrócone pytanie', S(
    t(380, 50, 'Do tej pory: piksel po pikselu', 32, INK, w=600, f=F_H),
    grid(140, 90, 60, ["????....", "????....", "???.....", "........", "........", "........"],
         {'?': '#FFFFFF', '.': '#FFFFFF'}, st=LINE, nums=["????    ", "????    ", "???     ", "        ", "        ", "        "], nsize=28, ncol=ORANGE),
    arr(370, 290, 330, 230, INK, 4), t(380, 500, '„co to jest?” × setki tysięcy', 28, MUTED),
    t(1165, 50, 'Teraz: sto pustych szuflad', 32, INK, w=600, f=F_H),
    _drawers, t(1165, 460, '… każda szuflada ma znaleźć jedną rzecz', 28, MUTED),
    t(1165, 500, 'i oddać: kształt + nazwę', 28, CYAN, w=600), h=560),
    notes="""[ok. 3,5 min · start 0:33]

Około 2020 roku do segmentacji trafiają transformery, czyli ta sama rodzina modeli, na której działa ChatGPT.

Najciekawsza zmiana polega na odwróceniu pytania. Do tej pory model szedł od piksela do piksela i pytał: co to jest? Nowe modele, takie jak MaskFormer i Mask2Former, robią to inaczej. Mają z góry ustaloną liczbę pustych szuflad, powiedzmy sto. Każda szuflada ma znaleźć na obrazie jedną rzecz i oddać dwie informacje: jaki ta rzecz ma kształt i czym jest.""")

_q = [('osoba', part(['hair', 'skin', 'brow', 'eye', 'lip', 'gl', 'cloth'], ORANGE)), ('okulary', part(['gl'], CYAN)),
      ('włosy', part(['hair'], HAIR)), ('skóra', part(['skin'], SKIN)), ('ubranie', part(['cloth'], CLOTH)),
      ('tło', part([], NEUT, bgc='#2A2D34'))]
slide('Każda szuflada oddaje jedną maskę z podpisem', S(
    *[c(140 + i * 264, 50, 40, '#EFEAE0', GRAY, 3) + t(140 + i * 264, 60, f'q{i + 1}', 28, INK, f=F_M)
      + arr(140 + i * 264, 96, 140 + i * 264, 150, GRAY, 4, 16)
      + panel(g(face(0, 0, 1, col, glw=10), 180, 200), 40 + i * 264, 165, 200, 255, 360, 460, rx=10)
      + t(140 + i * 264, 480, name, 30, INK, w=600, f=F_H) for i, (name, col) in enumerate(_q)], h=520),
    notes="""Na slajdzie widać to dosłownie. Każde zapytanie, od q1 do q6, zamienia się w jedną maskę z podpisem: osoba, okulary, włosy, skóra, ubranie, tło.""")

slide('Trzy rodzaje segmentacji = jeden model, inaczej odczytany', S(
    *[panel(pasture(m), 20 + i * 530, 40, 500, 233, 1200, 560) + t(270 + i * 530, 340, h_, 30, INK, w=600, f=F_H)
      + t(270 + i * 530, 385, sub, 26, MUTED)
      for i, (m, h_, sub) in enumerate([('sem', 'szuflada na każdy rodzaj', '= semantyczna'),
                                         ('inst', 'szuflada na każdą owcę', '= instancyjna'),
                                         ('pan', 'obie naraz', '= panoptyczna')])], h=440),
    cap='Kolory to te same kategorie, które za chwilę zobaczycie na kamerze.',
    notes="""Dlaczego to takie wygodne? Bo nagle te trzy rodzaje segmentacji z owcami stają się jednym zadaniem. Jedna szuflada na każdy rodzaj rzeczy to segmentacja semantyczna. Jedna szuflada na każdą owcę to instancyjna. Obie naraz to panoptyczna. Ten sam model, tylko inaczej odczytany wynik.

Kolory na slajdzie to te same kategorie, które za chwilę zobaczycie na kamerze.""")

# ---------- SAM ----------
section('Historia: SAM')
_cls19 = ['droga', 'chodnik', 'budynek', 'ściana', 'płot', 'słup', 'światła', 'znak', 'roślinność', 'teren',
          'niebo', 'pieszy', 'rowerzysta', 'samochód', 'ciężarówka', 'autobus', 'pociąg', 'motocykl', 'rower']
GLM = mono('none', 'none', gl=CYAN)
slide('SAM (Meta, 2023): nie ma listy', S(
    r(40, 0, 640, 560, '#FFFFFF', LINE, 2, 16), t(360, 56, 'Wcześniej: zamknięta lista, np. 19 klas', 30, INK, w=600, f=F_H),
    *[t(90 + (k_ // 10) * 300, 116 + (k_ % 10) * 40, '• ' + n_, 26, INK, 'start') for k_, n_ in enumerate(_cls19)],
    t(390, 520, 'okulary?  nie ma na liście = nie istnieją', 28, ORANGE, w=600),
    arr(720, 280, 820, 280, ORANGE, 6),
    panel(g(face(0, 0) + f'<g opacity=".8">{face(0, 0, 1, GLM, bg=False, glw=14)}</g>' + c(-45, -14, 12, ORANGE, '#FFFFFF', 4), 180, 200),
          880, 20, 400, 511, 360, 460, rx=12),
    tm(1320, 220, ['Pokazujecie,', 'co was', 'interesuje,', 'a on to wycina.'], 34, 1.3, fill=INK, a='start', w=600, f=F_H), h=580),
    notes="""[ok. 4 min · start 0:36]

I ostatni etap tej historii: Segment Anything, model firmy Meta z 2023 roku.

Wszystkie wcześniejsze modele miały zamkniętą listę rzeczy, które znają, na przykład 19 rodzajów obiektów na ulicy. Jeśli czegoś nie było na liście, model tego nie zauważał. SAM działa inaczej. Nie ma listy. Pokazujecie mu, co was interesuje, a on to wycina.""")

FACEM = mono('none', 'none', skin=CYAN, brow=CYAN, eye=CYAN, lip=CYAN, gl=CYAN, neck='none')
_pr = [('Punkt', 'klik w jeden piksel', GLM, c(-45, -14, 12, ORANGE, '#FFFFFF', 4)),
       ('Ramka', 'zgrubny prostokąt', FACEM, r(-118, -135, 236, 280, st=ORANGE, sw=6, dash='14 8', rx=8)),
       ('Tekst', 'dopiero SAM 3, koniec 2025', GLM, r(-110, -192, 220, 54, '#FFFFFF', ORANGE, 3, 27) + t(0, -155, '„okulary”', 30, INK, w=600))]
slide('Jak pokazać, o co chodzi?', S(
    *[panel(g(face(0, 0) + f'<g opacity=".75">{face(0, 0, 1, m_, bg=False, glw=14)}</g>' + mark, 180, 200), 80 + i * 520, 0, 400, 470, 360, 460, rx=12)
      + t(280 + i * 520, 530, h_, 34, INK, w=600, f=F_H) + t(280 + i * 520, 574, sub, 26, ORANGE if i == 2 else MUTED)
      for i, (h_, sub, m_, mark) in enumerate(_pr)], h=600),
    notes="""Można kliknąć w jeden punkt obiektu albo zaznaczyć go z grubsza prostokątem. Na slajdzie jest też tekst, ale tu uczciwie: w pierwszej wersji SAM wpisywanie słów nie działało. To przyszło dopiero w wersji trzeciej, pod koniec 2025 roku.""")

_amb = [('okulary?', GLM), ('twarz?', FACEM), ('cała osoba?', mono(CYAN, 'none'))]
slide('Klik w okulary: ale co właściwie macie na myśli?', S(
    panel(g(face(0, 0) + c(-45, -14, 14, ORANGE, '#FFFFFF', 4), 180, 200), 20, 40, 340, 435, 360, 460, rx=12),
    t(190, 530, 'jeden klik', 30, ORANGE, w=600, f=F_H),
    arr(390, 260, 470, 260, ORANGE, 6),
    *[panel(g(face(0, 0) + f'<g opacity=".8">{face(0, 0, 1, m_, bg=False, glw=14)}</g>', 180, 200), 500 + i * 370, 40, 340, 435, 360, 460, rx=12)
      + t(670 + i * 370, 530, h_, 32, INK, w=600, f=F_H) for i, (h_, m_) in enumerate(_amb)], h=580),
    cap='SAM nie udaje, że wie: oddaje kilka masek, od najmniejszej do największej, i pozwala wybrać.',
    notes="""Jest tu ciekawe nawiązanie do wazonu. Kiedy klikniecie w okulary na czyjejś twarzy, co właściwie macie na myśli? Okulary? Całą twarz? Całą osobę? SAM nie udaje, że wie. Zwraca kilka masek naraz, od najmniejszej do największej, i pozwala wybrać.""")

slide('Skąd ta wszechstronność? Z ogromu danych', S(
    t(330, 180, '11 mln', 120, INK, w=700, f=F_H), t(330, 240, 'zdjęć', 32, MUTED),
    t(330, 420, '1,1 mld', 120, CYAN, w=700, f=F_H), t(330, 480, 'zaznaczonych obiektów', 32, MUTED),
    c(1150, 290, 200, st=LINE, sw=6),
    r(1000, 50, 300, 80, '#3C4248', rx=40), t(1150, 102, 'model proponuje', 30, PAPER, w=600),
    r(1300, 330, 260, 80, ORANGE, rx=40), t(1430, 382, 'ludzie poprawiają', 28, '#FFFFFF', w=600),
    r(760, 330, 260, 80, CYAN, rx=40), t(890, 382, 'model się uczy', 28, INK, w=600),
    arr(1310, 140, 1380, 320, GRAY, 5), arr(1290, 420, 1030, 420, GRAY, 5), arr(900, 320, 990, 140, GRAY, 5), h=560),
    notes="""Skąd ta wszechstronność? Z ogromnej ilości danych: 11 milionów zdjęć i ponad miliard zaznaczonych obiektów. Większość tych zaznaczeń zrobił zresztą sam model, a ludzie je tylko poprawiali.""")

slide('Ograniczenie: SAM wie gdzie, ale nie wie co', S(
    panel(g(face(0, 0) + f'<g opacity=".8">{face(0, 0, 1, GLM, bg=False, glw=14)}</g>', 180, 200), 200, 20, 420, 537, 360, 460, rx=12),
    r(760, 160, 420, 90, CYAN, rx=45), t(970, 220, '„tu jest obiekt” ✓', 36, INK, w=600, f=F_H),
    r(760, 320, 420, 90, '#FFFFFF', ORANGE, 4, 45), t(970, 380, '„to są okulary” ✗', 36, ORANGE, w=600, f=F_H), h=580),
    cap='Tyle teorii. Zobaczmy, jak to wygląda naprawdę.',
    notes="""Jedno ograniczenie: SAM wycina kształt, ale nie wie, co to jest. Powie „tu jest obiekt”, ale nie powie „to są okulary”.

Tyle teorii. Zobaczmy, jak to wygląda naprawdę.""")

# =====================================================================
section('Demo')
BODY = '#C98B5A'
_D = dict(  # paleta sceny demo dla każdego trybu: ściana, tło po prawej, stół, dłoń + kolory twarzy
    nat=(dict(wall='#D8B48A', right='#8FA3B0', table='#B9875A', hand='#E3B48F'), NAT, {}),
    m1=(dict(wall=ORANGE, right='#2A2D34', table=ORANGE, hand=ORANGE),
        dict(bg='none', hair='#2A2D34', skin=ORANGE, brow='#2A2D34', eye='#2A2D34', lip='#2A2D34', gl='#2A2D34', cloth='#2A2D34', nose=None), {}),
    m2=(dict(wall='#2A2D34', right='#2A2D34', table='#2A2D34', hand=BODY),
        dict(bg='none', hair=HAIR, skin=SKIN, brow=SKIN, eye=SKIN, lip=SKIN, gl=GRAY, cloth=CLOTH, nose=None), dict(neck=BODY)),
    m3=(dict(wall='#2A2D34', right='#2A2D34', table='#2A2D34', hand='#2A2D34'), CLS, dict(neck=BODY)),
)


def demo_scene(m='nat', glasses=True, W=800, H=500):
    sc, fc, ov = _D[m]
    o = [r(0, 0, W, H, sc['wall']), r(W / 2, 0, W / 2, H, sc['right']), r(0, 420, W, 80, sc['table'])]
    o.append(face(400, 255, .95, fc, glasses=glasses, bg=False, glw=12 if m == 'm3' else 7, **ov))
    o.append(hand(640, 400, 1.6, sc['hand']))
    return ''.join(o)


_modes = [('1', 'Klasyczna', 'próg koloru skóry + GrabCut', 'm1'), ('2', 'Sieć wieloklasowa', 'tło, włosy, skóra, ubranie', 'm2'),
          ('3', 'Face parsing', '19 części twarzy, w tym okulary', 'm3'), ('4', 'Porównanie', 'wszystkie trzy obok siebie', None)]
_mc = []
for i, (k_, h_, sub, m) in enumerate(_modes):
    x = 20 + i * 400
    _mc.append(r(x, 0, 370, 420, CARD_D, '#2A2D34', 2, 16))
    if m:
        _mc.append(panel(demo_scene(m), x + 25, 25, 320, 200, 800, 500, st=None, rx=10))
    else:
        _mc += [panel(demo_scene(mm), x + 25 + j * 109, 70, 102, 64, 800, 500, st=None, rx=6) for j, mm in enumerate(['m1', 'm2', 'm3'])]
    _mc += [c(x + 55, 290, 28, ORANGE), t(x + 55, 301, k_, 30, '#FFFFFF', w=700, f=F_M),
            t(x + 100, 302, h_, 32, PAPER, 'start', 600, F_H), t(x + 30, 370, sub, 25, MUTED_D, 'start')]
slide('Czas na żywą kamerę', S(*_mc, h=440), dark=True,
      cap='Patrzcie zwłaszcza na okulary: jedna metoda je rozumie, inna w ogóle ich nie zauważa.',
      notes="""[ok. 15 min · start 0:40]

[Uruchom: uv run live_demo/gui_launcher.py. Tryby przełączasz klawiszami 1-4. Poproś ochotnika, najlepiej w okularach.]

Zobaczycie teraz trzy podejścia z naszej historii, działające na żywo na zwykłym laptopie, bez żadnej specjalnej karty graficznej.""")


def _pair(left, right, l1, l2, r1, r2, rcol=INK):
    return S(panel(left, 20, 0, 740, 463, 800, 500), t(390, 520, l1, 30, INK, w=600, f=F_H), t(390, 562, l2, 26, MUTED),
             panel(right, 840, 0, 740, 463, 800, 500), t(1210, 520, r1, 30, rcol, w=600, f=F_H), t(1210, 562, r2, 26, MUTED), h=590)


slide('Tryb 1: klasyczny — zna tylko kolor', _pair(
    demo_scene('nat'), demo_scene('m1'), 'obraz z kamery', 'beżowa ściana, drewniany stół', 'na pomarańczowo: „skóra”',
    'dłoń, ściana i stół też; okulary nie istnieją', ORANGE),
    notes="""Tryb pierwszy, klasyczny. To metoda z najstarszej warstwy: komputer szuka pikseli w kolorze skóry, a GrabCut wygładza wynik. Na pomarańczowo jest to, co uznał za skórę. Zwróćcie uwagę na dłoń: też jest pomarańczowa. A jeśli w tle stoi drewniany stół albo jest beżowa ściana, one też się pomalują. Ten algorytm nie ma pojęcia, czym jest twarz. Zna tylko kolor. Okulary dla niego po prostu nie istnieją.""")

slide('Tryb 2: sieć od Google — rozumie, co widzi', S(
    panel(demo_scene('m2'), 120, 0, 880, 550, 800, 500),
    legend(1080, 60, [('#2A2D34', 'tło'), (HAIR, 'włosy'), (SKIN, 'skóra twarzy'), (BODY, 'skóra rąk'), (CLOTH, 'ubranie'), (GRAY, '„inne”')], 32, 40, 66),
    t(1080, 500, 'okulary: co najwyżej „inne”', 30, ORANGE, 'start', 600), h=560),
    notes="""Tryb drugi, sieć neuronowa od Google. Ona już rozumie, co widzi: osobno tło, włosy, skórę twarzy, skórę rąk i ubranie. Zobaczcie, jak ładnie oddziela włosy od twarzy. Ale okulary? Nie ma dla nich osobnej kategorii, więc w najlepszym razie trafiają do szuflady „inne”. Model nie zauważy czegoś, czego nikt go nie nauczył.""")

slide('Tryb 3: 19 części twarzy, w tym okulary', _pair(
    demo_scene('m3', glasses=False) + r(20, 20, 330, 60, '#14161B', rx=8) + t(185, 61, 'brak okularów', 30, PAPER, w=600),
    demo_scene('m3') + r(20, 20, 400, 60, '#14161B', rx=8) + t(220, 61, 'OKULARY WYKRYTE', 30, CYAN, w=700),
    'ochotnik zdejmuje okulary', 'brwi, oczy, usta, uszy, włosy', 'zakłada je z powrotem', 'oprawka obrysowana na turkusowo', CYAN),
    notes="""Tryb trzeci, model, który zna 19 części twarzy: brwi, oczy, usta, uszy, włosy i okulary. Poproszę, żeby ochotnik zdjął okulary. Napis: brak okularów. A teraz je zakłada. Napis: okulary wykryte, a oprawka obrysowana na turkusowo. Nic tu nie jest doklejone. Model sam ocenia każdy piksel i stwierdza: to jest oprawka. Sprawdźmy, kiedy się pogubi: obrót głowy, zasłonięcie części twarzy dłonią, odsunięcie się od kamery.""")

_lag = '<g opacity=".55">' + face(400, 255, .95, mono('#FFFFFF', 'none'), glasses=False, bg=False) + '</g>'
slide('Tryb 4: wszystkie trzy obok siebie', S(
    *[panel(demo_scene(m) + (g(_lag, 60, 0) if m != 'm1' else ''), 20 + i * 530, 40, 500, 313, 800, 500)
      + t(270 + i * 530, 420, h_, 30, INK, w=600, f=F_H) + t(270 + i * 530, 462, sub, 26, MUTED)
      for i, (m, h_, sub) in enumerate([('m1', 'klasyczna', 'na bieżąco'), ('m2', 'sieć wieloklasowa', '~10 masek na sekundę'),
                                         ('m3', 'face parsing', '~6 masek na sekundę')])], h=500),
    cap='Przy szybkim ruchu maska sieci spóźnia się za obrazem. Taka jest cena zwykłego procesora.',
    notes="""Tryb czwarty, wszystkie trzy obok siebie. Liczby na dole mówią, ile razy na sekundę każda metoda liczy swój wynik. Przy szybkim ruchu widać, że maski sieci lekko spóźniają się za obrazem. Taka jest cena liczenia na zwykłym procesorze.

[Gdyby kamera nie ruszyła: zmień numer kamery w launcherze. Jeśli dalej nic, opowiedz wyniki na podstawie tabeli z następnego slajdu.]""")

# =====================================================================
section('Po pokazie')
_td = 'padding:22px;text-align:left'
_rows = [('Klasyczna', 'nie potrzebuje danych, działa wszędzie, każdą decyzję da się wytłumaczyć', 'gubi się przy innym świetle i innym odcieniu skóry'),
         ('Sieć od Google', 'radzi sobie z różnym światłem i tłem', f'<span style="color:{ORANGE}">widzi tylko to, czego ją nauczono: okularów nie</span>'),
         ('Części twarzy', f'<span style="color:{CYAN}">widzi okulary bardzo dokładnie</span>', 'uczyła się na celebrytach: twarz duża i na środku')]
slide('Co właśnie zobaczyliście', (
    f'<table style="border-collapse:collapse;width:1664px;font-size:30px;line-height:1.35;color:{INK}">'
    f'<tr><th style="{_td};width:22%;background:{DARK};color:{PAPER}">Metoda</th><th style="{_td};background:{DARK};color:{PAPER}">Mocne strony</th>'
    f'<th style="{_td};background:{DARK};color:{PAPER}">Słabości</th></tr>'
    + ''.join(f'<tr style="background:{["#FFFFFF", "#F1EDE3"][k_ % 2]}"><td style="{_td};font-weight:600">{a}</td><td style="{_td}">{b}</td><td style="{_td}">{c_}</td></tr>'
              for k_, (a, b, c_) in enumerate(_rows)) + '</table>'),
    notes="""[ok. 5 min · start 0:55]

Podsumujmy, co właśnie zobaczyliście.

Metoda klasyczna nie potrzebuje żadnych danych do nauki i działa na każdym komputerze. Każdą jej decyzję da się wytłumaczyć jednym zdaniem: ten piksel ma taki kolor. Ale wystarczy zmienić światło albo pokazać jej kogoś o innym odcieniu skóry, i się gubi.

Sieć od Google radzi sobie z różnym światłem i tłem, ale widzi tylko to, czego ją nauczono. Okularów nie było na jej liście, więc ich nie widzi.""")

_few = ''.join(r(x, y, 6, 6, CYAN) for x, y in [(392, 217), (400, 217), (433, 217), (441, 218), (408, 229), (426, 229)])
slide('Ten sam model, inaczej podany obraz', S(
    panel(r(0, 0, 640, 400, '#8FA3B0') + face(420, 230, .38, bg=False) + r(0, 360, 640, 40, '#B9875A') + _few, 40, 0, 640, 400, 640, 400),
    t(360, 460, 'cały obraz z kamery, twarz niewielka', 28, MUTED),
    t(360, 560, '129', 110, INK, w=700, f=F_H), t(360, 610, 'pikseli okularów', 28, MUTED),
    arr(720, 200, 860, 200, ORANGE, 6), t(790, 170, 'wytnij i powiększ', 24, ORANGE, w=600),
    panel(g(face(0, 0) + f'<g opacity=".85">{face(0, 0, 1, GLM, bg=False, glw=12)}</g>', 180, 200), 940, 0, 313, 400, 360, 460),
    t(1096, 460, 'najpierw sama twarz', 28, MUTED),
    t(1096, 560, '2553', 110, CYAN, w=700, f=F_H), t(1096, 610, 'pikseli okularów', 28, MUTED), h=640),
    notes="""Model od części twarzy widzi okulary bardzo dokładnie, ale on też ma swoje przyzwyczajenia. Uczył się na zdjęciach celebrytów, na których twarz jest duża i na środku kadru. Przy budowie tego demo wyszło to bardzo wyraźnie. Kiedy dostał cały obraz z kamery, na którym twarz była niewielka, znalazł na okularach 129 pikseli. Kiedy najpierw wycięliśmy samą twarz i ją powiększyliśmy, znalazł ich 2553, czyli tyle, ile trzeba. Ten sam model, bez żadnej zmiany w nim samym, tylko inaczej podany obraz. Dokładnie jak z zaokrąglaniem w Mask R-CNN: wystarczyło znaleźć miejsce, w którym ginęła informacja.""")

_six = [('#2A2D34', 'tło'), (HAIR, 'włosy'), (SKIN, 'skóra twarzy'), (BODY, 'skóra ciała'), (CLOTH, 'ubranie'), (GRAY, 'inne')]
slide('Każda metoda inaczej rozumie, czym jest obiekt', S(
    r(40, 0, 480, 470, '#FFFFFF', LINE, 2, 16), r(180, 80, 200, 200, ORANGE, rx=12),
    t(280, 360, 'obiekt = kolor', 36, INK, w=600, f=F_H), t(280, 410, 'klasyczna', 26, MUTED),
    r(560, 0, 480, 470, '#FFFFFF', LINE, 2, 16),
    *[r(640 + (k_ % 3) * 110, 60 + (k_ // 3) * 110, 90, 90, col, rx=10) for k_, (col, _) in enumerate(_six)],
    t(800, 360, 'świat = 6 kategorii', 36, INK, w=600, f=F_H), t(800, 410, 'sieć od Google (bez okularów)', 26, MUTED),
    r(1080, 0, 480, 470, '#FFFFFF', LINE, 2, 16), panel(g(face(0, 0, 1, CLS), 180, 200), 1240, 40, 160, 204, 360, 460, rx=8),
    l(1320, 30, 1320, 260, ORANGE, 3, '8 6'), l(1220, 142, 1420, 142, ORANGE, 3, '8 6'),
    t(1320, 360, 'twarz = 19 części', 36, INK, w=600, f=F_H), t(1320, 410, 'i zawsze na środku zdjęcia', 26, MUTED), h=490),
    cap='Żadna nie jest po prostu najlepsza. Tylko jak porównać je liczbowo?',
    notes="""Wniosek jest taki, że żadna z tych metod nie jest po prostu najlepsza. Każda inaczej rozumie, czym jest obiekt. Dla pierwszej obiekt to kolor. Dla drugiej świat składa się z sześciu kategorii. Dla trzeciej twarz ma 19 części i jest na środku zdjęcia.

Tylko jak porównać takie wyniki liczbowo? O tym za chwilę.""")

# =====================================================================
section('Ocena')
_M = ["..f..", ".pppx", ".pppx", ".pppx", "..f.."]
_MC = {'p': CYAN, 'x': ORANGE, 'f': YELLOW, '.': '#E3E0D6'}
_HUM = {'p': '#3C4248', 'f': '#3C4248', 'x': '#E3E0D6', '.': '#E3E0D6'}
_MOD = {'p': '#3C4248', 'x': '#3C4248', 'f': '#E3E0D6', '.': '#E3E0D6'}
slide('Ocena: porównujemy model z człowiekiem', S(
    grid(40, 0, 76, _M, _HUM, gap=4), t(230, 440, 'zaznaczył człowiek', 30, INK, w=600, f=F_H),
    t(470, 200, '+', 70, MUTED),
    grid(540, 0, 76, _M, _MOD, gap=4), t(730, 440, 'zaznaczył model', 30, INK, w=600, f=F_H),
    t(970, 200, '=', 70, MUTED),
    grid(1040, 0, 76, _M, _MC, gap=4), t(1230, 440, 'porównanie', 30, INK, w=600, f=F_H),
    legend(40, 500, [(CYAN, 'trafienie (9)')], 28, 30), legend(420, 500, [(ORANGE, 'fałszywy alarm (3)')], 28, 30),
    legend(840, 500, [(YELLOW, 'pominięcie (2)')], 28, 30), legend(1220, 500, [('#E3E0D6', 'zgodne tło (11)')], 28, 30), h=540),
    notes="""[ok. 6 min · start 1:00]

Żeby ocenić segmentację, porównujemy to, co zaznaczył model, z tym, co zaznaczył człowiek. Na slajdzie jest mała siatka pięć na pięć. Turkusowe pola to trafienia: model i człowiek zgodnie mówią „obiekt”. Pomarańczowe to fałszywe alarmy: model zaznaczył, a niepotrzebnie. Żółte to pominięcia: obiekt był, a model go nie zauważył. Szare to tło, co do którego obaj się zgadzają.

[Daj sali chwilę, żeby spróbowała policzyć pierwszy wynik.]""")


def _frac(name, top, bot, val, desc):
    def row(y, cols):
        return ''.join(r(560 + k_ * 44, y, 38, 38, col, rx=4) for k_, col in enumerate(cols))
    return S(grid(20, 40, 76, _M, _MC, gap=4), t(210, 470, 'ta sama predykcja', 26, MUTED),
             t(560, 80, name, 44, INK, 'start', 700, F_H),
             row(150, top), l(560, 222, 560 + max(len(top), len(bot)) * 44, 222, INK, 4), row(240, bot),
             t(560, 360, f'{len(top)} / {len(bot)}  ≈  <tspan fill="{ORANGE}" font-size="72" font-weight="700" font-family="{F_H}">{val}</tspan>', 54, INK, 'start', 500, F_M),
             t(560, 440, desc, 30, MUTED, 'start'), h=520)


slide('IoU: część wspólna podzielona przez całość', _frac('IoU', [CYAN] * 9, [CYAN] * 9 + [ORANGE] * 3 + [YELLOW] * 2, '0,64',
                                                         '1 oznaczałoby idealne nałożenie'),
      notes="""Najpopularniejsza miara to IoU. Bierzemy część wspólną obu zaznaczeń i dzielimy przez obszar, który zajmują razem. Tu mamy 9 trafień, 3 fałszywe alarmy i 2 pominięcia, czyli 9 przez 14, mniej więcej 0,64. Jedynka oznaczałaby idealne nałożenie.""")

slide('Dice: prawie to samo, ale łagodniej', _frac('Dice', [CYAN] * 18, [CYAN] * 18 + [ORANGE] * 3 + [YELLOW] * 2, '0,78',
                                                  'lekarze częściej podają Dice, informatycy IoU'),
      notes="""Druga miara, Dice, liczy prawie to samo, ale łagodniej. Ta sama predykcja daje 0,78. Lekarze częściej podają Dice, informatycy IoU, więc porównując wyniki z dwóch artykułów, warto sprawdzić, o której mowa.""")

slide('Dokładność: brzmi najlepiej, jest najmniej uczciwa', _frac('Dokładność', [CYAN] * 9 + ['#E3E0D6'] * 11, ['#C9CED3'] * 25, '0,80',
                                                                 'procent trafionych pikseli, razem z tłem'),
      cap='Jedna liczba nigdy nie mówi wszystkiego: w pracach naukowych podaje się kilka miar naraz.',
      notes="""I trzecia, najprostsza: jaki procent pikseli model trafił. Tutaj 20 z 25, czyli 0,80. Brzmi najlepiej, a jest najmniej uczciwa. Za chwilę pokażę dlaczego.

Wniosek praktyczny: jedna liczba nigdy nie mówi wszystkiego. W pracach naukowych podaje się kilka miar naraz.""")

_bar = r(100, 470, 1386, 70, '#8B939C', rx=8) + r(1486, 470, 14, 70, ORANGE, rx=4)
slide('Gdy 99% obrazu to „nic ciekawego”', S(
    _ct(800, 210, 1.1, tumor=9), l(800 - 66 + 30, 210 - 33 - 30, 1100, 80, ORANGE, 3), t(1110, 80, 'zmiana chorobowa', 30, ORANGE, 'start', 600),
    _bar, t(100, 590, 'wszystkie piksele skanu', 26, MUTED, 'start'), t(1500, 590, '< 1%', 26, ORANGE, 'end', 600), h=620),
    notes="""[ok. 5 min · start 1:06]

Ten pasek to wszystkie piksele zdjęcia z tomografu, na którym lekarz szuka zmiany chorobowej. Zmiana to ten ledwo widoczny pomarańczowy pasek po prawej. Mniej niż jeden procent obrazu.""")

slide('Model, który zawsze mówi „tu nic nie ma”', S(
    _ct(300, 230, 1.1, tumor=9), t(300, 470, 'prawda', 30, INK, w=600, f=F_H),
    _ct(860, 230, 1.1, tumor=9, outline=False), t(860, 470, 'odpowiedź modelu: wszystko to tło', 30, INK, w=600, f=F_H),
    r(1200, 80, 380, 130, '#FFFFFF', LINE, 2, 16), t(1390, 130, 'dokładność', 28, MUTED), t(1390, 190, '99% ✓', 52, '#4E8F3A', w=700, f=F_H),
    r(1200, 250, 380, 130, '#FFFFFF', LINE, 2, 16), t(1390, 300, 'znalezione zmiany', 28, MUTED), t(1390, 360, '0 ✗', 52, ORANGE, w=700, f=F_H), h=520),
    cap='Według najprostszej miary prawie idealny. W praktyce bezużyteczny.',
    notes="""Eksperyment myślowy. Model, który na każde zdjęcie odpowiada „nic tu nie ma, wszystko jest tłem”, trafia w ponad 99 procentach pikseli. Według najprostszej miary jest prawie idealny. W praktyce jest bezużyteczny, bo nigdy niczego nie znajdzie.""")

slide('Ta sama pułapka w czasie nauki', S(
    t(100, 60, 'Skąd może pochodzić błąd, który model poprawia:', 32, INK, 'start', 600, F_H),
    r(100, 120, 1300, 110, '#8B939C', rx=10), t(130, 190, 'piksele tła', 34, '#FFFFFF', 'start', 600),
    r(100, 270, 14, 110, ORANGE, rx=4), t(140, 340, 'piksele zmiany', 34, ORANGE, 'start', 600),
    arr(800, 420, 800, 480, GRAY, 5), t(800, 540, 'najszybciej opłaca się nauczyć jednego: zawsze odpowiadać „tło”', 32, INK, w=600), h=580),
    notes="""Ten sam problem pojawia się w trakcie nauki. Model uczy się, poprawiając swoje błędy, a najwięcej błędów może popełnić tam, gdzie jest najwięcej pikseli, czyli w tle. Najszybciej opłaca mu się więc nauczyć jednej rzeczy: zawsze odpowiadać „tło”.""")

slide('Jak sobie z tym radzić', S(
    l(380, 330, 380, 120, INK, 6), l(180, 150, 580, 110, INK, 6), r(330, 330, 100, 20, INK, rx=4),
    l(180, 150, 140, 260, INK, 2), l(180, 150, 220, 260, INK, 2), p('M120 260 L240 260 Q180 300 120 260 Z', INK),
    r(160, 200, 40, 56, ORANGE, rx=6), t(180, 340, 'pomyłka na guzie', 26, ORANGE, w=600),
    l(580, 110, 540, 220, INK, 2), l(580, 110, 620, 220, INK, 2), p('M520 220 L640 220 Q580 260 520 220 Z', INK),
    r(530, 150, 100, 66, '#C9CED3', rx=6), t(580, 300, 'pomyłka w tle', 26, MUTED, w=600),
    t(380, 450, '1. Pomyłka na małym obiekcie', 32, INK, w=600, f=F_H), t(380, 495, 'kosztuje dużo więcej', 32, INK, w=600, f=F_H),
    c(940, 210, 110, CYAN, op=.6), c(1050, 210, 110, ORANGE, op=.6), c(1350, 230, 32, CYAN, op=.6), c(1382, 230, 32, ORANGE, op=.6),
    t(995, 360, 'duży: Dice 0,5', 28, MUTED), t(1366, 360, 'mały: Dice 0,5', 28, MUTED),
    t(1150, 450, '2. Ocena nakładania się (Dice)', 32, INK, w=600, f=F_H), t(1150, 495, 'mały guz liczy się jak duży', 32, INK, w=600, f=F_H), h=540),
    notes="""Jak sobie z tym radzić? Można powiedzieć modelowi, że pomyłka na małym obiekcie kosztuje go dużo więcej niż pomyłka w tle. Można też oceniać go nie piksel po pikselu, tylko po tym, jak dobrze jego zaznaczenie nakłada się na prawdziwe, czyli właśnie miarą Dice z poprzedniego slajdu. Wtedy mały guz liczy się tak samo jak duży.

W naszym demo był dokładnie ten sam problem: oprawka okularów to tylko kilka procent pikseli twarzy.""")

# =====================================================================
section('Dane')


def clock(x, y, rad=60):
    return c(x, y, rad, '#FFFFFF', INK, 5) + l(x, y, x, y - rad * .7, INK, 6) + l(x, y, x + rad * .5, y, INK, 6) + c(x, y, 6, INK)


slide('Cityscapes: zdjęcia ulic z ok. 50 miast', S(
    panel(_street('nat'), 20, 20, 560, 350, 800, 500), arr(600, 195, 660, 195, ORANGE, 6),
    panel(_street('pan'), 680, 20, 560, 350, 800, 500),
    clock(1420, 150), t(1420, 270, '> 1,5 h', 48, ORANGE, w=700, f=F_H), t(1420, 315, 'ręcznej pracy', 26, MUTED), t(1420, 350, 'na jedno zdjęcie', 26, MUTED),
    t(800, 450, '5000 zdjęć zaznaczonych bardzo dokładnie, piksel po pikselu', 30, INK), h=500),
    notes="""[ok. 4 min · start 1:11]

Każdy z tych modeli jest tak dobry, jak dane, na których się uczył. Oto cztery zbiory, o których często słychać.

Cityscapes to zdjęcia ulic z około pięćdziesięciu miast, głównie niemieckich. Pięć tysięcy z nich zaznaczono bardzo dokładnie. Dla wyobrażenia, ile to pracy: zaznaczenie jednego takiego zdjęcia zajmowało człowiekowi średnio ponad półtorej godziny.""")


def _kitchen():
    o = [r(0, 0, 800, 500, '#C9A8D6'), r(0, 400, 800, 100, '#8C6D4F'), r(60, 60, 220, 160, '#9FD3E6'),
         r(320, 40, 300, 120, '#E39C58'), r(320, 240, 300, 160, '#E39C58'), r(650, 80, 120, 320, '#7BB0A6')]
    for x, y, s_ in [(170, 150, 'okno'), (470, 110, 'szafka'), (470, 330, 'szafka'), (710, 250, 'lodówka'), (150, 330, 'ściana'), (400, 465, 'podłoga')]:
        o.append(t(x, y, s_, 28, INK, w=600))
    return ''.join(o)


def _park():
    o = [r(0, 0, 800, 260, '#7FB2E5'), r(0, 260, 800, 240, '#8DBF6A'), c(150, 220, 110, '#4F8A3C'), r(135, 300, 30, 80, '#6B4A2F'),
         e(520, 380, 80, 40, ORANGE), c(600, 340, 30, ORANGE), e(680, 230, 40, 12, CYAN)]
    for x, y, s_, col in [(400, 100, 'niebo', INK), (400, 470, 'trawa', INK), (150, 200, 'drzewo', '#FFFFFF'), (520, 390, 'pies', '#FFFFFF'), (680, 200, 'frisbee', INK)]:
        o.append(t(x, y, s_, 28, col, w=600))
    return ''.join(o)


slide('ADE20K i COCO-Stuff: przedmioty i tło', S(
    panel(_kitchen(), 20, 0, 740, 463, 800, 500), t(390, 520, 'ADE20K: od kuchni po plaże', 30, INK, w=600, f=F_H),
    t(390, 562, '150 rodzajów obiektów', 26, MUTED),
    panel(_park(), 840, 0, 740, 463, 800, 500), t(1210, 520, 'COCO-Stuff: przedmioty + tło', 30, INK, w=600, f=F_H),
    t(1210, 562, 'niebo, trawa, ściany też mają etykiety', 26, MUTED), h=590),
    notes="""ADE20K to zdjęcia przeróżnych miejsc, od kuchni po plaże, ze stu pięćdziesięcioma rodzajami obiektów. COCO-Stuff to zdjęcia z życia codziennego, na których zaznaczono zarówno przedmioty, jak i tło: niebo, trawę, ściany.""")

_parts = [('włosy', (-100, -120), (-360, -150)), ('brwi', (-44, -46), (-360, -60)), ('oczy', (-42, -12), (-360, 10)),
          ('uszy', (-96, 4), (-360, 90)), ('okulary', (45, -30), (360, -120)), ('skóra', (60, 40), (360, -40)),
          ('usta', (15, 64), (360, 40)), ('szyja', (30, 110), (360, 120)), ('ubranie', (110, 200), (360, 200))]
slide('CelebAMask-HQ: 30 000 twarzy, 19 części', S(
    g(face(0, 0, 1, CLS, neck=BODY) + ''.join(l(px, py, lx + (40 if lx < 0 else -40), ly, INK, 2) + c(px, py, 6, INK)
                                              + t(lx, ly + 10, n_, 32, INK, 'end' if lx < 0 else 'start', 600, F_H)
                                              for n_, (px, py), (lx, ly) in _parts), 800, 290, 1.15), h=600),
    cap='Na nim uczył się model z trybu 3. Dlatego widział okulary, a sieć z trybu 2 nie.',
    notes="""I CelebAMask-HQ: trzydzieści tysięcy zdjęć twarzy, na których ręcznie zaznaczono 19 części, w tym okulary. Na nim uczył się model z trybu trzeciego. Dlatego widział okulary, a sieć z trybu drugiego, uczona na innych danych, nie.""")

_grain = ''.join(r((k_ * 37) % 800, (k_ * 53) % 500, 3, 3, '#FFFFFF', op=.18) for k_ in range(500))
slide('Ostrzeżenie: zdjęcia celebrytów', S(
    panel(r(0, 0, 360, 460, '#E7C9A0') + c(180, 120, 160, '#F6E2C4', op=.7) + g(face(0, 0, 1, NAT, bg=False), 180, 210), 160, 0, 360, 460, 360, 460),
    t(340, 520, 'dobre światło, twarz duża i na środku', 28, INK, w=600, f=F_H),
    panel(r(0, 0, 800, 500, '#3A3F47') + r(0, 380, 800, 120, '#4A3D33') + face(560, 260, .45, bg=False) + r(0, 0, 800, 500, '#14161B', op=.45) + _grain,
          780, 70, 640, 400, 800, 500),
    t(1100, 520, 'zwykła kamera: ciemno, twarz mała, z boku', 28, INK, w=600, f=F_H), h=560),
    notes="""Jest tu też ostrzeżenie. To zdjęcia celebrytów: dobrze oświetlone, starannie wykadrowane, często po makijażu. Model uczony na takich zdjęciach może gorzej radzić sobie ze zwykłymi ludźmi przed zwykłą kamerą.""")

statement('Model widzi tylko to, co pokazały mu dane.',
          """Jeśli zapamiętacie z tego wykładu jedno zdanie, niech to będzie to: model widzi tylko to, co pokazały mu dane.""",
          kicker='Jedno zdanie do zapamiętania', size=96)

# =====================================================================
section('Czego jeszcze nie umiemy')
TONES = ['#F3D9C1', '#E8BF9B', '#D2A07A', '#A9754F', '#7C5236', '#4E3322']


def _ic_weather(x, y):
    return c(x - 20, y - 10, 26, YELLOW) + ''.join(c(x + 18 + dx, y + 20 + dy, 6, '#7FA7C4') for dx, dy in [(0, 0), (16, -12), (-14, 14), (20, 18)])


def _ic_hair(x, y):
    return p(f'M{x - 50} {y + 40} Q{x - 10} {y - 60} {x + 50} {y - 30}', st=HAIR, sw=3) + p(f'M{x - 40} {y + 50} Q{x} {y - 40} {x + 55} {y - 10}', st=HAIR, sw=2)


def _ic_watch(x, y):
    return c(x, y + 6, 40, '#FFFFFF', INK, 5) + r(x - 10, y - 50, 20, 12, INK) + l(x, y + 6, x + 18, y - 14, ORANGE, 5)


def _ic_cost(x, y):
    return clock(x, y, 42)


def _ic_fair(x, y):
    return ''.join(r(x - 60 + k_ * 20, y - 30, 20, 60, col) for k_, col in enumerate(TONES))


_five = [('zmiana warunków', _ic_weather), ('cienkie rzeczy', _ic_hair), ('szybkość', _ic_watch),
         ('koszt danych', _ic_cost), ('sprawiedliwość', _ic_fair)]
slide('Pięć rzeczy, z którymi segmentacja wciąż ma kłopot', S(
    *[r(20 + k_ * 316, 60, 290, 400, '#FFFFFF', LINE, 2, 16) + fn(165 + k_ * 316, 210)
      + t(165 + k_ * 316, 120, f'0{k_ + 1}', 28, ORANGE, f=F_M) + t(165 + k_ * 316, 370, n_, 30, INK, w=600, f=F_H)
      for k_, (n_, fn) in enumerate(_five)], h=520),
    cap='Każda z nich mogłaby być tematem pracy magisterskiej.',
    notes="""[ok. 6 min · start 1:15]

Pięć rzeczy, z którymi segmentacja wciąż ma kłopot. Każda z nich mogłaby być tematem pracy magisterskiej.""")

_snow = ''.join(c((k_ * 71) % 800, (k_ * 43) % 500, 4, '#FFFFFF', op=.8) for k_ in range(140))
_holes = ''.join(r((k_ * 97) % 760, 180 + (k_ * 61) % 300, 70, 50, '#2A2D34', op=.85) for k_ in range(9))
slide('1. Zmiana warunków', S(
    panel(_street('nat'), 20, 0, 560, 280, 800, 500), panel(_street('pan'), 20, 300, 560, 280, 800, 500),
    t(300, 620, 'słoneczna ulica: model widzi wszystko', 28, INK, w=600, f=F_H),
    panel(_street('nat') + r(0, 0, 800, 500, '#0E1424', op=.65) + _snow, 620, 0, 560, 280, 800, 500),
    panel(_street('pan') + _holes, 620, 300, 560, 280, 800, 500),
    t(900, 620, 'noc i śnieg: model się gubi', 28, ORANGE, w=600, f=F_H),
    tm(1220, 200, ['Dziś widzieliście', 'to samo na żywo:', 'mniejsza twarz =', 'okulary znikają.'], 32, 1.4, fill=INK, a='start'), h=650),
    notes="""Po pierwsze: zmiana warunków. Model nauczony na słonecznych ulicach gubi się w śniegu albo nocą. Widzieliśmy to dziś na własne oczy, kiedy model od twarzy przestawał widzieć okulary, bo twarz była mniejsza niż na zdjęciach, na których się uczył.""")

_N = 24
_hairpx = {(i, round(2 + i * .8)) for i in range(_N)}
_fine = [''.join('h' if (i, j) in _hairpx else '.' for i in range(_N)) for j in range(_N)]
_coarse = []
for J in range(3):
    row = []
    for I in range(3):
        n_ = sum((i, j) in _hairpx for i in range(I * 8, I * 8 + 8) for j in range(J * 8, J * 8 + 8))
        row.append(n_)
    _coarse.append(row)


def _mix(n_):
    a = n_ / 64
    base, hc = (233, 216, 200), (59, 42, 34)
    return '#%02X%02X%02X' % tuple(round(b + (h - b) * a) for b, h in zip(base, hc))


slide('2. Cienkie rzeczy znikają przy zmniejszaniu', S(
    grid(140, 20, 20, _fine, {'h': '#3B2A22', '.': '#E9D8C8'}), t(380, 550, 'pojedynczy włos: 1–2 piksele szerokości', 28, MUTED),
    arr(700, 260, 860, 260, ORANGE, 6), t(780, 230, 'zmniejsz 8×', 26, ORANGE, w=600),
    grid(940, 20, 160, ['abc'] * 3, lambda i, j, ch: _mix(_coarse[j][i])), t(1180, 550, 'został ledwo widoczny ślad', 28, MUTED), h=580),
    notes="""Po drugie: cienkie rzeczy. Pojedynczy włos, kabel, siatka ogrodzenia czy oprawka okularów mają szerokość jednego, dwóch pikseli. Kiedy sieć po drodze zmniejsza obraz, takie detale po prostu znikają.""")

slide('3. Szybkość: dokładność kontra czas', S(
    l(300, 400, 1500, 400, INK, 3), *[l(300 + k_ * 100, 395, 300 + k_ * 100, 410, INK, 3) + t(300 + k_ * 100, 450, f'{k_ / 10:.1f}'.replace('.', ','), 24, MUTED, f=F_M) for k_ in range(13)],
    t(1500, 490, 'sekundy', 24, MUTED, 'end'),
    t(280, 140, 'duży, dokładny model', 30, INK, 'end', 600, F_H), r(300, 100, 1200, 70, '#6B7681', rx=8), t(900, 147, '1 klatka: 1,2 s', 30, '#FFFFFF', w=600),
    t(280, 290, 'model z demo', 30, INK, 'end', 600, F_H),
    *[r(302 + k_ * 100, 250, 94, 70, CYAN, rx=8) for k_ in range(12)], t(900, 230, '12 klatek w tym samym czasie', 26, CYAN, w=600), h=520),
    cap='Na telefonie liczy się każda milisekunda.',
    notes="""Po trzecie: szybkość. Przykład z przygotowania tego wykładu: duży, bardzo dokładny model do twarzy liczył jedną klatkę przez 1,2 sekundy. Ten, którego używaliśmy w demo, jest mniejszy i robi to w jedną dziesiątą sekundy. Wybór modelu to zawsze kompromis między dokładnością a szybkością, a na telefonie liczy się każda milisekunda.""")

_ann = [('pełna maska', 'najdroższa', sheep(0, 0, 1.7, CYAN, CYAN), 1.0),
        ('sam prostokąt', 'tańszy', sheep(0, 0, 1.7) + r(-158, -98, 286, 194, st=ORANGE, sw=6, rx=8), .3),
        ('jedno kliknięcie', 'najtańsze', sheep(0, 0, 1.7) + c(-10, -10, 14, ORANGE, '#FFFFFF', 4), .1),
        ('maska od SAM', 'człowiek tylko poprawia', sheep(0, 0, 1.7, CYAN, CYAN) + c(-10, -10, 14, ORANGE, '#FFFFFF', 4), .2)]
slide('4. Koszt danych: uczenie z tańszych wskazówek', S(
    *[panel(r(0, 0, 400, 300, '#86A866') + g(sh, 200, 160), 20 + k_ * 400, 0, 360, 270, 400, 300)
      + t(200 + k_ * 400, 330, n_, 30, INK, w=600, f=F_H) + t(200 + k_ * 400, 370, sub, 26, MUTED)
      + r(40 + k_ * 400, 410, 320 * cost, 30, ORANGE, rx=6) for k_, (n_, sub, sh, cost) in enumerate(_ann)],
    t(20, 490, 'koszt pracy człowieka →', 26, MUTED, 'start'), h=520),
    cap='Jedno zdjęcie ulicy to półtorej godziny. Tysiące zdjęć to lata pracy.',
    notes="""Po czwarte: koszt danych. Skoro jedno zdjęcie ulicy to półtorej godziny ręcznego zaznaczania, to zbiór z tysiącami zdjęć oznacza lata pracy. Dlatego tyle badań dotyczy uczenia z tańszych wskazówek: samych prostokątów, pojedynczych kliknięć albo zaznaczeń przygotowanych przez modele takie jak SAM.""")

slide('5. Sprawiedliwość: kogo próg w ogóle zauważy', S(
    *[r(160 + k_ * 220, 80, 180, 180, col, rx=16) for k_, col in enumerate(TONES)],
    p('M150 300 L150 330 L770 330 L770 300', st=ORANGE, sw=6), t(460, 380, 'zakres „skóry” dobrany na jasnych twarzach', 28, ORANGE, w=600),
    *[t(250 + k_ * 220, 480, '✓' if k_ < 3 else '✗', 64, '#4E8F3A' if k_ < 3 else ORANGE, w=700) for k_ in range(6)], h=540),
    cap='Jeśli model widział głównie jasną skórę, gorzej radzi sobie z ciemną. Najprościej widać to w trybie 1.',
    notes="""Po piąte: sprawiedliwość. Jeśli model widział głównie jasną skórę, gorzej radzi sobie z ciemną. Najprościej było to widać w trybie pierwszym, gdzie próg koloru dosłownie decyduje, kogo algorytm zauważy.""")

# =====================================================================
section('Na co dzień')
_trees = ''.join(c(x, y, rr, col) for x, y, rr, col in [(60, 120, 90, '#4F8A3C'), (300, 80, 110, '#6E9E4F'), (520, 140, 80, '#4F8A3C'),
                                                        (700, 90, 120, '#6E9E4F'), (200, 260, 70, '#86A866')])
slide('Tryb portretowy i tło w wideorozmowie', S(
    blur('bb', 12), r(180, 0, 300, 560, '#2A2D34', rx=40),
    panel(f'<g filter="url(#bb)">{r(0, 0, 300, 500, "#BFD7E6")}{g(_trees, -250, 0)}</g>' + face(150, 300, .8, NAT, bg=False), 200, 30, 260, 500, 300, 500, st=None, rx=24),
    t(330, 620, 'telefon wycina osobę i rozmywa resztę', 28, INK, w=600, f=F_H),
    r(700, 60, 820, 470, '#3C4248', rx=20), r(600, 530, 1020, 30, '#5B6168', rx=10),
    panel(r(0, 0, 800, 500, '#F4D35E') + r(0, 300, 800, 200, '#E9C98F') + p('M0 300 Q200 270 400 296 T800 290 L800 310 L0 310 Z', '#4C9DB8')
          + face(400, 280, 1, NAT, bg=False), 730, 85, 760, 420, 800, 500, st=None, rx=8),
    t(1110, 620, 'wideorozmowa: to samo, kilkadziesiąt razy na sekundę', 28, INK, w=600, f=F_H), h=650),
    notes="""[ok. 4 min · start 1:21]

Segmentacja jest wokół nas, tylko zwykle jej nie zauważamy, bo dobrze działa.

Tryb portretowy w telefonie: telefon wycina osobę i rozmywa wszystko za nią. Rozmyte albo podmienione tło w wideorozmowie: to samo, tylko kilkadziesiąt razy na sekundę, często modelem bardzo podobnym do tego z trybu drugiego.""")

_arg = '<g transform="translate(0 -95)">' + face(0, 0, 1, mono('none', 'none', gl='#7A3B5E'), bg=False, glw=12) + '</g>'
slide('Filtr z wirtualnymi okularami', S(
    panel(g(face(0, 0, 1, NAT, glasses=False) + face(0, 0, 1, mono('none', 'none', gl=HAIR), bg=False, glw=12), 180, 200), 260, 0, 380, 486, 360, 460, rx=12),
    t(450, 550, 'aplikacja wie, gdzie są oczy ✓', 30, '#4E8F3A', w=600, f=F_H),
    panel(g(face(0, 0, 1, NAT, glasses=False) + _arg, 180, 200), 960, 0, 380, 486, 360, 460, rx=12),
    t(1150, 550, 'bez tego okulary lądują na czole ✗', 30, ORANGE, w=600, f=F_H), h=600),
    notes="""Filtry z wirtualnymi okularami: aplikacja musi wiedzieć, gdzie dokładnie są oczy, żeby okulary nie wylądowały na czole.""")

_sat = (r(0, 0, 800, 500, '#5E7F4A') + ''.join(r(380 + (k_ % 5) * 80, 40 + (k_ // 5) * 90, 60, 60, '#B9B2A6', '#FFFFFF', 3) for k_ in range(20))
        + p('M0 380 L800 300', st='#E9E2D3', sw=26) + p('M300 0 L340 500', st='#E9E2D3', sw=22) + c(140, 140, 90, '#3F6B33'))
slide('Samochód, lekarz, mapa', S(
    panel(_street('pan'), 20, 40, 490, 306, 800, 500), t(265, 420, 'auto: jezdnia, chodnik, pieszy', 28, INK, w=600, f=F_H),
    _ct(800, 190, .9), t(800, 420, 'lekarz: czy guz się zmniejszył', 28, INK, w=600, f=F_H),
    panel(_sat, 1090, 40, 490, 306, 800, 500), t(1335, 420, 'mapy: budynki, drogi, lasy', 28, INK, w=600, f=F_H), h=480),
    notes="""Samochód autonomiczny musi w każdej chwili wiedzieć, gdzie jest jezdnia, gdzie chodnik, a gdzie pieszy. W medycynie lekarz zaznacza guz na skanie, żeby zmierzyć, czy po leczeniu się zmniejszył, a segmentacja może tę pracę przyspieszyć. A budynki, drogi i lasy, które widzicie na mapach w internecie, w dużej części zostały wyodrębnione ze zdjęć satelitarnych właśnie w ten sposób.""")

_miss = _street('pan').replace(f'fill="{YELLOW}"', 'fill="none"') + g(p('M-58 0 L-50 -88 Q-46 -110 -20 -112 L20 -112 Q46 -110 50 -88 L58 0 Z', st=ORANGE, sw=6, dash='12 8')
                                                                   + c(0, -150, 34, st=ORANGE, sw=6), 620, 380, .7)
slide('Nie każda pomyłka jest równie groźna', S(
    panel(r(0, 0, 800, 500, '#2A2D34') + face(380, 260, 1, mono(ORANGE, 'none'), glasses=False, bg=False)
          + hand(640, 470, 1.6, ORANGE) + r(600, 300, 120, 80, '#2A2D34'), 20, 0, 740, 463, 800, 500),
    t(390, 520, 'znika kawałek ręki w wideorozmowie', 30, INK, w=600, f=F_H), t(390, 562, 'nic się nie stanie', 26, MUTED),
    panel(_miss, 840, 0, 740, 463, 800, 500),
    t(1210, 520, 'samochód nie zauważa pieszego', 30, ORANGE, w=600, f=F_H), t(1210, 562, 'konsekwencje są poważne', 26, MUTED), h=590),
    cap='Warto pytać nie tylko, jak często system się myli, ale też jakie błędy popełnia.',
    notes="""Zauważcie, że pomyłki nie są tu równie groźne. Jeśli w wideorozmowie zniknie wam kawałek ręki, nic się nie stanie. Jeśli samochód nie zauważy pieszego albo program źle zaznaczy granicę guza, konsekwencje są poważne. Dlatego przy każdym takim systemie warto pytać nie tylko, jak często się myli, ale też jakie błędy popełnia.""")

# =====================================================================
section('Zamknięcie')
slide('Ten sam obraz. Inna odpowiedź.', img('grafiki/rubin_vase_decided.png', 960, 640),
      cap='Środek pomalowany na turkusowo: ktoś zdecydował, że obiektem jest wazon.',
      notes="""[ok. 2 min · start 1:25]

Wracamy do wazonu. Ten sam obrazek, ale teraz środek jest pomalowany na turkusowo. Ktoś podjął decyzję: to jest wazon, to jest obiekt.""")


def _photos(x, y):
    return ''.join(r(x - 80 + k_ * 20, y - 70 + k_ * 16, 150, 110, col, INK, 3, 8) for k_, col in enumerate(['#BFD7E6', '#86A866', '#E9C98F']))


_hid = [('jakie kategorie wybrano', ''.join(r(560 - 470 + 0, 140 + k_ * 44, 26, 26, col, rx=4) for k_, col in enumerate([CYAN, SKIN, HAIR, CLOTH]))),
        ('kto i jak zaznaczał zdjęcia', p('M-40 60 L60 -40 L80 -20 L-20 80 Z', ORANGE) + p('M-40 60 L-52 92 L-20 80 Z', INK)),
        ('jakie obrazy model widział', _photos(0, 0))]
slide('Każdy system podejmuje taką decyzję', S(
    *[r(40 + k_ * 520, 0, 480, 420, '#FFFFFF', LINE, 2, 16) + t(280 + k_ * 520, 360, n_, 30, INK, w=600, f=F_H) for k_, (n_, _) in enumerate(_hid)],
    *[r(200, 130 + k_ * 44, 26, 26, col, rx=4) + r(240, 136 + k_ * 44, 140, 14, LINE, rx=7) for k_, col in enumerate([CYAN, SKIN, HAIR, CLOTH])],
    g(_hid[1][1], 800, 180), g(_photos(0, 0), 1320, 190), h=440),
    cap='…nawet jeśli nikt tego głośno nie mówi.',
    notes="""Każdy system segmentacji podejmuje taką decyzję, nawet jeśli nikt tego głośno nie mówi. Ukrywa się ona w tym, jakie kategorie wybrano, kto i jak zaznaczał zdjęcia i jakie obrazy model zobaczył podczas nauki.""")

slide('Dziś widzieliście cztery takie decyzje', S(
    *[r(20 + k_ * 400, 0, 370, 430, '#FFFFFF', LINE, 2, 16) for k_ in range(4)],
    r(125, 70, 160, 160, ORANGE, rx=12), t(205, 320, 'obiekt = kolor', 30, INK, w=600, f=F_H),
    *[r(470 + (k_ % 3) * 90, 60 + (k_ // 3) * 90, 76, 76, col, rx=8) for k_, (col, _) in enumerate(_six)],
    t(605, 320, '6 kategorii', 30, INK, w=600, f=F_H), t(605, 360, 'i żadnych okularów', 26, MUTED),
    panel(g(face(0, 0, 1, CLS), 180, 200), 925, 40, 150, 192, 360, 460, rx=8),
    t(1000, 320, '19 części', 30, INK, w=600, f=F_H), t(1000, 360, 'twarz na środku', 26, MUTED),
    panel(g(face(0, 0) + f'<g opacity=".8">{face(0, 0, 1, GLM, bg=False, glw=14)}</g>', 180, 200), 1240, 40, 100, 128, 360, 460, rx=6),
    panel(g(face(0, 0) + f'<g opacity=".8">{face(0, 0, 1, FACEM, bg=False, glw=14)}</g>', 180, 200), 1350, 40, 100, 128, 360, 460, rx=6),
    panel(g(face(0, 0) + f'<g opacity=".8">{face(0, 0, 1, mono(CYAN, "none"), bg=False)}</g>', 180, 200), 1460, 40, 100, 128, 360, 460, rx=6),
    t(1405, 320, 'SAM: kilka odpowiedzi', 30, INK, w=600, f=F_H), t(1405, 360, 'wybiera człowiek', 26, MUTED), h=450),
    cap='Pytajcie nie tylko, jak system jest dokładny, ale też: kto i jak zdecydował, co jest obiektem.',
    notes="""Dziś widzieliście trzy takie decyzje. Dla pierwszej metody obiekt to kolor. Dla drugiej świat ma sześć kategorii i nie ma w nim okularów. Dla trzeciej twarz ma 19 części i jest na środku zdjęcia. A SAM pokazuje czwarte wyjście: jeśli nie wiadomo, o co chodzi, dać kilka odpowiedzi i pozwolić wybrać człowiekowi.

Więc kiedy następnym razem zobaczycie system, który coś zaznacza na obrazie, warto zapytać nie tylko, jak jest dokładny, ale też: kto i jak zdecydował, co jest obiektem.""")

slide('', dark=True, raw=(
    f'<div style="flex:1;display:flex;flex-direction:column;justify-content:center;gap:32px">'
    f'<p style="font-family:{F_H};font-weight:600;font-size:26px;color:{ORANGE};letter-spacing:4px;text-transform:uppercase">Na koniec</p>'
    f'<h1 style="font-family:{F_H};font-weight:700;font-size:100px;line-height:1.08;color:{PAPER};width:1600px">Który piksel nauczycie znaczenia?</h1>'
    f'<p style="font-size:32px;line-height:1.5;color:#B9C0C6;width:1400px">Jaką granicę na obrazie warto nauczyć komputer rozpoznawać w waszej dziedzinie?</p>'
    f'<p style="font-family:{F_M};font-size:26px;color:#6E7A82">Kod demo: repozytorium segmentation_presentation · działa na zwykłym laptopie</p></div>'),
    notes="""[ok. 3 min + dyskusja · start 1:27]

Na koniec zostawiam was z pytaniem ze slajdu: który piksel nauczycie znaczenia? Inaczej mówiąc: jaką granicę na obrazie warto by nauczyć komputer rozpoznawać w waszej dziedzinie?

Każda granica, o której dziś mówiliśmy, od oddzielenia włosów od twarzy po kształt oprawki okularów, była kiedyś nierozwiązanym problemem. Często przełom nie przychodził z genialnego pomysłu, tylko z dobrze przygotowanych danych albo z zauważenia drobnego błędu.

Cały kod dzisiejszego demo jest w repozytorium segmentation_presentation. Działa na zwykłym laptopie, więc można go uruchomić u siebie i sprawdzić, kiedy te modele się mylą.

Kilka pytań na rozmowę.
Jak zebrać zdjęcia, żeby model od twarzy działał dobrze na zwykłej kamerze, a nie tylko na zdjęciach celebrytów?
Czy okulary powinny być osobną kategorią, częścią twarzy, a może czymś półprzezroczystym? Od czego to zależy?
Gdzie w waszej dziedzinie segmentacja mogłaby zaoszczędzić komuś godzin ręcznej pracy?""")

if __name__ == '__main__':
    build()
