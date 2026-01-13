# ==============================
# ==== Gunjala Gondi core ======
# ==============================

import re, unicodedata

# Unicode block U+11D60..U+11DAF
GONG_BLOCK        = r'\U00011D60-\U00011DAF'
gunjala_span_re   = re.compile(rf'([{GONG_BLOCK}]+)')
NON_GUNJALA_GONDI = re.compile(rf'[^{GONG_BLOCK}]')

VIRAMA_GG     = '\U00011D97'  # Virama
ANUSVARA_GG   = '\U00011D95'  # Anusvara
VISARGA_GG    = '\U00011D96'  # Visarga
OM_GG         = '\U00011D98'  # OM
ZWJ           = '\u200D'
ZWNJ          = '\u200C'

# Independent vowels
V_INDEP_GG = {
    '\U00011D60':'a','\U00011D61':'ā','\U00011D62':'i','\U00011D63':'ī',
    '\U00011D64':'u','\U00011D65':'ū',
    '\U00011D67':'ē','\U00011D68':'ai','\U00011D6A':'ō','\U00011D6B':'au',
}

# Dependent signs
V_SIGN_GG = {
    '\U00011D8A':'ā','\U00011D8B':'i','\U00011D8C':'ī','\U00011D8D':'u','\U00011D8E':'ū',
    '\U00011D90':'ē','\U00011D91':'ai','\U00011D93':'ō','\U00011D94':'au',
}

C_BASE_GG = {
    '\U00011D6C':'y','\U00011D6D':'v','\U00011D6E':'b','\U00011D6F':'bʰ','\U00011D70':'m',
    '\U00011D71':'k','\U00011D72':'kʰ','\U00011D73':'t','\U00011D74':'tʰ','\U00011D75':'l',
    '\U00011D76':'g','\U00011D77':'gʰ','\U00011D78':'d','\U00011D79':'dʰ','\U00011D7A':'n',
    '\U00011D7B':'c','\U00011D7C':'cʰ','\U00011D7D':'ṭ','\U00011D7E':'ṭʰ','\U00011D7F':'ḷ',
    '\U00011D80':'j','\U00011D81':'jʰ','\U00011D82':'ḍ','\U00011D83':'ḍʰ','\U00011D84':'ṅ',
    '\U00011D85':'p','\U00011D86':'pʰ','\U00011D87':'h','\U00011D88':'r','\U00011D89':'s',
}

DIGITS_GG = {
    '\U00011DA0':'0','\U00011DA1':'1','\U00011DA2':'2','\U00011DA3':'3','\U00011DA4':'4',
    '\U00011DA5':'5','\U00011DA6':'6','\U00011DA7':'7','\U00011DA8':'8','\U00011DA9':'9',
}

_ASSIM = {}
for c in ('\U00011D71','\U00011D72','\U00011D76','\U00011D77'): _ASSIM[c] = 'ṅ'
for c in ('\U00011D7B','\U00011D7C','\U00011D80','\U00011D81'): _ASSIM[c] = 'ñ'
for c in ('\U00011D7D','\U00011D7E','\U00011D82','\U00011D83'): _ASSIM[c] = 'ṇ'
for c in ('\U00011D73','\U00011D74','\U00011D78','\U00011D79'): _ASSIM[c] = 'n'
for c in ('\U00011D85','\U00011D86','\U00011D6E','\U00011D6F'): _ASSIM[c] = 'm'

def _anusvara_assim(next_char: str) -> str:
    return _ASSIM.get(next_char, 'ṁ')

def _next_base_idx(s: str, j: int) -> int:
    n = len(s)
    while j < n:
        ch = s[j]
        if ch in (ZWJ, ZWNJ):
            j += 1; continue
        if ch in C_BASE_GG or ch in V_INDEP_GG or ch in DIGITS_GG or ch in (VISARGA_GG, OM_GG):
            return j
        j += 1
    return -1

PRECOMP_INHERENT_GG = {c: C_BASE_GG[c] + 'a' for c in C_BASE_GG}
PRECOMP_MATRA_GG    = {(c, m): C_BASE_GG[c] + V_SIGN_GG[m] for c in C_BASE_GG for m in V_SIGN_GG}

def transliterate_gunjala_gondi_span_core(s: str, do_nfc: bool) -> str:
    s = unicodedata.normalize('NFC', s) if do_nfc else s

    out = []
    i = 0
    n = len(s)
    append = out.append
    C_HAS = C_BASE_GG.__contains__

    while i < n:
        ch = s[i]

        if ch in (ZWJ, ZWNJ):
            i += 1; continue

        v = V_INDEP_GG.get(ch)
        if v is not None:
            append(v); i += 1; continue

        d = DIGITS_GG.get(ch)
        if d is not None:
            append(d); i += 1; continue

        if ch == OM_GG:
            append('oṃ'); i += 1; continue

        if ch == VISARGA_GG:
            append('ḥ'); i += 1; continue

        if ch == ANUSVARA_GG:
            j = _next_base_idx(s, i + 1)
            if j != -1 and C_HAS(s[j]):
                append(_anusvara_assim(s[j]))
            else:
                append('ṁ')
            i += 1; continue

        if C_HAS(ch):
            last = ch
            j = i + 1
            terminated = False

            while True:
                if j >= n or s[j] != VIRAMA_GG:
                    break
                j += 1
                if j < n and s[j] == ZWJ:
                    j += 1
                elif j < n and s[j] == ZWNJ:
                    append(C_BASE_GG[last])
                    i = j + 1
                    terminated = True
                    break
                if j < n and C_HAS(s[j]):
                    append(C_BASE_GG[last])
                    last = s[j]
                    j += 1
                    continue
                append(C_BASE_GG[last])
                i = j
                terminated = True
                break

            if terminated:
                continue

            if j < n and s[j] == VIRAMA_GG:
                append(C_BASE_GG[last])
                i = j + 1
                continue

            if j < n and s[j] in V_SIGN_GG:
                append(PRECOMP_MATRA_GG[(last, s[j])])
                i = j + 1
                continue

            append(PRECOMP_INHERENT_GG[last])
            i = j
            continue

        append(ch); i += 1

    return ''.join(out)