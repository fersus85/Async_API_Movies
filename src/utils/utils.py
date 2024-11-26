from typing import Set, Any, Type


def get_all_subclasses(cls: Type[Any]) -> Set[Type[Any]]:
    subclasses = set()
    queue = [cls]
    while queue:
        parent = queue.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                queue.append(child)
    return subclasses
