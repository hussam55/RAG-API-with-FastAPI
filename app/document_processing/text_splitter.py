def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    words = text.split()
    step = max(chunk_size - overlap, 1)
    return [
        " ".join(words[start : start + chunk_size])
        for start in range(0, len(words), step)
        if words[start : start + chunk_size]
    ]
