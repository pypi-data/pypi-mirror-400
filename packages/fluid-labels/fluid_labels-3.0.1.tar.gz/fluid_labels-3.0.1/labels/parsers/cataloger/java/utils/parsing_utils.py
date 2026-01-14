from bs4 import NavigableString, Tag


def get_next_text(parent: Tag | NavigableString, name: str) -> str | None:
    element = parent.find_next(name)
    if element:
        return element.get_text()

    return None


def get_direct_child_text(parent: Tag, name: str) -> str | None:
    element = parent.find(name)
    if element:
        return element.get_text()

    return None


def safe_get_text(value: Tag | None) -> str:
    if not value:
        return ""
    return value.get_text()
