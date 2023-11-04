import typing as tp

if tp.TYPE_CHECKING:
    from uuid import UUID

GLOBALS: 'dict[UUID, tp.Any]' = {}


def get_global(key: 'UUID') -> tp.Any:
    return GLOBALS.get(key)


def set_global(key: 'UUID', value: tp.Any):
    GLOBALS[key] = value
