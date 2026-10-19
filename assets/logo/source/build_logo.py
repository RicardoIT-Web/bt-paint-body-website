"""Regenerates the BT logo files (SVG + PNG).

Usage: FONT_DIR=/path/to/fonts python3 build_logo.py assets/logo
FONT_DIR must contain the extracted @fontsource/orbitron and @fontsource/open-sans
npm packages (npm pack @fontsource/orbitron @fontsource/open-sans).
Needs: pip install fonttools brotli cairosvg
"""
import sys, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import cairosvg

F = os.environ['FONT_DIR']
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

GREEN = '#8DC63F'; GREEN_HI = '#B2E05A'; GREEN_LO = '#6AAE34'
GREY = '#D9DEE2'; DARK = '#232628'; DARK2 = '#2C3033'; HEX_LINE = '#353A3D'; TYRE = '#3C4145'

def text_path(fontfile, text, size, cx, baseline, max_w=None, tracking=0.0):
    f = TTFont(fontfile); gs = f.getGlyphSet(); cmap = f.getBestCmap()
    upm = f['head'].unitsPerEm
    names = [cmap[ord(c)] for c in text]
    adv = [gs[n].width for n in names]
    track = tracking * upm
    total = sum(adv) + track * (len(names) - 1)
    scale = size / upm
    if max_w and total * scale > max_w:
        scale = max_w / total
    x0 = cx - total * scale / 2
    pen = SVGPathPen(gs)
    x = 0
    for n, a in zip(names, adv):
        tp = TransformPen(pen, (scale, 0, 0, -scale, x0 + x * scale, baseline))
        gs[n].draw(tp)
        x += a + track
    return pen.getCommands(), total * scale

title_d, title_w = text_path(F + '/fontsource-orbitron-5.3.0/package/files/orbitron-latin-700-normal.woff2',
                             'BRUNO TIOPISTO', 60, 500, 478, max_w=560, tracking=0.04)
sub_d, sub_w = text_path(F + '/fontsource-open-sans-5.3.0/package/files/open-sans-latin-700-normal.woff2',
                         'PINTURA E BATE-CHAPAS', 25, 500, 530, max_w=268, tracking=0.03)
gap = 18
bl_end = 500 - sub_w / 2 - gap; br_start = 500 + sub_w / 2 + gap

def hexpts(top, side_x, shoulder_y, bottom_y_off=0):
    # elongated hexagon: points at top/bottom centre, vertical sides
    return [(500, top), (1000 - side_x, shoulder_y), (1000 - side_x, 640 - shoulder_y),
            (500, 640 - top), (side_x, 640 - shoulder_y), (side_x, shoulder_y)]

def poly(pts):
    return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + ' Z'

outer = hexpts(6, 8, 146)       # grey rim
inner = hexpts(24, 26, 151)     # dark field
green = hexpts(48, 52, 158)     # green inner frame centre-line

def mirror(d):
    """Mirror an absolute-coordinate path around the badge's vertical centre (x=500)."""
    out = []
    for tok in d.split():
        cmd = tok[0] if tok[0].isalpha() else ''
        nums = tok[len(cmd):]
        if nums:
            x, y = nums.split(',')
            nums = f'{1000 - float(x):g},{y}'
        out.append(cmd + nums)
    return ' '.join(out)

# Low, wide sports car seen from the front: raked windscreen, wide flared
# fenders, swept headlights, side intakes, splitter and tyres.
body = ('M446,190 L554,190 Q568,190 577,199 L642,250 C692,254 736,262 762,276 '
        'C782,288 792,310 792,335 L790,374 L760,384 L240,384 L210,374 L208,335 '
        'C208,310 218,288 238,276 C264,262 308,254 358,250 L423,199 Q432,190 446,190 Z '
        'M452,203 L548,203 L607,247 L393,247 Z')
left_green = ['M360,250 L338,236 Q314,230 306,243 Q312,254 350,256 Z',          # wing mirror
              ]
left_tyre = 'M224,384 L280,384 L280,410 Q280,416 274,416 L230,416 Q224,416 224,410 Z'
left_dark = ['M232,296 L382,320 L374,334 L296,330 Q256,324 236,310 Z',          # headlight
             'M226,348 L326,348 L350,376 L240,376 Q228,370 226,360 Z',          # side intake
             'M432,262 L446,262 L478,304 L470,306 Z']                           # bonnet vent
tyres = [left_tyre, mirror(left_tyre)]
greens = left_green + [mirror(d) for d in left_green] + ['M290,390 L710,390 L702,397 L298,397 Z']  # splitter
darks = left_dark + [mirror(d) for d in left_dark] + ['M392,350 L608,350 L592,376 L408,376 Z']    # grille
leds = ['M252,305 L368,324', mirror('M252,305 L368,324')]

def car_group(transform=''):
    t = f' transform="{transform}"' if transform else ''
    return (f'<g{t}>\n' + ''.join(f'    <path d="{d}" fill="{TYRE}"/>\n' for d in tyres)
            + f'    <path d="{body}" fill="url(#carGrad)" fill-rule="evenodd"/>\n'
            + ''.join(f'    <path d="{d}" fill="url(#carGrad)"/>\n' for d in greens)
            + ''.join(f'    <path d="{d}" fill="{DARK}"/>\n' for d in darks)
            + ''.join(f'    <path d="{d}" fill="none" stroke="{GREY}" stroke-width="3.5" stroke-linecap="round"/>\n' for d in leds)
            + f'    <path d="M412,363 L588,363" fill="none" stroke="{GREY}" stroke-width="2.5" opacity="0.6"/>\n  </g>')

def badge(pattern=True):
    return f'''<defs>
    <linearGradient id="carGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{GREEN_HI}"/><stop offset="1" stop-color="{GREEN_LO}"/>
    </linearGradient>
    <linearGradient id="fieldGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{DARK2}"/><stop offset="1" stop-color="{DARK}"/>
    </linearGradient>
    <pattern id="honey" width="34" height="58.89" patternUnits="userSpaceOnUse">
      <path d="M17,0 L34,9.81 L34,29.44 L17,39.26 L0,29.44 L0,9.81 Z M17,39.26 L17,58.89 M0,29.44 L0,49.07 M34,29.44 L34,49.07"
            fill="none" stroke="{HEX_LINE}" stroke-width="1.6"/>
    </pattern>
    <clipPath id="field"><path d="{poly(inner)}"/></clipPath>
  </defs>
  <path d="{poly(outer)}" fill="{GREY}" stroke="{GREY}" stroke-width="10" stroke-linejoin="round"/>
  <path d="{poly(inner)}" fill="url(#fieldGrad)"/>
  {'<rect width="1000" height="640" fill="url(#honey)" clip-path="url(#field)" opacity="0.9"/>' if pattern else ''}
  <path d="{poly(green)}" fill="none" stroke="{GREEN}" stroke-width="11" stroke-linejoin="round"/>
  {car_group('translate(500 416) scale(1.18) translate(-500 -416)')}
  <path d="{title_d}" fill="{GREEN}"/>
  <rect x="{bl_end-92:.1f}" y="518" width="92" height="7" rx="1.5" fill="{GREEN}"/>
  <rect x="{br_start:.1f}" y="518" width="92" height="7" rx="1.5" fill="{GREEN}"/>
  <path d="{sub_d}" fill="{GREY}"/>'''

def svg(inner_xml, vb='0 0 1000 640', w=1000, h=640, title='Bruno Tiopisto, Pintura e Bate-Chapas'):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{w}" height="{h}" role="img" aria-label="{title}">\n'
            f'  <title>{title}</title>\n  {inner_xml}\n</svg>\n')

logo = svg(badge())
open(OUT + '/logo.svg', 'w').write(logo)
dark = svg(f'<rect x="-60" y="-60" width="1120" height="760" fill="#121416"/>\n  ' + badge(),
           vb='-60 -60 1120 760', w=1120, h=760)
open(OUT + '/logo-on-dark.svg', 'w').write(dark)

# icon: car mark only, on a rounded dark square
icon = svg(f'''<defs><linearGradient id="carGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{GREEN_HI}"/><stop offset="1" stop-color="{GREEN_LO}"/></linearGradient></defs>
  <rect x="180" y="-10" width="640" height="640" rx="76" fill="{DARK}"/>
  {car_group()}''', vb='180 -10 640 640', w=640, h=640, title='Bruno Tiopisto icon')
open(OUT + '/logo-icon.svg', 'w').write(icon)

for name, w in [('logo', 600), ('logo', 1200), ('logo', 2400)]:
    cairosvg.svg2png(bytestring=logo.encode(), write_to=f'{OUT}/{name}-{w}.png', output_width=w)
cairosvg.svg2png(bytestring=dark.encode(), write_to=f'{OUT}/logo-on-dark-1200.png', output_width=1200)
cairosvg.svg2png(bytestring=dark.encode(), write_to=f'{OUT}/logo-on-dark-2400.png', output_width=2400)
for w in (512, 180, 32):
    cairosvg.svg2png(bytestring=icon.encode(), write_to=f'{OUT}/icon-{w}.png', output_width=w)
print('done', title_w, sub_w)
