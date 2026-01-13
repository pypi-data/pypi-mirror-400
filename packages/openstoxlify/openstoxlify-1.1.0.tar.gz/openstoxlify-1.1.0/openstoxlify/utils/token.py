from typing import List


def fetch_token(agrv: List[str]) -> str | None:
    if len(agrv) < 2:
        return None
    return agrv[1]
