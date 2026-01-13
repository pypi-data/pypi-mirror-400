from pathlib import Path


def read_reverse_order(
    path: Path | str,
    chunk_size: int = 4096,
    max_lines: int | None = None,
    encoding: str = "utf-8",
    errors: str = "replace",
):
    """
    Yield lines from `path` in reverse order, one at a time.
    - Reads in `chunk_size`-byte blocks from the end for efficiency.
    - Stops after `max_lines` if specified.
    - Decodes using `encoding`, `errors` policy.
    """
    path = Path(path)
    file_size = path.stat().st_size
    buffer = ""
    lines_yielded = 0

    with path.open("rb") as f:
        pos = file_size
        while pos > 0:
            read_size = min(chunk_size, pos)
            pos -= read_size
            f.seek(pos)
            data = f.read(read_size).decode(encoding, errors=errors)
            buffer = data + buffer
            parts = buffer.split("\n")
            buffer = parts.pop(0)  # leftover start of first line
            for line in reversed(parts):
                yield line
                lines_yielded += 1
                if max_lines and lines_yielded >= max_lines:
                    return
        # finally yield the remaining buffer if non-empty
        if buffer:
            yield buffer
