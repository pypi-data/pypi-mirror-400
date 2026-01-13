# avoine

A tiny serialisation and deserialisation library.

`avoine` does not implement any serialisation or deserialisation itself. Instead,
it relies on the common Python pattern of `load` and `dump` functions (for file-like
objects) and `loads` and `dumps` functions (for string-like objects).

To configure serialisation and deserialisation, use the `avoine` class:

```py
import json
import tomllib

from avoine import avoine

# define a format for deserialisation (load -> from file, loads -> from string/bytes)
# and serialisation (dump -> from file, dumps -> from string/bytes) and set it as default
avoine.register("json", default=True, load=json.load, loads=json.loads, dump=json.dump, dumps=json.dumps)

# not all methods are required
avoine.register("toml", load=tomllib.load)

# register can be used again to update a format definition
avoine.register("toml", loads=tomllib.loads)

# the default format is what is used when the format is left unspecified
# it can be set or unset on its own
avoine.default = "toml"
avoine.default = None

# and retrieved with
print(avoine.default)

# you can unregister a format too
avoine.unregister("toml", default="json")

# the list of currently-registered formats can be retrieved with
avoine.formats()

# or for a specific method with
avoine.formats("load")

# all configuration can be reset with
avoine.clear()
```

Then, in your code, you can define dataclasses and add the `AvoineBase` mixin class,
which will allow you to serialise/deserialise them from any registered format anywhere:

```py
from dataclasses import dataclass
from avoine import AvoineBase

@dataclass
class MyStruct(AvoineBase):
    foo: str
    bar: MyInnerStruct

@dataclass
class MyInnerStruct(AvoineBase):
    baz: list[str]
    opt: str | None = None

with open("mystruct.json") as f:
    data = MyStruct.load(f)
    # kwargs for the underlying loader/dumper are passed down to them
    data.dumps(indent=2)

with open("mystruct.toml") as f:
    print(MyStruct.load(f, format="toml"))
```

Custom formats can be created by writing functions with the following signatures:

```py
def load(fp: SupportsRead[AnyStr], **kwargs) -> dict[str, Any]:
    ...

def loads(s: AnyStr, **kwargs) -> dict[str, Any]:
    ...

def dump(obj: Any, fp: SupportsWrite[AnyStr], **kwargs) -> None:
    ...

def dumps(obj: Any, **kwargs) -> AnyStr:
    ...
```

Notes:

- `AnyStr` can be `str`, `bytes`, or both
- `kwargs` are optional

If a set of loading/dumping functions for a format do not match these signatures,
wrapper functions can be written to transform them to a compatible signature.

## License

avoine is in the public domain.

To the extent possible under law, classabbyamp has waived all copyright and related or neighboring rights to this work.

http://creativecommons.org/publicdomain/zero/1.0/
