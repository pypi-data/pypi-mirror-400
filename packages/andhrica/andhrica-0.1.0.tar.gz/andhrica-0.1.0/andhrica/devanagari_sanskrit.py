# ==============================
# === Devanagari (Sanskrit) ====
# ==============================

import re, unicodedata

DEV_BLOCK       = r'\u0900-\u097F'
dev_span_re     = re.compile(rf'([{DEV_BLOCK}]+)')
NON_DEV         = re.compile(rf'[^{DEV_BLOCK}]')

VIRAMA_DV       = '्'
ANUSVARA_DV     = 'ं'
CHANDRABINDU_DV = 'ँ'
VISARGA_DV      = 'ः'
AVAGRAHA_DV     = 'ऽ'
NUKTA_DV        = '़'
ZWJ             = '\u200D'
ZWNJ            = '\u200C'

V_INDEP_DV = {
    'अ':'a','आ':'ā','इ':'i','ई':'ī','उ':'u','ऊ':'ū',
    'ऋ':'r̥','ॠ':'r̥̄','ऌ':'l̥','ॡ':'l̥̄',
    'ए':'e','ऐ':'ai','ओ':'o','औ':'au',
}
V_SIGN_DV = {
    'ा':'ā','ि':'i','ी':'ī','ु':'u','ू':'ū',
    'ृ':'r̥','ॄ':'r̥̄','ॢ':'l̥','ॣ':'l̥̄',
    'े':'e','ै':'ai','ो':'o','ौ':'au',
}
C_BASE_DV = {
    'क':'k','ख':'kʰ','ग':'g','घ':'gʰ','ङ':'ṅ',
    'च':'c','छ':'cʰ','ज':'j','झ':'jʰ','ञ':'ñ',
    'ट':'ṭ','ठ':'ṭʰ','ड':'ḍ','ढ':'ḍʰ','ण':'ṇ',
    'त':'t','थ':'tʰ','द':'d','ध':'dʰ','न':'n',
    'प':'p','फ':'pʰ','ब':'b','भ':'bʰ','म':'m',
    'य':'y','र':'r','ल':'l','व':'v',
    'श':'ś','ष':'ṣ','स':'s','ह':'h',
    'क़':'q','ख़':'x','ग़':'ġ','ज़':'z','फ़':'f','ड़':'ṛ','ढ़':'ṛh','ऱ':'ṟ',
}
DIGITS_DV = {'०':'0','१':'1','२':'2','३':'3','४':'4','५':'5','६':'6','७':'7','८':'8','९':'9'}

_ASSIM = {}
for c in 'कखगघक़ख़ग़': _ASSIM[c] = 'ṅ'
for c in 'चछजझ':     _ASSIM[c] = 'ñ'
for c in 'टठडढढ़ड़':    _ASSIM[c] = 'ṇ'
for c in 'तथदध':     _ASSIM[c] = 'n'
for c in 'पफबभफ़':    _ASSIM[c] = 'm'

def _anusvara_homorganic(next_char: str) -> str:
    return _ASSIM.get(next_char, 'ṃ')

def _next_index_skip_marks(s: str, j: int) -> int:
    n = len(s)
    while j < n:
        ch = s[j]
        if ch in (ZWJ, ZWNJ, NUKTA_DV):
            j += 1; continue
        if ch in C_BASE_DV or V_INDEP_DV.get(ch) is not None or DIGITS_DV.get(ch) is not None or ch in (VISARGA_DV, CHANDRABINDU_DV):
            return j
        j += 1
    return -1

PRECOMP_INHERENT_DV = {c: C_BASE_DV[c] + 'a' for c in C_BASE_DV}
PRECOMP_MATRA_DV    = {(c, m): C_BASE_DV[c] + V_SIGN_DV[m] for c in C_BASE_DV for m in V_SIGN_DV}

def transliterate_devanagari_sanskrit_span_core(s: str, do_nfc: bool) -> str:
    s = unicodedata.normalize('NFC', s) if do_nfc else s

    out = []
    i = 0
    n = len(s)
    append = out.append
    C_HAS = C_BASE_DV.__contains__

    while i < n:
        ch = s[i]

        if ch in (ZWJ, ZWNJ):
            i += 1; continue

        v = V_INDEP_DV.get(ch)
        if v is not None:
            append(v); i += 1; continue

        d = DIGITS_DV.get(ch)
        if d is not None:
            append(d); i += 1; continue

        if ch == AVAGRAHA_DV:
            append("'"); i += 1; continue

        if ch == CHANDRABINDU_DV:
            append('m̐'); i += 1; continue

        if ch == VISARGA_DV:
            append('ḥ'); i += 1; continue

        if ch == ANUSVARA_DV:
            j = _next_index_skip_marks(s, i + 1)
            if j != -1 and C_HAS(s[j]):
                append(_anusvara_homorganic(s[j]))
            else:
                append('ṃ')
            i += 1
            continue

        if C_HAS(ch):
            last = ch
            j = i + 1
            # possible nukta on base
            if j < n and s[j] == NUKTA_DV:
                j += 1  # mapping can be handled via C_BASE_DV if needed

            terminated = False

            while True:
                if j >= n or s[j] != VIRAMA_DV:
                    break
                j += 1
                if j < n and s[j] == ZWJ:
                    j += 1
                elif j < n and s[j] == ZWNJ:
                    append(C_BASE_DV[last])
                    i = j + 1
                    terminated = True
                    break
                if j < n and C_HAS(s[j]):
                    append(C_BASE_DV[last])
                    last = s[j]
                    j += 1
                    # greedily skip nukta after conjunct member
                    if j < n and s[j] == NUKTA_DV:
                        j += 1
                    continue
                append(C_BASE_DV[last])
                i = j
                terminated = True
                break

            if terminated:
                continue

            if j < n and s[j] == VIRAMA_DV:
                append(C_BASE_DV[last])
                i = j + 1
                continue

            if j < n and s[j] in V_SIGN_DV:
                append(PRECOMP_MATRA_DV[(last, s[j])])
                i = j + 1
                continue

            append(PRECOMP_INHERENT_DV[last])
            i = j
            continue

        append(ch); i += 1

    return ''.join(out)