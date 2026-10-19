"""Regenerates the BT logo files (SVG + PNG).

Usage: FONT_DIR=/path/to/fonts [CAR=sport|lambo|p308] python3 build_logo.py assets/logo
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

def sym(paths):
    """Left-half shapes plus their mirror images."""
    return paths + [mirror(d) for d in paths]

TYRE_L = 'M224,384 L280,384 L280,410 Q280,416 274,416 L230,416 Q224,416 224,410 Z'

# Each car is drawn front-on in a 1000-wide box, roughly y=150..416.
# body: main green silhouette (windscreen cut out with evenodd)
# greens/darks: extra green parts and dark cut-ins; strokes: light-grey lines (d, width, opacity)
CARS = {
    # Low, wide sports car: raked windscreen, flared fenders, swept headlights, splitter.
    'sport': dict(
        body=('M446,190 L554,190 Q568,190 577,199 L642,250 C692,254 736,262 762,276 '
              'C782,288 792,310 792,335 L790,374 L760,384 L240,384 L210,374 L208,335 '
              'C208,310 218,288 238,276 C264,262 308,254 358,250 L423,199 Q432,190 446,190 Z '
              'M452,203 L548,203 L607,247 L393,247 Z'),
        tyres=sym([TYRE_L]),
        greens=sym(['M360,250 L338,236 Q314,230 306,243 Q312,254 350,256 Z'])
               + ['M290,390 L710,390 L702,397 L298,397 Z'],
        darks=sym(['M232,296 L382,320 L374,334 L296,330 Q256,324 236,310 Z',
                   'M226,348 L326,348 L350,376 L240,376 Q228,370 226,360 Z',
                   'M432,262 L446,262 L478,304 L470,306 Z'])
              + ['M392,350 L608,350 L592,376 L408,376 Z'],
        strokes=[(d, 3.5, 1) for d in sym(['M252,305 L368,324'])] + [('M412,363 L588,363', 2.5, 0.6)],
        transform='translate(500 416) scale(1.18) translate(-500 -416)'),

    # Lamborghini-style supercar: tiny cabin set far back, very wide and low,
    # sharp faceted nose, Y-shaped light signature, big angular intakes.
    'lambo': dict(
        body=('M458,226 L542,226 L590,238 L636,262 L706,266 L756,276 L792,298 L802,330 '
              'L794,372 L764,384 L236,384 L206,372 L198,330 L208,298 L244,276 L294,266 '
              'L364,262 L410,238 Z M466,236 L534,236 L604,259 L396,259 Z'),
        tyres=sym(['M218,384 L274,384 L274,408 Q274,414 268,414 L224,414 Q218,414 218,408 Z']),
        greens=sym(['M362,258 L344,248 Q328,244 324,252 Q330,260 356,262 Z'])
               + ['M262,390 L738,390 L726,398 L274,398 Z'],
        darks=sym(['M220,302 L356,290 L398,298 L372,310 L300,314 L234,320 Z',         # slit headlight
                   'M210,334 L318,320 L374,352 L352,378 L236,378 L212,358 Z',         # big faceted intake
                   'M436,272 L446,272 L488,314 L484,318 Z'])                          # bonnet V
              + ['M424,348 L576,348 L556,378 L444,378 Z'],                            # centre nose intake
        strokes=[(d, 3.5, 1) for d in sym(['M236,309 L312,303 L352,296', 'M312,303 L330,311'])]
                + [(d, 3, 0.7) for d in sym(['M236,366 L340,334', 'M262,374 L352,348'])],
        transform='translate(500 416) scale(1.28) translate(-500 -416)'),

    # Peugeot 308-style hatchback: taller cabin, slim headlights, vertical
    # "fang" daytime running lights and a wide frameless grille.
    'p308': dict(
        body=('M414,152 L586,152 Q602,152 610,164 L668,250 C710,254 748,262 768,280 '
              'C782,295 786,315 786,340 L782,374 L760,388 L240,388 L218,374 L214,340 '
              'C214,315 218,295 232,280 C252,262 290,254 332,250 L390,164 Q398,152 414,152 Z '
              'M422,163 L578,163 L644,247 L356,247 Z'),
        tyres=sym(['M228,388 L280,388 L280,410 Q280,416 274,416 L234,416 Q228,416 228,410 Z']),
        greens=sym(['M336,250 L314,232 Q292,226 286,240 Q290,254 328,256 Z']),
        darks=sym(['M230,292 L366,304 L382,318 L252,320 Q236,312 230,292 Z',          # slim headlight
                   'M226,346 L250,346 L266,376 L232,376 Q226,366 226,356 Z',          # corner vent
                   'M404,262 L412,262 L450,306 L446,308 Z'])                          # bonnet crease
              + ['M326,326 L674,326 L652,374 L348,374 Z'],                            # wide grille
        strokes=[(d, 3.5, 1) for d in sym(['M246,304 L364,311'])]
                + [(d, 5, 1) for d in sym(['M262,322 L280,372'])]                     # fang DRL
                + [(d, 3, 1) for d in sym(['M284,322 L294,348'])]
                + [(f'M{x0},{y} L{x1},{y}', 2, 0.45) for x0, x1, y in ((345, 655, 340), (352, 648, 352), (358, 642, 364))],
        transform='translate(500 416) scale(1.08) translate(-500 -416)'),

    # Mercedes C-Class-style saloon: upright wide grille with horizontal slats,
    # slim LED headlights with a swoosh DRL, sculpted bonnet power-domes.
    'merc': dict(
        body=('M420,160 L580,160 Q598,160 608,172 L664,246 C712,250 750,258 770,276 '
              'C784,290 788,312 788,340 L784,376 L762,390 L238,390 L216,376 L212,340 '
              'C212,312 216,290 230,276 C250,258 288,250 336,246 L392,172 Q402,160 420,160 Z '
              'M430,174 L570,174 L634,242 L366,242 Z'),
        tyres=sym(['M226,390 L280,390 L280,412 Q280,418 274,418 L232,418 Q226,418 226,412 Z']),
        greens=sym(['M338,246 L316,230 Q294,224 288,238 Q292,252 330,254 Z']),
        darks=sym(['M228,286 L350,286 L372,300 L248,312 Q232,306 228,286 Z',          # headlight
                   'M226,350 L258,350 L272,378 L236,378 Q226,370 226,360 Z',          # fog vent
                   'M394,256 L412,256 L430,282 L418,284 Z',                           # bonnet dome
                   ])
              + ['M372,314 L628,314 L616,376 L384,376 Z'],                            # grille
        strokes=[(d, 3.5, 1) for d in sym(['M244,300 L350,296'])]
                + [(f'M{x0},{y} L{x1},{y}', 3, 0.7) for x0, x1, y in ((392, 608, 330), (390, 610, 344), (388, 612, 358))],
        transform='translate(500 416) scale(1.1) translate(-500 -416)'),
}
CAR = CARS[os.environ.get('CAR', 'merc')]

def car_group(transform=''):
    t = f' transform="{transform}"' if transform else ''
    return (f'<g{t}>\n' + ''.join(f'    <path d="{d}" fill="{TYRE}"/>\n' for d in CAR['tyres'])
            + f'    <path d="{CAR["body"]}" fill="url(#carGrad)" fill-rule="evenodd"/>\n'
            + ''.join(f'    <path d="{d}" fill="url(#carGrad)"/>\n' for d in CAR['greens'])
            + ''.join(f'    <path d="{d}" fill="{DARK}"/>\n' for d in CAR['darks'])
            + ''.join(f'    <path d="{d}" fill="none" stroke="{GREY}" stroke-width="{w}" stroke-linecap="round" opacity="{o}"/>\n'
                      for d, w, o in CAR['strokes'])
            + '  </g>')

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
  {car_group(CAR['transform'])}
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
