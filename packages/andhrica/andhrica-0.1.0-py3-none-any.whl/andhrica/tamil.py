# ==============================
# ===== Tamil core =============
# ==============================

import re, unicodedata

TAMIL_BLOCK = r'\u0B80-\u0BFF'
tamil_span_re = re.compile(rf'([{TAMIL_BLOCK}]+)')
NON_TAMIL    = re.compile(rf'[^{TAMIL_BLOCK}]')

VIRAMA_TA = '்'    # pulli
AYTHAM   = 'ஃ'
ZWJ      = '\u200D'
ZWNJ     = '\u200C'

V_INDEP_TA = {
    'அ':'a','ஆ':'ā','இ':'i','ஈ':'ī','உ':'u','ஊ':'ū',
    'எ':'e','ஏ':'ē','ஐ':'ai','ஒ':'o','ஓ':'ō','ஔ':'au',
}

V_SIGN_TA = {
    'ா':'ā','ி':'i','ீ':'ī','ு':'u','ூ':'ū',
    'ெ':'e','ே':'ē','ை':'ai','ொ':'o','ோ':'ō','ௌ':'au',
}

# Include Grantha letters where present in modern Tamil blocks
C_BASE_TA = {
    'க':'k','ங':'ṅ',
    'ச':'c','ஞ':'ñ',
    'ட':'ṭ','ண':'ṇ',
    'த':'t','ந':'n',
    'ப':'p','ம':'m',
    'ய':'y','ர':'r','ல':'l','வ':'v',
    'ழ':'ḻ','ள':'ḷ','ற':'ṟ','ன':'ṉ',
    # Grantha (pulli handling same)
    'ஜ':'j','ஷ':'ṣ','ஸ':'s','ஹ':'h','ஶ':'ś','க்ஷ':'kṣ',  # 'க்ஷ' handled via conjunct too
}

DIGITS_TA = {'௦':'0','௧':'1','௨':'2','௩':'3','௪':'4','௫':'5','௬':'6','௭':'7','௮':'8','௯':'9'}

PRECOMP_INHERENT_TA = {c: C_BASE_TA[c] + 'a' for c in C_BASE_TA}
PRECOMP_MATRA_TA    = {(c, m): C_BASE_TA[c] + V_SIGN_TA[m] for c in C_BASE_TA for m in V_SIGN_TA}

def transliterate_tamil_span_core(s: str, do_nfc: bool) -> str:
    s = unicodedata.normalize('NFC', s) if do_nfc else s

    out = []
    i = 0
    n = len(s)
    append = out.append
    V_INDEP_get = V_INDEP_TA.get
    V_SIGN_get  = V_SIGN_TA.get
    C_BASE_has  = C_BASE_TA.__contains__
    DIGITS_get  = DIGITS_TA.get

    while i < n:
        ch = s[i]

        if ch in (ZWJ, ZWNJ):
            i += 1; continue

        v = V_INDEP_get(ch)
        if v is not None:
            append(v); i += 1; continue

        d = DIGITS_get(ch)
        if d is not None:
            append(d); i += 1; continue

        if ch == AYTHAM:
            append('ḵ')  # aytham (visarga-like)
            i += 1; continue

        if C_BASE_has(ch):
            last = ch
            j = i + 1
            terminated = False

            while True:
                if j >= n or s[j] != VIRAMA_TA:
                    break
                j += 1
                if j < n and s[j] == ZWJ:
                    j += 1
                elif j < n and s[j] == ZWNJ:
                    append(C_BASE_TA[last])
                    i = j + 1
                    terminated = True
                    break
                if j < n and C_BASE_has(s[j]):
                    append(C_BASE_TA[last])  # bare
                    last = s[j]
                    j += 1
                    continue
                append(C_BASE_TA[last])  # explicit pulli end
                i = j
                terminated = True
                break

            if terminated:
                continue

            if j < n and s[j] == VIRAMA_TA:
                append(C_BASE_TA[last])
                i = j + 1
                continue

            if j < n:
                mat = V_SIGN_get(s[j])
                if mat is not None:
                    append(PRECOMP_MATRA_TA[(last, s[j])])
                    i = j + 1
                    continue

            append(PRECOMP_INHERENT_TA[last])
            i = j
            continue

        append(ch); i += 1

    return ''.join(out)