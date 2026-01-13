# ==============================
# ===== Odia (Oriya) core ======
# ==============================

import re, unicodedata

ODIA_BLOCK   = r'\u0B00-\u0B7F'
odia_span_re = re.compile(rf'([{ODIA_BLOCK}]+)')
NON_ODIA     = re.compile(rf'[^{ODIA_BLOCK}]')

VIRAMA_OD   = '୍'
ANUSVARA_OD = 'ଂ'
CHANDRA_OD  = 'ଁ'
VISARGA_OD  = 'ଃ'
NUKTA_OD    = '଼'
AVAGRAHA_OD = 'ଽ'
ZWJ         = '\u200D'
ZWNJ        = '\u200C'

V_INDEP_OD = {
    'ଅ':'a','ଆ':'ā','ଇ':'i','ଈ':'ī','ଉ':'u','ଊ':'ū',
    'ଋ':'r̥','ୠ':'r̥̄','ଌ':'l̥','ୡ':'l̥̄',
    'ଏ':'e','ଐ':'ai','ଓ':'o','ଔ':'au',
}

V_SIGN_OD = {
    'ା':'ā','ି':'i','ୀ':'ī','ୁ':'u','ୂ':'ū',
    'ୃ':'r̥','ୄ':'r̥̄','ୢ':'l̥','ୣ':'l̥̄',
    'େ':'e','ୈ':'ai','ୋ':'o','ୌ':'au',
}

C_BASE_OD = {
    'କ':'k','ଖ':'kʰ','ଗ':'g','ଘ':'gʰ','ଙ':'ṅ',
    'ଚ':'c','ଛ':'cʰ','ଜ':'j','ଝ':'jʰ','ଞ':'ñ',
    'ଟ':'ṭ','ଠ':'ṭʰ','ଡ':'ḍ','ଢ':'ḍʰ','ଣ':'ṇ',
    'ତ':'t','ଥ':'tʰ','ଦ':'d','ଧ':'dʰ','ନ':'n',
    'ପ':'p','ଫ':'pʰ','ବ':'b','ଭ':'bʰ','ମ':'m',
    'ଯ':'y','ୟ':'y','ର':'r','ଲ':'l','ଳ':'ḷ',
    'ଶ':'ś','ଷ':'ṣ','ସ':'s','ହ':'h',
    'ୱ':'w',
    'ଡ଼':'ṛ','ଢ଼':'ṛh',
}

DIGITS_OD = {'୦':'0','୧':'1','୨':'2','୩':'3','୪':'4','୫':'5','୬':'6','୭':'7','୮':'8','୯':'9'}

NUKTA_PRECOMP_OD = { 'ଡ': 'ଡ଼', 'ଢ': 'ଢ଼' }

_ASSIM = {}
for c in 'କଖଗଘ':        _ASSIM[c] = 'ṅ'
for c in 'ଚଛଜଝ':        _ASSIM[c] = 'ñ'
for c in 'ଟଠଡଢଡ଼ଢ଼':       _ASSIM[c] = 'ṇ'
for c in 'ତଥଦଧ':        _ASSIM[c] = 'n'
for c in 'ପଫବଭ':        _ASSIM[c] = 'm'

def _anusvara_assim(look: str) -> str:
    return _ASSIM.get(look, 'ṁ')

def _apply_nukta_od(ch: str) -> str:
    return NUKTA_PRECOMP_OD.get(ch, ch)

def _next_base_idx(s: str, j: int) -> int:
    n = len(s)
    while j < n:
        ch = s[j]
        if ch in (ZWJ, ZWNJ, NUKTA_OD):
            j += 1; continue
        if ch in C_BASE_OD or ch in V_INDEP_OD or ch in DIGITS_OD or ch in (VISARGA_OD, CHANDRA_OD):
            return j
        j += 1
    return -1

PRECOMP_INHERENT_OD = {c: C_BASE_OD[c] + 'a' for c in C_BASE_OD}
PRECOMP_MATRA_OD    = {(c, m): C_BASE_OD[c] + V_SIGN_OD[m] for c in C_BASE_OD for m in V_SIGN_OD}

def transliterate_odia_span_core(s: str, do_nfc: bool) -> str:
    s = unicodedata.normalize('NFC', s) if do_nfc else s

    out = []
    i = 0
    n = len(s)
    append = out.append

    while i < n:
        ch = s[i]

        if ch in (ZWJ, ZWNJ):
            i += 1; continue

        v = V_INDEP_OD.get(ch)
        if v is not None:
            append(v); i += 1; continue

        d = DIGITS_OD.get(ch)
        if d is not None:
            append(d); i += 1; continue

        if ch == CHANDRA_OD:
            append('m̐'); i += 1; continue

        if ch == VISARGA_OD:
            append('ḥ'); i += 1; continue

        if ch == AVAGRAHA_OD:
            append("'"); i += 1; continue

        if ch == ANUSVARA_OD:
            j = _next_base_idx(s, i + 1)
            if j != -1 and s[j] in C_BASE_OD:
                look = s[j]
                # consider nukta on lookahead
                if j + 1 < n and s[j+1] == NUKTA_OD:
                    look = _apply_nukta_od(look)
                append(_anusvara_assim(look))
            else:
                append('ṁ')
            i += 1; continue

        if ch in C_BASE_OD:
            j = i + 1
            base = ch
            if j < n and s[j] == NUKTA_OD:
                base = _apply_nukta_od(base)
                j += 1

            last = base
            terminated = False

            while True:
                if j >= n or s[j] != VIRAMA_OD:
                    break
                j += 1
                if j < n and s[j] == ZWJ:
                    j += 1
                elif j < n and s[j] == ZWNJ:
                    append(C_BASE_OD[last])
                    i = j + 1
                    terminated = True
                    break
                if j < n and s[j] in C_BASE_OD:
                    append(C_BASE_OD[last])
                    nxt = s[j]
                    j += 1
                    if j < n and s[j] == NUKTA_OD:
                        nxt = _apply_nukta_od(nxt)
                        j += 1
                    last = nxt
                    continue
                append(C_BASE_OD[last])
                i = j
                terminated = True
                break

            if terminated:
                continue

            if j < n and s[j] == VIRAMA_OD:
                append(C_BASE_OD[last])
                i = j + 1
                continue

            if j < n:
                mat = V_SIGN_OD.get(s[j])
                if mat is not None:
                    append(PRECOMP_MATRA_OD[(last, s[j])])
                    i = j + 1
                    continue

            append(PRECOMP_INHERENT_OD[last])
            i = j
            continue

        append(ch); i += 1

    return ''.join(out)