from typing import *

import setdoc

__all__ = ["VersionError"]


class VersionError(ValueError):

    args: tuple  # inherited property

    @setdoc.basic
    def __init__(self: Self, *args: Any) -> None:
        super().__init__(*args)
