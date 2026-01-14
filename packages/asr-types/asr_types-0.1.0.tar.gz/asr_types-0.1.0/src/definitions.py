from typing import List, TypedDict


class ASRWord(TypedDict):
    word: str
    start_ms: int
    end_ms: int


class ASRSegment(TypedDict):
    text: str
    start_ms: int
    end_ms: int
    words: List[ASRWord]
