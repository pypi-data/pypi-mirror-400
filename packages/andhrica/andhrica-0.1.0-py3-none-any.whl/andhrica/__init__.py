# andhrica/__init__.py
"""Andhrica — Indic script transliteration."""

import os
import time
import unicodedata
from dataclasses import dataclass
from typing import Callable, Iterable, Union
from collections import OrderedDict

# Per-script cores
from .telugu import telugu_span_re, transliterate_telugu_span_core, NON_TELUGU
from .malayalam import malayalam_span_re, transliterate_malayalam_span_core, NON_MALAYALAM
from .tamil import tamil_span_re, transliterate_tamil_span_core, NON_TAMIL
from .kannada import kannada_span_re, transliterate_kannada_span_core, NON_KANNADA
from .odia import odia_span_re, transliterate_odia_span_core, NON_ODIA
from .devanagari_hindi import (
    dev_span_re as dev_span_re_hi, NON_DEV as NON_DEV_HI,
    transliterate_devanagari_hindi_span_core,
    transliterate_devanagari_hindi_span_core_advanced,
)
from .devanagari_sanskrit import (
    dev_span_re as dev_span_re_sa, NON_DEV as NON_DEV_SA,
    transliterate_devanagari_sanskrit_span_core,
)
from .gondi import gunjala_span_re, NON_GUNJALA_GONDI, transliterate_gunjala_gondi_span_core

__all__ = ["transliterate", "transliterate_file", "Stats"]

# ============================================
# Stats
# ============================================

@dataclass
class Stats:
    bytes_processed: int
    seconds: float
    cache_hits: int
    cache_misses: int
    
    @property
    def throughput_mbps(self) -> float:
        return (self.bytes_processed / 1e6) / max(self.seconds, 1e-9)
    
    @property
    def cache_hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / max(total, 1)

# ============================================
# LRU Cache (internal)
# ============================================

class _LRUCache:
    __slots__ = ("_d", "_cap")
    
    def __init__(self, capacity: int = 200_000):
        self._d: OrderedDict[str, str] = OrderedDict()
        self._cap = capacity
    
    def get(self, k: str):
        return self._d.get(k)
    
    def set(self, k: str, v: str) -> None:
        d = self._d
        if k in d:
            d[k] = v
        else:
            d[k] = v
            if len(d) > self._cap:
                d.popitem(last=False)
    
    def __len__(self) -> int:
        return len(self._d)

# ============================================
# Language registry
# ============================================

_LANGS = {
    "te": (telugu_span_re, transliterate_telugu_span_core, NON_TELUGU),
    "telugu": (telugu_span_re, transliterate_telugu_span_core, NON_TELUGU),
    "ml": (malayalam_span_re, transliterate_malayalam_span_core, NON_MALAYALAM),
    "malayalam": (malayalam_span_re, transliterate_malayalam_span_core, NON_MALAYALAM),
    "ta": (tamil_span_re, transliterate_tamil_span_core, NON_TAMIL),
    "tamil": (tamil_span_re, transliterate_tamil_span_core, NON_TAMIL),
    "kn": (kannada_span_re, transliterate_kannada_span_core, NON_KANNADA),
    "kannada": (kannada_span_re, transliterate_kannada_span_core, NON_KANNADA),
    "or": (odia_span_re, transliterate_odia_span_core, NON_ODIA),
    "odia": (odia_span_re, transliterate_odia_span_core, NON_ODIA),
    "hi": (dev_span_re_hi, transliterate_devanagari_hindi_span_core, NON_DEV_HI),
    "hindi": (dev_span_re_hi, transliterate_devanagari_hindi_span_core, NON_DEV_HI),
    "hi+": (dev_span_re_hi, transliterate_devanagari_hindi_span_core_advanced, NON_DEV_HI),
    "sa": (dev_span_re_sa, transliterate_devanagari_sanskrit_span_core, NON_DEV_SA),
    "sanskrit": (dev_span_re_sa, transliterate_devanagari_sanskrit_span_core, NON_DEV_SA),
    "gon": (gunjala_span_re, transliterate_gunjala_gondi_span_core, NON_GUNJALA_GONDI),
    "gondi": (gunjala_span_re, transliterate_gunjala_gondi_span_core, NON_GUNJALA_GONDI),
}

def _get_lang(lang: str):
    key = lang.strip().lower()
    if key not in _LANGS:
        raise ValueError(f"Unsupported language: {lang!r}. Options: te, ml, ta, kn, or, hi, hi+, sa, gon")
    return _LANGS[key]

# ============================================
# Core transliteration
# ============================================

def _transliterate_text(text: str, span_re, core_fn, cache: _LRUCache) -> str:
    """Transliterate a single string using cache."""
    pieces = []
    pos = 0
    
    for m in span_re.finditer(text):
        s, e = m.span()
        if s > pos:
            pieces.append(text[pos:s])
        
        span = unicodedata.normalize("NFC", m.group(1))
        cached = cache.get(span)
        
        if cached is None:
            out = core_fn(span, False)
            cache.set(span, out)
        else:
            out = cached
        
        pieces.append(out)
        pos = e
    
    if pos < len(text):
        pieces.append(text[pos:])
    
    return "".join(pieces)

# ============================================
# Public API
# ============================================

def transliterate(lang: str, text: Union[str, Iterable[str]]) -> Union[str, list]:
    """
    Transliterate text to ISO 15919 romanization.
    
    Args:
        lang: Language code (te, ml, ta, kn, or, hi, hi+, sa, gon)
        text: String or iterable of strings
    
    Returns:
        Transliterated string or list of strings
    """
    span_re, core_fn, _ = _get_lang(lang)
    cache = _LRUCache()
    
    if isinstance(text, str):
        return _transliterate_text(text, span_re, core_fn, cache)
    
    return [_transliterate_text(s, span_re, core_fn, cache) for s in text]


def transliterate_file(
    lang: str,
    in_path: str,
    out_path: str,
    *,
    on_progress: Callable | None = None,
    chunk_size: int = 64 * 1024 * 1024,
) -> Stats:
    """
    Stream-transliterate a file.
    
    Args:
        lang: Language code
        in_path: Input file path
        out_path: Output file path
        on_progress: Optional callback(ProgressInfo) for progress updates
        chunk_size: Read chunk size in bytes (default 64MB)
    
    Returns:
        Stats with processing details
    """
    from .progress import ProgressInfo  # late import to avoid circular
    
    span_re, core_fn, non_re = _get_lang(lang)
    cache = _LRUCache()
    hits = misses = 0
    
    total_bytes = os.path.getsize(in_path)
    bytes_done = 0
    t0 = time.time()
    
    with open(in_path, "r", encoding="utf-8") as fin, \
         open(out_path, "w", encoding="utf-8") as fout:
        
        while True:
            chunk = fin.read(chunk_size)
            if not chunk:
                break
            
            # Transliterate with hit/miss counting
            pieces = []
            pos = 0
            
            for m in span_re.finditer(chunk):
                s, e = m.span()
                if s > pos:
                    pieces.append(chunk[pos:s])
                
                span = unicodedata.normalize("NFC", m.group(1))
                cached = cache.get(span)
                
                if cached is None:
                    out = core_fn(span, False)
                    cache.set(span, out)
                    misses += 1
                else:
                    out = cached
                    hits += 1
                
                pieces.append(out)
                pos = e
            
            if pos < len(chunk):
                pieces.append(chunk[pos:])
            
            fout.write("".join(pieces))
            bytes_done += len(chunk.encode("utf-8"))
            
            if on_progress:
                on_progress(ProgressInfo(
                    bytes_done=bytes_done,
                    bytes_total=total_bytes,
                    elapsed=time.time() - t0,
                    cache_hits=hits,
                    cache_misses=misses,
                ))
    
    elapsed = time.time() - t0
    
    # Final progress call
    if on_progress:
        on_progress(ProgressInfo(
            bytes_done=total_bytes,
            bytes_total=total_bytes,
            elapsed=elapsed,
            cache_hits=hits,
            cache_misses=misses,
        ))
    
    return Stats(
        bytes_processed=total_bytes,
        seconds=elapsed,
        cache_hits=hits,
        cache_misses=misses,
    )