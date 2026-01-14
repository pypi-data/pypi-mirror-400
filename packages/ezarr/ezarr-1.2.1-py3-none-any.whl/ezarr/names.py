from typing import final


@final
class Attribute:
    EZType = "__ez_type__"
    EZClass = "__ez_class__"

    EZVectorSize = "size"


@final
class EZType:
    Object = "object"
    List = "list"
    Vector = "vector"


UNKNOWN = "<UNKNWON>"
