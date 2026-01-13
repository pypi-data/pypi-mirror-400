# Andhrica

Fast ISO 15919 transliteration for Indic scripts.

## Supported Scripts

| Code | Script |
|------|--------|
| `te` | Telugu |
| `ta` | Tamil |
| `ml` | Malayalam |
| `kn` | Kannada |
| `or` | Odia |
| `hi` | Hindi (with schwa deletion) |
| `hi+` | Hindi (aggressive schwa deletion) |
| `sa` | Sanskrit (no schwa deletion) |
| `gon` | Gunjala Gondi |

## Installation

```bash
pip install andhrica
```

Or install from source:

```bash
git clone https://github.com/neet2407/andhrica.git
cd andhrica
pip install -e .
```

## Usage

```python
from andhrica import transliterate

# Single string
transliterate("te", "తెలుగు")
# → 'telugu'

# Multiple strings
transliterate("ta", ["தமிழ்", "நன்றி"])
# → ['tamiḻ', 'naṉṟi']
```

### File Processing

For large files with progress tracking:

```python
from andhrica import transliterate_file
from andhrica.progress import progress_bar, print_stats

stats = transliterate_file(
    "te",
    "input.txt",
    "output.txt",
    on_progress=progress_bar()
)
print_stats(stats)
```

Output:
```
[████████████████████████████████████████] 100.0% │  45.2 MB/s │ hit 94.1%
──────────────────────────────────────────────────
  Bytes:      1,234,567,890
  Time:       27.32s
  Throughput: 45.2 MB/s
  Cache hit:  94.1%
──────────────────────────────────────────────────
```

## Output Format

Uses [ISO 15919](https://en.wikipedia.org/wiki/ISO_15919) romanization with standard diacritics:

| Type | Characters |
|------|------------|
| Long vowels | `ā ī ū` |
| Retroflex | `ṭ ḍ ṇ ḷ` |
| Sibilants | `ś ṣ` |
| Nasals | `ṅ ñ ṁ` |
| Aspirates | `kʰ gʰ cʰ jʰ ṭʰ ḍʰ tʰ dʰ pʰ bʰ` |
| Vocalic R/L | `r̥ r̥̄ l̥ l̥̄` |

## Examples

| Script | Input | Output |
|--------|-------|--------|
| Telugu | తెలుగు | telugu |
| Tamil | தமிழ் | tamiḻ |
| Malayalam | മലയാളം | malayāḷaṁ |
| Kannada | ಕನ್ನಡ | kannaḍa |
| Hindi | हिन्दी | hindī |
| Sanskrit | संस्कृतम् | saṃskr̥tam |

## API Reference

### `transliterate(lang, text)`

Transliterate text to ISO 15919 romanization.

**Parameters:**
- `lang` (str): Language code (`te`, `ta`, `ml`, `kn`, `or`, `hi`, `hi+`, `sa`, `gon`)
- `text` (str | list): String or list of strings to transliterate

**Returns:** Transliterated string or list of strings

### `transliterate_file(lang, in_path, out_path, on_progress=None)`

Stream-transliterate a file with optional progress callback.

**Parameters:**
- `lang` (str): Language code
- `in_path` (str): Input file path
- `out_path` (str): Output file path
- `on_progress` (callable, optional): Progress callback function

**Returns:** `Stats` object with processing details

## License

MIT

## Author

[neet2407](https://github.com/neet2407)
