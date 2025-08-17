from typing import List, Tuple

def simple_search(query: str, cases: List[dict]) -> List[Tuple[int, dict]]:
    """Простой поиск по совпадениям слов."""
    query_words = set(query.lower().split())
    results = []
    for idx, case in enumerate(cases):
        text_words = set(case['text'].lower().split())
        common = query_words & text_words
        if common:
            results.append((idx, case, len(common)))
    results.sort(key=lambda x: x[2], reverse=True)
    return [(idx, case) for idx, case, _ in results]
