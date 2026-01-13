# *************************************************************************
#
#  Copyright (c) 2025 - Datatailr Inc.
#  All Rights Reserved.
#
#  This file is part of Datatailr and subject to the terms and conditions
#  defined in 'LICENSE.txt'. Unauthorized copying and/or distribution
#  of this file, in parts or full, via any medium is strictly prohibited.
# *************************************************************************

from typing import Any, ClassVar


class dt__Tag:
    """
    Tag management for local runs in the absence of the DataTailr platform.
    All instances share the same tag store.
    """

    # shared across all instances
    tags: ClassVar[dict[str, Any]] = {
        "blob_storage_prefix": "local-no-dt-",
    }

    def ls(self) -> dict[str, Any]:
        return self.__class__.tags

    def get(self, name: str) -> Any:
        return self.__class__.tags.get(name)

    def set(self, name: str, value: Any) -> None:
        self.__class__.tags[name] = value

    def rm(self, name: str) -> None:
        self.__class__.tags.pop(name, None)


__DT_TAGS__ = None
__TAGS__ = {}


def dt_tags():
    global __DT_TAGS__
    if __DT_TAGS__ is None:
        from datatailr.wrapper import dt__Tag

        __DT_TAGS__ = dt__Tag()
    return __DT_TAGS__


def get_tag(key: str, cached: bool = True):
    global __TAGS__
    if not cached or key not in __TAGS__:
        __TAGS__[key] = dt_tags().get(key)
    return __TAGS__[key]
