"""Generate the CoreS3 LVGL GUI prototype (mock data) for the IX3212 PDM controller.

Usage: pip install pyyaml; python3 gen2.py  ->  writes pdm_ui_v14.yaml next to this file.
"""
import yaml

# ---------- YAML emit helpers ----------
class Hx(int): pass
class Lam(str): pass
class D(yaml.SafeDumper): pass
D.add_representer(Hx, lambda d, v: d.represent_scalar('tag:yaml.org,2002:int', '0x%06X' % int(v)))
D.add_representer(Lam, lambda d, v: d.represent_scalar('!lambda', str(v), style="'"))
D.ignore_aliases = lambda *a: True

C = {k: Hx(v) for k, v in dict(
    bg=0x101412, surf=0x1A1F1C, tile=0x171B19, line=0x2A302C, text=0xE8ECE6, muted=0x9AA39C,
    amber=0xF2A93B, amberBg=0x2A2210, amberTxt=0xFFC56B, teal=0x3FB8A8, blue=0x8FA3FF,
    green=0x57C78A, ink=0x101412, press=0x3A423D, fault=0xFF6B5E, faultBg=0x3A1512,
    faultTxt=0xFF8A7F, soft=0xC9D0C8, off=0x7D867F, track=0x1F2522, key=0x262C29,
    stop=0x3A423D, bright=0xF1F4EF, divider=0x222925, lscBg=0x122523, lscLine=0x2B5C56,
    lscTxt=0xC7E6E1, faultSub=0xE6B3AD, resetInk=0x1A0A08, border=0x2F3632, haLine=0x3D7A58,
    haTxt=0x8FE0B0, tabSel=0x2C332F).items()}
BACK, NEXT, GEAR = '\uf053', '\uf054', '\uf013'

def lbl(text, font='montserrat_12', color='text', lid=None, **pos):
    d = {}
    if lid: d['id'] = lid
    d['text'] = text
    d.update(pos)
    d['text_font'] = font
    d['text_color'] = C[color]
    return {'label': d}

def dot_lbl(text, font, color, x, y, width, lid=None):
    h = {'montserrat_12': 16, 'montserrat_14': 18, 'montserrat_16': 21, 'montserrat_18': 23}[font]
    d = lbl(text, font, color, lid, x=x, y=y, width=width, height=h)
    d['label']['long_mode'] = 'DOT'
    return d

def box(x, y, w, h, bg, widgets=None, border=None, radius=0, oid=None, hidden=False):
    d = {}
    if oid: d['id'] = oid
    d.update(x=x, y=y, width=w, height=h, bg_color=C[bg], border_width=1 if border else 0)
    if border: d['border_color'] = C[border]
    d.update(radius=radius, pad_all=0, scrollable=False)
    if hidden: d['hidden'] = True
    if widgets: d['widgets'] = widgets
    return {'obj': d}

def btn(x, y, w, h, bg, widgets=None, click=None, border=None, radius=6, pressed='press', bid=None, extra=None):
    d = {}
    if bid: d['id'] = bid
    d.update(x=x, y=y, width=w, height=h, bg_color=C[bg], radius=radius, shadow_width=0, pad_all=0,
             border_width=1 if border else 0)
    if border: d['border_color'] = C[border]
    d['pressed'] = {'bg_color': C[pressed]}
    if extra: d.update(extra)
    if click: d['on_click'] = click
    if widgets: d['widgets'] = widgets
    return {'button': d}

def show(page): return {'lvgl.page.show': page}

# ---------- mock channel data ----------
def ch(n, name, kind, on=False, pwm=100, amps=0.0, limit=10, fault=None, spd=None):
    return dict(n=n, name=name, kind=kind, on=on, pwm=pwm, amps=amps, limit=limit, fault=fault,
                spd=spd if spd is not None else (abs(pwm) or 50))
PDM = {
 1: dict(addr='0x1E', batt='12.8 V', dot='green', ch=[
    ch(1, 'Cabin lights', 'dim', True, 60, 3.1), ch(2, 'Water pump', 'sw'), ch(3, 'Fridge', 'sw', True, amps=4.2),
    ch(4, 'HA Yellow', 'lsc', True, amps=0.9, limit=2.5), ch(5, 'Roof fan', 'hbr', True, -50, 1.6, 5), ch(6, 'Roof fan', 'pair'),
    ch(7, '12V outlets', 'sw', True, amps=0.4, limit=15), ch(8, 'Porch light', 'sw'), ch(9, 'Diesel heater', 'sw', limit=7.5),
    ch(10, 'Inverter remote', 'sw', True, amps=0.2, limit=2.5), ch(11, 'Spare', 'sw'), ch(12, 'Spare', 'sw')]),
 2: dict(addr='0x1F', batt='12.7 V', dot='amber', ch=[
    ch(1, 'Kitchen lights', 'dim', True, 80, 2.4), ch(2, 'Range hood', 'sw'), ch(3, 'Water heater', 'sw', limit=15, fault='Short circuit'),
    ch(4, 'Bath fan', 'sw', True, amps=1.1), ch(5, 'Awning', 'hbr', False, 0, 0, 10, spd=60), ch(6, 'Awning', 'pair'),
    ch(7, 'Garage lights', 'sw', True, amps=0.8), ch(8, 'Starlink', 'sw', True, amps=3.6, limit=7.5), ch(9, 'Router', 'sw', True, amps=0.9, limit=2.5),
    ch(10, 'Bed lights', 'dim', False, 40, limit=10), ch(11, 'Spare', 'sw'), ch(12, 'Spare', 'sw')]),
}
def pages_of(n): return [c for c in PDM[n]['ch'] if c['kind'] != 'pair']
def num(c): return f"CH {c['n']:02d}-{c['n']+1:02d}" if c['kind'] == 'hbr' else f"CH {c['n']:02d}"

# ---------- overview ----------
def tile_view(c):
    k = c['kind']
    if k == 'pair': return 'bg', 'line', 'blue', f"paired w/ {c['n']-1:02d}", 'montserrat_12', None
    if c['fault']: return 'faultBg', 'fault', 'faultTxt', 'SHORT', 'montserrat_18', None
    chip = None
    if k == 'lsc': chip = ('LSC', 'teal')
    if k == 'hbr': chip = ('REV' if c['pwm'] < 0 else 'FWD', 'blue') if c['on'] else ('H-BR', 'blue')
    if k == 'dim' and c['on'] and c['pwm'] < 100: chip = (f"{c['pwm']}%", 'amber')
    if c['on']: return 'amberBg', 'amber', 'amberTxt', f"{c['amps']:.1f} A", 'montserrat_18', chip
    return 'tile', 'line', 'off', 'OFF', 'montserrat_18', chip

def overview(n):
    chs = PDM[n]['ch']
    halves = [chs[:6], chs[6:]]
    faulted = [any(c['fault'] for c in h) for h in halves]
    tabs = []
    for i in (1, 2):
        sel = i == n
        tabs.append(btn(2 + (i-1)*72, 2, 70, 28, 'tabSel' if sel else 'surf',
                        click=None if sel else [show(f'page_overview_{i}')],
                        widgets=[box(10, 10, 7, 7, PDM[i]['dot'], radius=4),
                                 lbl(f'PDM {i}', 'montserrat_14', 'text' if sel else 'muted', x=22, y=6)]))
    tiles = []
    for pg, half in enumerate(halves):
        ws = []
        for idx, c in enumerate(half):
            r, col = divmod(idx, 2)
            bg, bd, vc, val, vfont, chip = tile_view(c)
            target = c['n'] - 1 if c['kind'] == 'pair' else c['n']
            kids = [lbl(f"{c['n']:02d}", 'montserrat_10', 'muted', x=6, y=7),
                    dot_lbl(c['name'], 'montserrat_16', 'text', 24, 4, 124),
                    lbl(val, vfont, vc, x=6, y=28)]
            if chip: kids.append(lbl(chip[0], 'montserrat_12', chip[1], align='BOTTOM_RIGHT', x=-6, y=-6))
            ws.append(btn(4 + col*158, r*56, 154, 52, bg, border=bd, widgets=kids, click=[
                {'globals.set': {'id': 'cur_pdm', 'value': str(n)}},
                {'lvgl.tileview.select': {'id': f'dtv_{n}', 'tile_id': f'dt_{n}_{target}', 'animated': False}},
                show(f'page_detail_{n}')]))
        tiles.append({'id': f'tv_pdm{n}_p{pg+1}', 'row': 0, 'column': pg, 'dir': 'RIGHT' if pg == 0 else 'LEFT', 'widgets': ws})
    hid = 'fault' if faulted[1] else 'muted'
    bar = btn(4, 206, 312, 32, 'bg', border='line', click=[{'if': {
        'condition': {'lambda': f'return id(pdm{n}_page) == 0;'},
        'then': [{'lvgl.tileview.select': {'id': f'tv_pdm{n}', 'tile_id': f'tv_pdm{n}_p2', 'animated': True}},
                 {'script.execute': {'id': f'pdm{n}_bar', 'page': 1}}],
        'else': [{'lvgl.tileview.select': {'id': f'tv_pdm{n}', 'tile_id': f'tv_pdm{n}_p1', 'animated': True}},
                 {'script.execute': {'id': f'pdm{n}_bar', 'page': 0}}]}}],
        widgets=[lbl('CH 1-6', lid=f'bar{n}_l', align='LEFT_MID', x=10),
                 lbl(f'CH 7-12 {NEXT}', color=hid, lid=f'bar{n}_r', align='RIGHT_MID', x=-10),
                 box(143, 11, 8, 8, 'text', radius=4, oid=f'bar{n}_d0'),
                 box(157, 11, 8, 8, 'fault' if faulted[1] else 'stop', radius=4, oid=f'bar{n}_d1')])
    return {'id': f'page_overview_{n}', 'bg_color': C['bg'], 'widgets': [
        box(4, 4, 146, 32, 'surf', radius=8, widgets=tabs),
        btn(156, 4, 52, 32, 'bg', border='haLine', widgets=[lbl('HA', color='haTxt', align='CENTER')]),
        lbl(PDM[n]['batt'], color='soft', x=214, y=12),
        btn(278, 4, 38, 32, 'bg', border='line', click=[show('page_size')],
            widgets=[lbl('SIZE', 'montserrat_10', 'soft', align='CENTER')]),
        {'tileview': {'id': f'tv_pdm{n}', 'x': 0, 'y': 40, 'width': 320, 'height': 164, 'bg_color': C['bg'],
                      'border_width': 0, 'pad_all': 0, 'scrollbar_mode': 'OFF',
                      'on_value': [{'script.execute': {'id': f'pdm{n}_bar',
                                    'page': Lam('return lv_obj_get_x(tile) > 0 ? 1 : 0;')}}],
                      'tiles': tiles}},
        bar]}

def bar_script(n):
    chs = PDM[n]['ch']
    faulted = [any(c['fault'] for c in chs[:6]), any(c['fault'] for c in chs[6:])]
    dim = lambda i: C['fault'] if faulted[i] else C['muted']
    dotoff = lambda i: C['fault'] if faulted[i] else C['stop']
    def ups(l, lc, r, rc, d0, d1):
        return [{'lvgl.label.update': {'id': f'bar{n}_l', 'text': l, 'text_color': lc}},
                {'lvgl.label.update': {'id': f'bar{n}_r', 'text': r, 'text_color': rc}},
                {'lvgl.obj.update': {'id': f'bar{n}_d0', 'bg_color': d0}},
                {'lvgl.obj.update': {'id': f'bar{n}_d1', 'bg_color': d1}}]
    return {'id': f'pdm{n}_bar', 'parameters': {'page': 'int'}, 'then': [
        {'globals.set': {'id': f'pdm{n}_page', 'value': Lam('return page;')}},
        {'if': {'condition': {'lambda': 'return page == 0;'},
                'then': ups('CH 1-6', C['text'], f'CH 7-12 {NEXT}', dim(1), C['text'], dotoff(1)),
                'else': ups(f'{BACK} CH 1-6', dim(0), 'CH 7-12', C['text'], dotoff(0), C['text'])}}]}

# ---------- detail ----------
def seg(prefix, y, h, opts, sel):
    """Segmented control: equal-width buttons in a 296-wide container at x=12. opts = [(label, checked_bg, checked_fg)]"""
    n = len(opts)
    bw = (296 - 4 - 2*(n-1)) // n
    ids = [f'{prefix}_{i}' for i in range(n)]
    kids = []
    for i, (text, cbg, cfg) in enumerate(opts):
        click = [{'lvgl.widget.update': {'id': ids[j], 'state': {'checked': j == i}}} for j in range(n)]
        kids.append(btn(2 + i*(bw+2), 2, bw, h-4, 'surf', bid=ids[i], click=click, extra={
            'text_color': C['muted'],
            'checked': {'bg_color': C[cbg], 'text_color': C[cfg]},
            'state': {'checked': i == sel}},
            widgets=[lbl(text, 'montserrat_18', 'muted', align='CENTER')]))
    # label color must follow the button's checked state, so drop the label's own color
    for k in kids:
        del k['button']['widgets'][0]['label']['text_color']
    return kids

def detail_tile(n, c, pos, last):
    k, cid = c['kind'], f"{n}_{c['n']}"
    amps = c['amps'] if c['on'] and not c['fault'] else 0.0
    pct = min(100, round(amps / c['limit'] * 100))
    name_x = 102 if k == 'hbr' else 84
    ws = [
        btn(0, 0, 44, 40, 'bg', click=[show(f'page_overview_{n}')],
            widgets=[lbl(BACK, 'montserrat_16', 'soft', align='CENTER')]),
        lbl(num(c), 'montserrat_10', 'muted', x=48, y=14),
        dot_lbl(c['name'], 'montserrat_18', 'text', name_x, 9, 222 - name_x, lid=f'dn_{cid}'),
        lbl({'hbr': 'H-BRIDGE', 'lsc': 'LSC'}.get(k, 'HSS'), 'montserrat_10', 'soft', align='TOP_RIGHT', x=-48, y=14),
        btn(276, 0, 44, 40, 'bg', widgets=[lbl(GEAR, 'montserrat_16', 'soft', align='CENTER')], click=[
            {'globals.set': {'id': 'cur_pdm', 'value': str(n)}},
            {'globals.set': {'id': 'cur_ch', 'value': str(c['n'])}},
            {'lvgl.textarea.update': {'id': 'name_ta', 'text': c['name']}},
            show('page_name')]),
        box(0, 40, 320, 1, 'divider'),
        lbl(f'{amps:.1f}', 'montserrat_36', 'faultTxt' if c['fault'] else ('amberTxt' if c['on'] else 'off'), x=12, y=50),
        lbl('A', 'montserrat_14', 'muted', x=78, y=66),
        lbl(f"limit {c['limit']:.1f} A - {pct}%", color='muted', align='TOP_RIGHT', x=-12, y=52),
        lbl(f"PDM {n} - {PDM[n]['addr']}", color='muted', align='TOP_RIGHT', x=-12, y=68),
        {'bar': {'x': 12, 'y': 94, 'width': 296, 'height': 6, 'min_value': 0, 'max_value': 100, 'value': pct,
                 'bg_color': C['track'], 'radius': 3, 'indicator': {'bg_color': C['amber'], 'radius': 3}}},
    ]
    onoff = [('OFF', 'stop', 'bright'), ('ON', 'amber', 'ink')]
    if c['fault']:
        ws.append(box(12, 116, 296, 112, 'faultBg', border='fault', radius=6, oid=f'fc_{cid}', widgets=[
            lbl(c['fault'], 'montserrat_16', 'faultTxt', x=10, y=6),
            lbl('Latched off by the PDM. Reset leaves it off.', color='faultSub', x=10, y=28),
            btn(8, 52, 278, 52, 'fault', pressed='faultTxt', click=[
                {'lvgl.widget.hide': f'fc_{cid}'}, {'lvgl.widget.show': f'fx_{cid}'}],
                widgets=[lbl('Reset fault', 'montserrat_18', 'resetInk', align='CENTER')])]))
        ws.append(box(12, 160, 296, 68, 'surf', radius=8, oid=f'fx_{cid}', hidden=True,
                      widgets=seg(f'sw_{cid}', 0, 68, onoff, 0)))
    elif k == 'sw':
        ws.append(box(12, 160, 296, 68, 'surf', radius=8, widgets=seg(f'sw_{cid}', 0, 68, onoff, 1 if c['on'] else 0)))
    elif k == 'dim':
        ws.append(box(12, 116, 296, 56, 'surf', radius=8, widgets=seg(f'sw_{cid}', 0, 56, onoff, 1 if c['on'] else 0)))
        ws.append({'slider': {'id': f'sl_{cid}', 'x': 26, 'y': 196, 'width': 200, 'height': 12,
                              'min_value': 0, 'max_value': 100, 'value': c['pwm'],
                              'bg_color': C['track'], 'radius': 6,
                              'indicator': {'bg_color': C['amber'], 'radius': 6},
                              'knob': {'bg_color': C['amberTxt'], 'pad_all': 8, 'radius': 14},
                              'on_value': [{'lvgl.label.update': {'id': f'pc_{cid}',
                                            'text': Lam('return str_sprintf("%d%%", (int) x);')}}]}})
        ws.append(box(248, 180, 60, 44, 'bg', border='border', radius=6,
                      widgets=[lbl(f"{c['pwm']}%", 'montserrat_16', lid=f'pc_{cid}', align='CENTER')]))
    elif k == 'hbr':
        sel = 1 if not c['on'] else (0 if c['pwm'] < 0 else 2)
        ws.append(box(12, 116, 296, 56, 'surf', radius=8, widgets=seg(
            f'dir_{cid}', 0, 56, [('REV', 'amber', 'ink'), ('STOP', 'stop', 'bright'), ('FWD', 'amber', 'ink')], sel)))
        g, sp = f'spd_{cid}', f'sp_{cid}'
        upd = {'lvgl.label.update': {'id': sp, 'text': Lam(f'return str_sprintf("%d%%", id({g}));')}}
        ws.append(box(12, 176, 296, 52, 'surf', radius=8, widgets=[
            btn(2, 2, 96, 48, 'key', widgets=[lbl('-', 'montserrat_24', align='CENTER')],
                click=[{'lambda': f'id({g}) = std::max(10, id({g}) - 10);'}, upd]),
            lbl(f"{c['spd']}%", 'montserrat_16', lid=sp, align='CENTER', y=-7),
            lbl('SPEED', 'montserrat_10', 'muted', align='CENTER', y=11),
            btn(198, 2, 96, 48, 'key', widgets=[lbl('+', 'montserrat_24', align='CENTER')],
                click=[{'lambda': f'id({g}) = std::min(100, id({g}) + 10);'}, upd])]))
    elif k == 'lsc':
        ws.append(box(12, 148, 296, 80, 'lscBg', border='lscLine', radius=6, widgets=[
            lbl('LSC', 'montserrat_12', 'teal', x=10, y=10),
            lbl('Follows its hardwired input. No CAN commands - stays on if the CS3, MQTT or HA go down.',
                color='lscTxt', x=48, y=8, width=236)]))
    return {'id': f'dt_{cid}', 'row': 0, 'column': pos,
            'dir': 'RIGHT' if pos == 0 else ('LEFT' if last else 'HOR'), 'widgets': ws}

def detail_page(n):
    ps = pages_of(n)
    tiles = [detail_tile(n, c, i, i == len(ps) - 1) for i, c in enumerate(ps)]
    return {'id': f'page_detail_{n}', 'bg_color': C['bg'], 'widgets': [
        {'tileview': {'id': f'dtv_{n}', 'x': 0, 'y': 0, 'width': 320, 'height': 240, 'bg_color': C['bg'],
                      'border_width': 0, 'pad_all': 0, 'scrollbar_mode': 'OFF', 'tiles': tiles}}]}

# ---------- size test ----------
def size_page():
    ws = [lbl('Tap targets - find your minimum', 'montserrat_16', x=12, y=10),
          lbl('Square = button. Tap each with a fingertip.', color='muted', x=12, y=32)]
    x = 22
    for s in (32, 44, 56, 72):
        ws.append(btn(x, 150 - s, s, s, 'surf', border='amber', pressed='amber'))
        ws.append(lbl(f'{s}px', x=x + s//2 - 14, y=158))
        ws.append(lbl(f'{s/7.87:.1f}mm', 'montserrat_10', 'muted', x=x + s//2 - 17, y=176))
        x += s + 20
    ws.append(btn(12, 196, 96, 40, 'surf', border='line', click=[show('page_overview_1')],
                  widgets=[lbl(f'{BACK} Back', 'montserrat_14', align='CENTER')]))
    return {'id': 'page_size', 'bg_color': C['bg'], 'widgets': ws}

# ---------- naming ----------
def back_to_detail():
    return {'if': {'condition': {'lambda': 'return id(cur_pdm) == 1;'},
                   'then': [show('page_detail_1')], 'else': [show('page_detail_2')]}}

def name_page():
    renames = []
    for n in (1, 2):
        for c in pages_of(n):
            renames.append({'if': {'condition': {'lambda': f"return id(cur_pdm) == {n} && id(cur_ch) == {c['n']};"},
                                   'then': [{'lvgl.label.update': {'id': f"dn_{n}_{c['n']}",
                                             'text': Lam('return std::string(lv_textarea_get_text(id(name_ta)));')}}]}})
    return {'id': 'page_name', 'bg_color': C['bg'], 'widgets': [
        btn(0, 0, 44, 40, 'bg', click=[back_to_detail()], widgets=[lbl(BACK, 'montserrat_16', 'soft', align='CENTER')]),
        lbl('Channel name', 'montserrat_16', x=48, y=12),
        {'textarea': {'id': 'name_ta', 'x': 6, 'y': 42, 'width': 308, 'height': 38, 'one_line': True, 'max_length': 20,
                      'text': '', 'text_font': 'montserrat_16', 'text_color': C['text'], 'bg_color': C['surf'],
                      'border_width': 1, 'border_color': C['amber'], 'radius': 6, 'pad_all': 6}},
        {'keyboard': {'id': 'name_kb', 'textarea': 'name_ta', 'mode': 'TEXT_LOWER', 'align': 'BOTTOM_MID',
                      'width': 320, 'height': 156, 'bg_color': C['bg'], 'border_width': 0, 'pad_all': 2,
                      'items': {'bg_color': C['key'], 'text_color': C['text'], 'text_font': 'montserrat_14',
                                'radius': 5, 'border_width': 0, 'shadow_width': 0,
                                'pressed': {'bg_color': C['amber'], 'text_color': C['ink']}},
                      'on_ready': renames + [back_to_detail()],
                      'on_cancel': [back_to_detail()]}}]}

# ---------- assemble ----------
globals_ = [{'id': f'pdm{n}_page', 'type': 'int', 'initial_value': '0'} for n in (1, 2)]
globals_ += [{'id': 'cur_pdm', 'type': 'int', 'initial_value': '1'}, {'id': 'cur_ch', 'type': 'int', 'initial_value': '1'}]
for n in (1, 2):
    for c in pages_of(n):
        if c['kind'] == 'hbr':
            globals_.append({'id': f"spd_{n}_{c['n']}", 'type': 'int', 'initial_value': str(c['spd'])})

cfg = {
    'globals': globals_,
    'script': [bar_script(1), bar_script(2)],
    'lvgl': {'displays': ['m5cores3_lcd'], 'touchscreens': ['touch'],
             'pages': [overview(1), overview(2), detail_page(1), detail_page(2), size_page(), name_page()]},
}

import os
HERE = os.path.dirname(os.path.abspath(__file__))
head = open(os.path.join(HERE, 'base.yaml')).read().split('esphome:', 1)[1]
banner = """## PDM Controller - on-device prototype of the Claude Design screens.
## Overview (2x3 swipe pages per PDM) -> channel detail (swipe between channels)
## -> gear -> name. Static mock data; controls change on screen only.
## Generated by gen2.py. UNVERIFIED keys are flagged in chat - paste any error.

esphome:"""
body = yaml.dump(cfg, Dumper=D, sort_keys=False, allow_unicode=True, width=200, default_flow_style=False)
open(os.path.join(HERE, 'pdm_ui_v14.yaml'), 'w').write(banner + head.rstrip() + '\n\n' + body)
