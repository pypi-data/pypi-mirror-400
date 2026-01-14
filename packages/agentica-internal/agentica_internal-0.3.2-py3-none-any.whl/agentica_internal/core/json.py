from typing import cast

__all__ = [
    'Json',
    'JsonObject',
    'JsonList',
    'JsonNumber',
    'JsonDatum',
    'json_merge',
    'JsonMergeStrategy',
]

type Json = JsonObject | JsonList | JsonDatum
type JsonObject = dict[str, Json]
type JsonList = list[Json]
type JsonNumber = int | float
type JsonDatum = str | JsonNumber | bool | None


class JsonMergeStrategy:
    # Objects are merged by default
    def object_merge[J: JsonObject](self, a: J, b: J) -> J:
        c: JsonObject = dict()
        for key in a.keys() | b.keys():
            if key in a and key in b:
                c[key] = json_merge(a[key], b[key])
            elif key in a:
                c[key] = a[key]
            elif key in b:
                c[key] = b[key]
        return cast(J, c)

    # Lists are superimposed by default, not concatenated
    def list_merge[J: JsonList](self, a: J, b: J) -> J:
        # len(a) <= len(b)
        a, b = sorted((a, b), key=lambda x: len(x))

        c = b.copy()
        for i in range(len(a)):
            c[i] = json_merge(a[i], b[i])
        return cast(J, c)

    # Strings are concatenated by default
    def string_merge(self, a: str, b: str) -> str:
        return a + b

    # Numbers are summed by default
    def number_merge(self, a: JsonNumber, b: JsonNumber) -> JsonNumber:
        return a + b

    # Booleans are or-ed by default
    def bool_merge(self, a: bool, b: bool) -> bool:
        return a or b

    # None and False-y values are overridden by default
    def datum_merge[J: Json](self, a: J, b: J) -> J:
        return a or b

    def merge[J: Json](
        self,
        a: J,
        b: J,
    ) -> J:
        """Merge two JSON items of roughly the same shape."""
        if isinstance(a, dict) and isinstance(b, dict):
            return self.object_merge(a, b)
        elif isinstance(a, list) and isinstance(b, list):
            return self.list_merge(a, b)
        elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
            return cast(J, self.number_merge(a, b))
        elif isinstance(a, str) and isinstance(b, str):
            return cast(J, self.string_merge(a, b))
        elif isinstance(a, bool) and isinstance(b, bool):
            return cast(J, self.bool_merge(a, b))
        else:
            return cast(J, self.datum_merge(a, b))


json_merge = JsonMergeStrategy().merge
