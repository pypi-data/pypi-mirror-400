# andhrica/progress.py
"""Progress display utilities for Andhrica."""

import sys
import time
from dataclasses import dataclass
from typing import Callable, TextIO

@dataclass
class ProgressInfo:
    """Progress state passed to callbacks."""
    bytes_done: int
    bytes_total: int
    elapsed: float
    cache_hits: int
    cache_misses: int
    
    @property
    def pct(self) -> float:
        return (self.bytes_done / max(self.bytes_total, 1)) * 100
    
    @property
    def mbps(self) -> float:
        return (self.bytes_done / 1e6) / max(self.elapsed, 1e-9)
    
    @property
    def hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / max(total, 1)


def progress_bar(
    width: int = 40,
    file: TextIO = sys.stderr,
    update_interval: float = 0.1,
) -> Callable[[ProgressInfo], None]:
    """
    Returns a callback that displays a progress bar.
    
    Example:
        transliterate_file("te", "in.txt", "out.txt", on_progress=progress_bar())
    
    Output:
        [████████████░░░░░░░░░░░░░░░░]  42.3% │ 128.5 MB/s │ hit 94.2%
    """
    last_update = [0.0]  # mutable container for closure
    
    def callback(info: ProgressInfo) -> None:
        now = time.time()
        if now - last_update[0] < update_interval and info.pct < 100:
            return
        last_update[0] = now
        
        # Build bar
        filled = int(width * info.pct / 100)
        bar = '█' * filled + '░' * (width - filled)
        
        # Format line
        line = (
            f"\r[{bar}] {info.pct:5.1f}% │ "
            f"{info.mbps:6.1f} MB/s │ "
            f"hit {info.hit_rate * 100:4.1f}%"
        )
        
        file.write(line)
        file.flush()
        
        if info.pct >= 100:
            file.write('\n')
    
    return callback


def progress_log(
    file: TextIO = sys.stderr,
    every_bytes: int = 1 << 30,  # 1 GiB
) -> Callable[[ProgressInfo], None]:
    """
    Returns a callback that prints periodic log lines.
    
    Output:
        [1 GiB]  12.5% │  45.2s │ 128.5 MB/s │ hits 1,234,567 / misses 12,345
    """
    next_report = [every_bytes]
    
    def callback(info: ProgressInfo) -> None:
        if info.bytes_done < next_report[0] and info.pct < 100:
            return
        
        gib_done = info.bytes_done / (1 << 30)
        
        line = (
            f"[{gib_done:.0f} GiB] {info.pct:5.1f}% │ "
            f"{info.elapsed:6.1f}s │ {info.mbps:6.1f} MB/s │ "
            f"hits {info.cache_hits:,} / misses {info.cache_misses:,}"
        )
        print(line, file=file)
        
        while next_report[0] <= info.bytes_done:
            next_report[0] += every_bytes
    
    return callback


def progress_silent() -> Callable[[ProgressInfo], None]:
    """No-op callback for benchmarking without display overhead."""
    def callback(info: ProgressInfo) -> None:
        pass
    return callback


def print_stats(stats, file: TextIO = sys.stderr) -> None:
    """Print final stats summary."""
    print(f"\n{'─' * 50}", file=file)
    print(f"  Bytes:      {stats.bytes_processed:,}", file=file)
    print(f"  Time:       {stats.seconds:.2f}s", file=file)
    print(f"  Throughput: {stats.throughput_mbps:.1f} MB/s", file=file)
    print(f"  Cache hit:  {stats.cache_hit_rate * 100:.1f}%", file=file)
    print(f"{'─' * 50}", file=file)