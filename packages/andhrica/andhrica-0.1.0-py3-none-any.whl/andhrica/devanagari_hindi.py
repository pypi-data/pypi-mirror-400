# ==============================
# ===== Devanagari (Hindi) =====
# ==============================

import re, unicodedata

DEV_BLOCK       = r'\u0900-\u097F'
dev_span_re     = re.compile(rf'([{DEV_BLOCK}]+)')
NON_DEV         = re.compile(rf'[^{DEV_BLOCK}]')

# Signs & specials
VIRAMA_DV       = '्'
ANUSVARA_DV     = 'ं'
CHANDRABINDU_DV = 'ँ'
VISARGA_DV      = 'ः'
AVAGRAHA_DV     = 'ऽ'
NUKTA_DV        = '़'
ZWJ             = '\u200D'
ZWNJ            = '\u200C'

# Independent vowels (ISO 15919)
V_INDEP_DV = {
    'अ':'a','आ':'ā','इ':'i','ई':'ī','उ':'u','ऊ':'ū',
    'ऋ':'r̥','ॠ':'r̥̄','ऌ':'l̥','ॡ':'l̥̄',
    'ए':'e','ऐ':'ai','ओ':'o','औ':'au',
}

# Dependent vowel signs
V_SIGN_DV = {
    'ा':'ā','ि':'i','ी':'ī','ु':'u','ू':'ū',
    'ृ':'r̥','ॄ':'r̥̄','ॢ':'l̥','ॣ':'l̥̄',
    'े':'e','ै':'ai','ो':'o','ौ':'au',
}

# Consonants (incl. nukta precomposed forms)
C_BASE_DV = {
    'क':'k','ख':'kʰ','ग':'g','घ':'gʰ','ङ':'ṅ',
    'च':'c','छ':'cʰ','ज':'j','झ':'jʰ','ञ':'ñ',
    'ट':'ṭ','ठ':'ṭʰ','ड':'ḍ','ढ':'ḍʰ','ण':'ṇ',
    'त':'t','थ':'tʰ','द':'d','ध':'dʰ','न':'n',
    'प':'p','फ':'pʰ','ब':'b','भ':'bʰ','म':'m',
    'य':'y','र':'r','ल':'l','व':'v',
    'श':'ś','ष':'ṣ','स':'s','ह':'h',
    # Nukta letters (common Hindi set)
    'क़':'q','ख़':'x','ग़':'ġ','ज़':'z','फ़':'f',
    'ड़':'ṛ','ढ़':'ṛh','ऩ':'ṉ','ऱ':'ṟ','ऴ':'ḻ',
}

DIGITS_DV = {'०':'0','१':'1','२':'2','३':'3','४':'4','५':'5','६':'6','७':'7','८':'8','९':'9'}

# Anusvara assimilation (homorganic, Hindi)
_ASSIM = {}
for c in 'कखगघक़ख़ग़': _ASSIM[c] = 'ṅ'   # velars
for c in 'चछजझ':     _ASSIM[c] = 'ñ'   # palatals
for c in 'टठडढढ़ड़':    _ASSIM[c] = 'ṇ'   # retroflex
for c in 'तथदध':     _ASSIM[c] = 'n'   # dentals
for c in 'पफबभफ़':    _ASSIM[c] = 'm'   # labials

SONORANTS = set('यरलवऱ')

def _anusvara_homorganic(next_char: str) -> str:
    return _ASSIM.get(next_char, 'n')

# Greedy nukta precompose
NUKTA_PRECOMP_DV = {
    'क':'क़', 'ख':'ख़', 'ग':'ग़', 'ज':'ज़', 'फ':'फ़',
    'ड':'ड़', 'ढ':'ढ़', 'र':'ऱ',
}

def _apply_nukta(ch: str) -> str:
    return NUKTA_PRECOMP_DV.get(ch, ch)

def _next_index_skip_marks(s: str, j: int) -> int:
    n = len(s)
    while j < n:
        ch = s[j]
        if ch in (ZWJ, ZWNJ, NUKTA_DV):
            j += 1; continue
        v = V_INDEP_DV.get(ch)
        d = DIGITS_DV.get(ch)
        if ch in C_BASE_DV or v is not None or d is not None or ch in (VISARGA_DV, CHANDRABINDU_DV):
            return j
        j += 1
    return -1

# Precompute compose tables
PRECOMP_INHERENT_DV = {c: C_BASE_DV[c] + 'a' for c in C_BASE_DV}
PRECOMP_MATRA_DV    = {(c, m): C_BASE_DV[c] + V_SIGN_DV[m] for c in C_BASE_DV for m in V_SIGN_DV}

# --- Common core (no schwa pass) ---
def _core_without_schwa(s: str, do_nfc: bool):
    """
    Build token stream with per-token metadata so deletions can be done safely.

    Returns:
      out_tokens: list[str]
      kinds:      list[str]  # 'N' = normal, 'I' = inherent 'a', 'P' = protected first inherent 'a'
      medial_mask:list[bool] # True where that index hosts an inherent 'a' eligible for medial deletion
    """
    s = unicodedata.normalize('NFC', s) if do_nfc else s

    out: list[str] = []
    kinds: list[str] = []       # aligned with out
    medial_mask: list[bool] = []# aligned with out

    i = 0
    n = len(s)
    C_HAS = C_BASE_DV.__contains__

    first_inherent_marked = False

    def append(tok: str, kind: str = 'N', medial: bool = False):
        out.append(tok); kinds.append(kind); medial_mask.append(medial)

    while i < n:
        ch = s[i]

        if ch in (ZWJ, ZWNJ):
            i += 1; continue

        v = V_INDEP_DV.get(ch)
        if v is not None:
            append(v)  # vowels are standalone; no inherent slot
            i += 1; continue

        d = DIGITS_DV.get(ch)
        if d is not None:
            append(d)
            i += 1; continue

        if ch == AVAGRAHA_DV:
            append("'")
            i += 1; continue

        if ch == CHANDRABINDU_DV:
            append('m̐')
            i += 1; continue

        if ch == VISARGA_DV:
            append('ḥ')
            i += 1; continue

        if ch == ANUSVARA_DV:
            j = _next_index_skip_marks(s, i + 1)
            if j != -1:
                look = s[j]
                if j + 1 < n and s[j+1] == NUKTA_DV:
                    look = _apply_nukta(look)
                if look in SONORANTS:
                    append('m̐')
                elif C_HAS(look):
                    append(_anusvara_homorganic(look))
                else:
                    append('m̐')
            else:
                append('m̐')
            i += 1
            continue

        if C_HAS(ch):
            j = i + 1
            base = ch
            if j < n and s[j] == NUKTA_DV:
                base = _apply_nukta(base)
                j += 1

            last = base
            terminated = False

            # Conjunct chain C + virama [+ ZWJ/ZWNJ] + C ...
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
                    append(C_BASE_DV[last])  # bare in stack
                    nxt = s[j]
                    j += 1
                    if j < n and s[j] == NUKTA_DV:
                        nxt = _apply_nukta(nxt)
                        j += 1
                    last = nxt
                    continue
                append(C_BASE_DV[last])      # explicit halant end
                i = j
                terminated = True
                break

            if terminated:
                continue

            # Explicit virama with nothing after
            if j < n and s[j] == VIRAMA_DV:
                append(C_BASE_DV[last])
                i = j + 1
                continue

            # Matra?
            if j < n:
                mat = V_SIGN_DV.get(s[j])
                if mat is not None:
                    append(PRECOMP_MATRA_DV[(last, s[j])])
                    i = j + 1
                    continue

            # Otherwise, inherent 'a'
            append(C_BASE_DV[last])  # the consonant
            # mark the following 'a' token as inherent; protect the first one only
            medial_candidate = False
            # Check immediate next akshara pattern: if next is C(+nukta)+matra, this 'a' may delete
            k = j
            if k < n and C_HAS(s[k]):
                k2 = k + 1
                if k2 < n and s[k2] == NUKTA_DV:
                    k2 += 1
                if k2 < n and s[k2] in V_SIGN_DV:
                    medial_candidate = True

            if not first_inherent_marked:
                append('a', kind='P', medial=medial_candidate)  # protected first-akshara 'a'
                first_inherent_marked = True
            else:
                append('a', kind='I', medial=medial_candidate)

            i = j
            continue

        # Fallback passthrough
        append(ch); i += 1

    return out, kinds, medial_mask

def _apply_hindi_schwa_simple(out_tokens: list[str], kinds: list[str], medial_mask: list[bool]) -> str:
    """
    - Delete one rightmost medial inherent 'a' eligible by mask.
    - Delete final inherent 'a' (even if it is the only inherent 'a').
    - Never delete the protected first-akshara 'a' unless it's the ONLY inherent and final.
    """
    assert len(out_tokens) == len(kinds) == len(medial_mask)

    # Rightmost eligible medial deletion
    for i in range(len(out_tokens) - 1, -1, -1):
        if kinds[i] == 'I' and medial_mask[i] and out_tokens[i] == 'a':
            del out_tokens[i]; del kinds[i]; del medial_mask[i]
            break

    # Count inherent 'a'
    inherent_idxs = [i for i,k in enumerate(kinds) if k in ('I','P') and out_tokens[i] == 'a']

    # Final deletion
    if out_tokens and out_tokens[-1] == 'a' and kinds[-1] in ('I','P'):
        if len(inherent_idxs) == 1:
            # only inherent is final (could be protected) -> delete
            out_tokens.pop(); kinds.pop(); medial_mask.pop()
        else:
            # multiple inherent a's: delete if not protected
            if kinds[-1] != 'P':
                out_tokens.pop(); kinds.pop(); medial_mask.pop()

    return ''.join(out_tokens)

def _apply_hindi_schwa_advanced(out_tokens: list[str], kinds: list[str], medial_mask: list[bool]) -> str:
    """
    - Delete ALL medial eligible inherent 'a' (mask=True), except the protected first akshara.
    - Then delete final inherent 'a' (even if it's the only inherent).
    """
    assert len(out_tokens) == len(kinds) == len(medial_mask)

    # Delete all eligible medial (scan right-to-left to keep indices valid)
    i = len(out_tokens) - 1
    while i >= 0:
        if kinds[i] == 'I' and medial_mask[i] and out_tokens[i] == 'a':
            del out_tokens[i]; del kinds[i]; del medial_mask[i]
        i -= 1

    # Count inherent 'a' after medial deletions
    inherent_idxs = [i for i,k in enumerate(kinds) if k in ('I','P') and out_tokens[i] == 'a']

    # Final deletion
    if out_tokens and out_tokens[-1] == 'a' and kinds[-1] in ('I','P'):
        if len(inherent_idxs) == 1:
            out_tokens.pop(); kinds.pop(); medial_mask.pop()
        else:
            if kinds[-1] != 'P':
                out_tokens.pop(); kinds.pop(); medial_mask.pop()

    return ''.join(out_tokens)


# Public cores

def transliterate_devanagari_hindi_span_core(s: str, do_nfc: bool) -> str:
    out, kinds, medial = _core_without_schwa(s, do_nfc)
    return _apply_hindi_schwa_simple(out, kinds, medial)

def transliterate_devanagari_hindi_span_core_advanced(s: str, do_nfc: bool) -> str:
    out, kinds, medial = _core_without_schwa(s, do_nfc)
    return _apply_hindi_schwa_advanced(out, kinds, medial)