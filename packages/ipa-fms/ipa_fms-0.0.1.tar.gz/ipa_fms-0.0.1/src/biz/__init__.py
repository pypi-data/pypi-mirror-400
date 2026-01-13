from sdk import add


def demo_biz_add(a: int, b: int) -> int:
    c = add(a, b)
    print(f"add({a}, {b}) = {c}")
    return c
