# ==============================
# ===== Kannada core ===========
# ==============================

import re, unicodedata

KANNADA_BLOCK = r'\u0C80-\u0CFF'
kannada_span_re = re.compile(rf'([{KANNADA_BLOCK}]+)')
NON_KANNADA    = re.compile(rf'[^{KANNADA_BLOCK}]')

VIRAMA_KN = '್'
ANUSVARA_KN = 'ಂ'
CANDRA_KN   = 'ಁ'
VISARGA_KN  = 'ಃ'
ZWJ         = '\u200D'
ZWNJ        = '\u200C'

V_INDEP_KN = {
    'ಅ':'a','ಆ':'ā','ಇ':'i','ಈ':'ī','ಉ':'u','ಊ':'ū',
    'ಋ':'r̥','ೠ':'r̥̄','ಌ':'l̥','ೡ':'l̥̄',
    'ಎ':'e','ಏ':'ē','ಐ':'ai','ಒ':'o','ಓ':'ō','ಔ':'au'
}
V_SIGN_KN = {
    'ಾ':'ā','ಿ':'i','ೀ':'ī','ು':'u','ೂ':'ū',
    'ೃ':'r̥','ೄ':'r̥̄','ೆ':'e','ೇ':'ē','ೈ':'ai','ೊ':'o','ೋ':'ō','ೌ':'au',
    'ೢ':'l̥','ೣ':'l̥̄'
}

C_BASE_KN = {
    'ಕ':'k','ಖ':'kʰ','ಗ':'g','ಘ':'gʰ','ಙ':'ṅ',
    'ಚ':'c','ಛ':'cʰ','ಜ':'j','ಝ':'jʰ','ಞ':'ñ',
    'ಟ':'ṭ','ಠ':'ṭʰ','ಡ':'ḍ','ಢ':'ḍʰ','ಣ':'ṇ',
    'ತ':'t','ಥ':'tʰ','ದ':'d','ಧ':'dʰ','ನ':'n',
    'ಪ':'p','ಫ':'pʰ','ಬ':'b','ಭ':'bʰ','ಮ':'m',
    'ಯ':'y','ರ':'r','ಲ':'l','ವ':'v',
    'ಶ':'ś','ಷ':'ṣ','ಸ':'s','ಹ':'h',
    'ಳ':'ḷ','ೞ':'ḻ','ಱ':'ṟ',
}
DIGITS_KN = {'೦':'0','೧':'1','೨':'2','೩':'3','೪':'4','೫':'5','೬':'6','೭':'7','೮':'8','೯':'9'}

_ASSIM = {}
for c in 'ಕಖಗಘ': _ASSIM[c] = 'ṅ'
for c in 'ಚಛಜಝ': _ASSIM[c] = 'ñ'
for c in 'ಟಠಡಢ': _ASSIM[c] = 'ṇ'
for c in 'ತಥದಧ': _ASSIM[c] = 'n'
for c in 'ಪಫಬಭ': _ASSIM[c] = 'm'

def _anusvara_assim(next_char: str) -> str:
    return _ASSIM.get(next_char, 'ṁ')

def _next_base_idx(s: str, j: int) -> int:
    n = len(s)
    while j < n:
        ch = s[j]
        if ch in (ZWJ, ZWNJ):
            j += 1; continue
        if ch in C_BASE_KN or ch in V_INDEP_KN or ch in DIGITS_KN or ch in (VISARGA_KN, CANDRA_KN):
            return j
        j += 1
    return -1

PRECOMP_INHERENT_KN = {c: C_BASE_KN[c] + 'a' for c in C_BASE_KN}
PRECOMP_MATRA_KN    = {(c, m): C_BASE_KN[c] + V_SIGN_KN[m] for c in C_BASE_KN for m in V_SIGN_KN}

def transliterate_kannada_span_core(s: str, do_nfc: bool) -> str:
    s = unicodedata.normalize('NFC', s) if do_nfc else s

    out = []
    i = 0
    n = len(s)
    append = out.append

    while i < n:
        ch = s[i]

        if ch in (ZWJ, ZWNJ):
            i += 1; continue

        v = V_INDEP_KN.get(ch)
        if v is not None:
            append(v); i += 1; continue

        d = DIGITS_KN.get(ch)
        if d is not None:
            append(d); i += 1; continue

        if ch == CANDRA_KN:
            append('m̐'); i += 1; continue

        if ch == VISARGA_KN:
            append('ḥ'); i += 1; continue

        if ch == ANUSVARA_KN:
            j = _next_base_idx(s, i + 1)
            if j != -1 and s[j] in C_BASE_KN:
                append(_anusvara_assim(s[j]))
            else:
                append('ṁ')
            i += 1; continue

        if ch in C_BASE_KN:
            last = ch
            j = i + 1
            terminated = False

            while True:
                if j >= n or s[j] != VIRAMA_KN:
                    break
                j += 1
                if j < n and s[j] == ZWJ:
                    j += 1
                elif j < n and s[j] == ZWNJ:
                    append(C_BASE_KN[last])
                    i = j + 1
                    terminated = True
                    break
                if j < n and s[j] in C_BASE_KN:
                    append(C_BASE_KN[last])
                    last = s[j]
                    j += 1
                    continue
                append(C_BASE_KN[last])
                i = j
                terminated = True
                break

            if terminated:
                continue

            if j < n and s[j] == VIRAMA_KN:
                append(C_BASE_KN[last])
                i = j + 1
                continue

            if j < n and s[j] in V_SIGN_KN:
                append(PRECOMP_MATRA_KN[(last, s[j])])
                i = j + 1
                continue

            append(PRECOMP_INHERENT_KN[last])
            i = j
            continue

        append(ch); i += 1

    return ''.join(out)