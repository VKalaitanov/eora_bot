from typing import List, Tuple, Dict

def simple_search(query: str, cases: List[Dict[str, str]]) -> List[Tuple[int, Dict[str, str]]]:
    """
    Простой поиск по совпадению слов в тексте кейсов.

    Args:
        query (str): Вопрос или поисковая фраза.
        cases (List[Dict[str, str]]): Список кейсов, каждый кейс должен содержать ключ 'text'.

    Returns:
        List[Tuple[int, Dict[str, str]]]: Список найденных кейсов в формате (индекс, кейс),
                                          отсортированный по количеству совпадений слов (по убыванию).
    """
    query_words = set(query.casefold().split())
    results: List[Tuple[int, Dict[str, str], int]] = []

    for idx, case in enumerate(cases):
        text_words = set(case.get("text", "").casefold().split())
        common_count = len(query_words & text_words)
        if common_count > 0:
            results.append((idx, case, common_count))

    # Сортировка по количеству совпадений (по убыванию)
    results.sort(key=lambda x: x[2], reverse=True)

    # Возвращаем только индекс и кейс
    return [(idx, case) for idx, case, _ in results]
