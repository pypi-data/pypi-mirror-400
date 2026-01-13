# ==============================
# ===== Telugu core ============
# ==============================

import re, unicodedata

TELUGU_BLOCK = r'\u0C00-\u0C7F'
telugu_span_re = re.compile(rf'([{TELUGU_BLOCK}]+)')
NON_TELUGU    = re.compile(rf'[^{TELUGU_BLOCK}]')

# Signs & specials
VIRAMAM   = '్'
SUNNA     = 'ం'
ARASUNNA  = 'ఁ'
VISARGA   = 'ః'
CANDRABINDUVU = 'ఀ'
NAKARAM   = 'ౝ'
AVAGRAHAM = 'ఽ'
ZWJ       = '\u200D'
ZWNJ      = '\u200C'

# Vowels
V_INDEP = {
    'అ':'a','ఆ':'ā','ఇ':'i','ఈ':'ī','ఉ':'u','ఊ':'ū',
    'ఋ':'r̥','ౠ':'r̥̄','ఌ':'l̥','ౡ':'l̥̄',
    'ఎ':'e','ఏ':'ē','ఐ':'ai','ఒ':'o','ఓ':'ō','ఔ':'au'
}
V_SIGN = {
    'ా':'ā','ి':'i','ీ':'ī','ు':'u','ూ':'ū',
    'ృ':'r̥','ౄ':'r̥̄','ౢ':'l̥','ౣ':'l̥̄',
    'ె':'e','ే':'ē','ై':'ai','ొ':'o','ో':'ō','ౌ':'au'
}

# Consonants
C_BASE = {
    'క':'k','ఖ':'kʰ','గ':'g','ఘ':'gʰ','ఙ':'ṅ',
    'చ':'c','ఛ':'cʰ','జ':'j','ఝ':'jʰ','ఞ':'ñ',
    'ట':'ṭ','ఠ':'ṭʰ','డ':'ḍ','ఢ':'ḍʰ','ణ':'ṇ',
    'త':'t','థ':'tʰ','ద':'d','ధ':'dʰ','న':'n',
    'ప':'p','ఫ':'pʰ','బ':'b','భ':'bʰ','మ':'m',
    'య':'y','ర':'r','ల':'l','వ':'v',
    'శ':'ś','ష':'ṣ','స':'s','హ':'h',
    'ళ':'ḷ','ఱ':'ṟ','ఴ':'ḻ',
    'ౘ':'ĉ','ౙ':'z'
}
DIGITS = {'౦':'0','౧':'1','౨':'2','౩':'3','౪':'4','౫':'5','౬':'6','౭':'7','౮':'8','౯':'9'}

# Sunna assimilation (fast dict)
_ASSIM = {}
for c in 'కఖగఘ': _ASSIM[c] = 'ṅ'   # velars
for c in 'చఛజఝ': _ASSIM[c] = 'ñ'   # palatals
for c in 'టఠడఢ': _ASSIM[c] = 'ṇ'   # retroflex
for c in 'తథదధ': _ASSIM[c] = 'n'   # dentals
for c in 'పఫబభ': _ASSIM[c] = 'm'   # labials

def _sunna_assim(next_char: str) -> str:
    return _ASSIM.get(next_char, 'ṁ')

def _next_base_index(s: str, j: int) -> int:
    # lookahead for anusvara: skip ZWJ/ZWNJ and non-letters; return index of next base consonant or -1
    n = len(s)
    while j < n:
        ch = s[j]
        if ch in (ZWJ, ZWNJ):
            j += 1; continue
        if ch in C_BASE or ch in V_INDEP or ch in DIGITS or ch in (VISARGA, CANDRABINDUVU, ARASUNNA):
            return j
        j += 1
    return -1

# Precomposed
PRECOMP_INHERENT = {c: C_BASE[c] + 'a' for c in C_BASE}
PRECOMP_MATRA    = {(c, m): C_BASE[c] + V_SIGN[m] for c in C_BASE for m in V_SIGN}

def transliterate_telugu_span_core(s: str, do_nfc: bool) -> str:
    s = unicodedata.normalize('NFC', s) if do_nfc else s

    out = []
    i = 0
    n = len(s)
    append = out.append

    while i < n:
        ch = s[i]

        if ch == ZWJ or ch == ZWNJ:
            i += 1; continue

        v_ind = V_INDEP.get(ch)
        if v_ind is not None:
            append(v_ind); i += 1; continue

        d = DIGITS.get(ch)
        if d is not None:
            append(d); i += 1; continue

        if ch == ARASUNNA:
            append('n̆'); i += 1; continue

        if ch == VISARGA:
            append('ḥ'); i += 1; continue

        if ch == CANDRABINDUVU:
            append('m̐'); i += 1; continue

        if ch == NAKARAM:
            append('n'); i += 1; continue

        if ch == AVAGRAHAM:
            append("'"); i += 1; continue

        if ch == SUNNA:
            j = _next_base_index(s, i + 1)
            if j != -1 and s[j] in C_BASE:
                append(_sunna_assim(s[j]))
            else:
                append('ṁ')
            i += 1; continue

        if ch in C_BASE:
            last = ch
            j = i + 1
            terminated = False

            while True:
                if j >= n or s[j] != VIRAMAM:
                    break
                j += 1
                if j < n and s[j] == ZWJ:
                    j += 1
                elif j < n and s[j] == ZWNJ:
                    append(C_BASE[last])
                    i = j + 1
                    terminated = True
                    break
                if j < n and s[j] in C_BASE:
                    append(C_BASE[last])  # bare consonant in stack
                    last = s[j]
                    j += 1
                    continue
                # explicit halant with nothing usable after
                append(C_BASE[last])
                i = j
                terminated = True
                break

            if terminated:
                continue

            if j < n and s[j] == VIRAMAM:
                append(C_BASE[last])
                i = j + 1
                continue

            if j < n and s[j] in V_SIGN:
                append(PRECOMP_MATRA[(last, s[j])])
                i = j + 1
                continue

            append(PRECOMP_INHERENT[last])
            i = j
            continue

        append(ch); i += 1

    return ''.join(out)