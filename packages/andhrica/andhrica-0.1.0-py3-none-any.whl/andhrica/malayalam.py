# ============================================
# ===== Malayalam core =======================
# ============================================

import re, unicodedata

MALAYALAM_BLOCK   = r'\u0D00-\u0D7F'
malayalam_span_re = re.compile(rf'([{MALAYALAM_BLOCK}]+)')
NON_MALAYALAM     = re.compile(rf'[^{MALAYALAM_BLOCK}]')

VIRAMAM_ML  = '്'
ANUSVARA_ML = 'ം'
VISARGA_ML  = 'ഃ'
CANDRA_ML   = 'ഁ'
ZWJ         = '\u200D'
ZWNJ        = '\u200C'

# Independent vowels (ISO 15919)
V_INDEP_ML = {
    'അ':'a','ആ':'ā','ഇ':'i','ഈ':'ī','ഉ':'u','ഊ':'ū',
    'ഋ':'r̥','ൠ':'r̥̄','ഌ':'l̥','ൡ':'l̥̄',
    'എ':'e','ഏ':'ē','ഐ':'ai','ഒ':'o','ഓ':'ō','ഔ':'au',
}

# Dependent vowel signs (matras)
V_SIGN_ML = {
    'ാ':'ā','ി':'i','ീ':'ī','ു':'u','ൂ':'ū',
    'ൃ':'r̥','ൄ':'r̥̄','െ':'e','േ':'ē','ൈ':'ai','ൊ':'o','ോ':'ō','ൌ':'au',
    'ൢ':'l̥','ൣ':'l̥̄'
}

C_BASE_ML = {
    'ക':'k','ഖ':'kʰ','ഗ':'g','ഘ':'gʰ','ങ':'ṅ',
    'ച':'c','ഛ':'cʰ','ജ':'j','ഝ':'jʰ','ഞ':'ñ',
    'ട':'ṭ','ഠ':'ṭʰ','ഡ':'ḍ','ഢ':'ḍʰ','ണ':'ṇ',
    'ത':'t','ഥ':'tʰ','ദ':'d','ധ':'dʰ','ന':'n',
    'പ':'p','ഫ':'pʰ','ബ':'b','ഭ':'bʰ','മ':'m',
    'യ':'y','ര':'r','ല':'l','വ':'v',
    'ശ':'ś','ഷ':'ṣ','സ':'s','ഹ':'h',
    'ള':'ḷ','ഴ':'ḻ','റ':'ṟ', 'ഺ':'ṯ'
}

DIGITS_ML = {'൦':'0','൧':'1','൨':'2','൩':'3','൪':'4','൫':'5','൬':'6','൭':'7','൮':'8','൯':'9',
             '൰':'10', '൱': '100', '൲': '1000'}

# Atomic chillus
CHILLU_MAP = {
    'ൺ': 'ṇ','ൻ': 'n','ർ': 'r','ൽ': 'l','ൾ': 'ḷ','ൿ': 'k',
    'ൔ': 'm','ൕ': 'y','ൖ': 'ḻ'
}
CHILLU_GET = CHILLU_MAP.get

PRECOMP_INHERENT_ML = {c: C_BASE_ML[c] + 'a' for c in C_BASE_ML}
PRECOMP_MATRA_ML    = {(c, m): C_BASE_ML[c] + V_SIGN_ML[m] for c in C_BASE_ML for m in V_SIGN_ML}

def transliterate_malayalam_span_core(s: str, do_nfc: bool) -> str:
    s = unicodedata.normalize('NFC', s) if do_nfc else s

    out = []
    i = 0
    n = len(s)
    append = out.append
    V_INDEP_get = V_INDEP_ML.get
    V_SIGN_get  = V_SIGN_ML.get
    DIGITS_get  = DIGITS_ML.get
    C_BASE_has  = C_BASE_ML.__contains__

    while i < n:
        ch = s[i]

        if ch in (ZWJ, ZWNJ):
            i += 1; continue

        cv = CHILLU_GET(ch)
        if cv is not None:
            append(cv); i += 1; continue

        v = V_INDEP_get(ch)
        if v is not None:
            append(v); i += 1; continue

        d = DIGITS_get(ch)
        if d is not None:
            append(d); i += 1; continue

        if ch == VISARGA_ML:
            append('ḥ'); i += 1; continue

        if ch == CANDRA_ML:
            append('m̐'); i += 1; continue

        if ch == ANUSVARA_ML:
            append('ṁ'); i += 1; continue  # no assimilation in Malayalam

        if C_BASE_has(ch):
            last = ch
            j = i + 1

            # Conjunct chain
            while j + 1 < n and s[j] == VIRAMAM_ML and C_BASE_has(s[j+1]):
                append(C_BASE_ML[last])  # bare consonant
                last = s[j+1]
                j += 2

            # Legacy chillu C + virama + ZWJ
            if j < n and s[j] == VIRAMAM_ML and j + 1 < n and s[j+1] == ZWJ:
                append(C_BASE_ML[last])
                i = j + 2
                continue

            # Explicit virama
            if j < n and s[j] == VIRAMAM_ML:
                append(C_BASE_ML[last])
                i = j + 1
                continue

            # Matra?
            if j < n:
                mat = V_SIGN_get(s[j])
                if mat is not None:
                    append(PRECOMP_MATRA_ML[(last, s[j])])
                    i = j + 1
                    continue

            append(PRECOMP_INHERENT_ML[last])
            i = j
            continue

        append(ch); i += 1

    return ''.join(out)