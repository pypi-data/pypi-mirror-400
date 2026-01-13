def match_hierarchy(text: str, pattern: str) -> bool:
    """
    匹配由 '.' 分隔的层级字符串。

    通配符规则：
      - '*'  匹配恰好一个层级段（即两个 '.' 之间的部分）
      - '#'  匹配零个或多个连续的层级段
      - 其他字符必须完全相等

    示例：
      match_hierarchy("a.b.c", "a.*.c")   → True
      match_hierarchy("a.b.c.d", "a.#")   → True
      match_hierarchy("x.y", "x.*.z")     → False
    """
    if pattern == '#':
        return True

    text_parts = text.split('.')
    pattern_parts = pattern.split('.')

    def _match(t_idx: int, p_idx: int) -> bool:
        # 模式和文本都结束：匹配成功
        if p_idx == len(pattern_parts):
            return t_idx == len(text_parts)

        # 文本已结束，但模式还有剩余
        if t_idx == len(text_parts):
            # 剩余模式必须全为 '#' 才可能匹配
            return all(p == '#' for p in pattern_parts[p_idx:])

        current = pattern_parts[p_idx]

        if current == '#':
            # 尝试匹配 0 个段
            if _match(t_idx, p_idx + 1):
                return True
            # 尝试匹配 1 个、2 个……直到末尾
            for i in range(t_idx, len(text_parts)):
                if _match(i + 1, p_idx + 1):
                    return True
            return False

        elif current == '*':
            # 匹配恰好一个段
            return _match(t_idx + 1, p_idx + 1)

        else:
            # 普通字符串，必须完全相等
            return text_parts[t_idx] == current and _match(t_idx + 1, p_idx + 1)

    return _match(0, 0)


def best_match(text: str, patterns: list[str]) -> str | None:
    """
    在多个 pattern 中，找出与 text 匹配且匹配度最高的 pattern 的索引。

    - 自动跳过 patterns 中的 None 或非字符串值
    - 匹配度规则（从高到低）：
        1. 不含 '#' 的 pattern 优于含 '#' 的
        2. '*' 越少越优
        3. 段数（. 分割后的长度）越多越优

    返回最匹配的 pattern 在 `patterns` 中的索引，若无有效匹配则返回 None。
    """
    if not isinstance(text, str):
        return None  # 非法输入

    matched_with_index = []

    for i, p in enumerate(patterns):
        # 跳过 None、非字符串、或空字符串（可选：空字符串是否有效？）
        if p is None or not isinstance(p, str):
            continue
        # 可选：跳过空字符串（因为 "".split('.') → ['']，可能不符合预期）
        # if p == "":
        #     continue

        if match_hierarchy(text, p):
            matched_with_index.append((i, p))

    if not matched_with_index:
        return None

    def _priority(item: tuple[int, str]) -> tuple[int, int, int]:
        _, p = item
        parts = p.split('.')
        has_hash = 1 if '#' in parts else 0
        star_count = parts.count('*')
        segment_count = len(parts)
        return (has_hash, star_count, -segment_count)

    best_item = min(matched_with_index, key=_priority)
    return best_item[0]


if __name__ == '__main__':
    assert match_hierarchy("a.b.c", "a.*.c") == True
    assert match_hierarchy("a.b.c", "#.c") == True
    assert match_hierarchy("a.b.c", "*.*.c") == True
    assert match_hierarchy("a.b.c.d", "a.*.d") == False
    assert match_hierarchy("a.b.c", "a.#") == True
    assert match_hierarchy("a", "a.#") == True
    assert match_hierarchy("a.b.c", "#") == True
    assert match_hierarchy("stock.usd.nyse", "stock.*.nyse") == True
    assert match_hierarchy("nyse.ibm", "stock.*.nyse") == False
    assert match_hierarchy("quick.orange.rabbit", "quick.*") == False

    assert best_match("x.y", ["x.*", "x.y"]) == 1
    assert best_match("a.b.c", ["a.#", "a.*.c"]) == 1  # 无 # 优于有 #
    assert best_match("a", ["#", "a"]) == 1
    assert best_match("a.b", ["a.*", "*.*"]) == 0  # * 更少
    assert best_match("a.b.c", ["a.b.*", "a.*.*"]) == 0  # 段数更多
    assert best_match("a.b.c", ["a.b.#", "a.*.*"]) == 1  # 段数更多
    assert best_match("a.b.c", ["a.b.#", None, "a.*.*"]) == 2  # 段数更多
    print("✅ All tests passed!")
