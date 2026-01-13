from collections.abc import Callable
from dataclasses import dataclass, asdict
from typing import TYPE_CHECKING, Any, AnyStr, Concatenate, Literal, Self

if TYPE_CHECKING:
    from _typeshed import DataclassInstance, SupportsRead, SupportsWrite
else:
    DataclassInstance = object

type Load[AnyStr: (str, bytes)] = Callable[Concatenate[SupportsRead[AnyStr], ...], dict[str, Any]]
type Loads[AnyStr: (str, bytes)] = Callable[Concatenate[AnyStr, ...], dict[str, Any]]

type Dump[AnyStr: (str, bytes)] = Callable[Concatenate[Any, SupportsWrite[AnyStr], ...], None]
type Dumps[AnyStr: (str, bytes)] = Callable[Concatenate[Any, ...], AnyStr]


@dataclass
class AvoineFormat:
    load: Load | None = None
    loads: Loads | None = None
    dump: Dump | None = None
    dumps: Dumps | None = None


class Avoine:
    """Manages state for avoine"""

    __fmts: dict[str, AvoineFormat] = {}
    __default_fmt: str | None = None

    def register(self, name: str, *, default: bool = False,
                 load: Load | None = None,
                 loads: Loads | None = None,
                 dump: Dump | None = None,
                 dumps: Dumps | None = None):
        """Register a loading/dumping format

        :param name: the name of the format
        :param default: make this format the default (used when unspecified)
        :param load: the loader from file-like object function
        :param loads: the loader from string-like object function
        :param dump: the dumper to file-like object function
        :param dumps: the dumper to string-like object function
        """
        if name not in self.__fmts:
            self.__fmts[name] = AvoineFormat()
        self.__fmts[name].load = load
        self.__fmts[name].loads = loads
        self.__fmts[name].dump = dump
        self.__fmts[name].dumps = dumps
        if default:
            self.__default_fmt = name

    def unregister(self, name: str, default: str | None = None):
        """Unregisters a format

        :param name: the name of the format
        :param default: the name of the new default format
        """
        if name in self.__fmts:
            del self.__fmts[name]
        if self.default == name:
            self.default = None
        if default:
            self.default = default

    def clear(self):
        """Clear all registered formats"""
        self.__fmts = {}
        self.__default_fmt = None

    def formats(self, method: Literal["load", "loads", "dump", "dumps"] | None = None) -> list[str]:
        """List all registered formats

        :param method: list all registered formats that implement this method
        :raises ValueError: if the method is unknown
        """
        match method:
            case "load" | "loads" | "dump" | "dumps":
                return [k for k, v in self.__fmts.items() if getattr(v, method) is not None]
            case None:
                return list(self.__fmts.keys())
            case _:
                raise ValueError(f"unknown method: {method}")

    @property
    def default(self) -> str | None:
        """Get the default format for loading/dumping

        :return: the name of the default format (or `None` if not set)
        """
        return self.__default_fmt

    @default.setter
    def default(self, format: str | None = None):
        """Set the default format for loading/dumping

        :param format: the new default format
        :raises ValueError: if the format is not registered
        """
        if format is not None and format not in self.__fmts:
            raise ValueError(f"unknown format: {format}")
        self.__default_fmt = format

    def _get_format(self, format: str | None = None) -> AvoineFormat:
        if (not format and not (format := self.default)):
            raise NotImplementedError(f"no default format set, format must be specified")
        if format not in self.__fmts:
            raise ValueError(f"unknown format: {format}")
        return self.__fmts[format]


class AvoineBase(DataclassInstance):
    """Mixin to add loading/dumping capabilities to a dataclass"""

    @classmethod
    def load(cls, fp: SupportsRead[AnyStr], format: str | None = None, **kwargs) -> Self:
        """Load data from a file-like object

        Exceptions from the underlying loader are passed up.

        :param fp: the file-like object to read from
        :param format: the format to use for loading
        :param kwargs: keyword arguments passed to the underlying loader
        :raises ValueError: if the format is not registered
        :raises NotImplementedError: if loading from file-like object is not supported for the specified format
        """
        if (load := avoine._get_format(format).load) is None:
            raise NotImplementedError(f"loading from {format} file is not supported")
        return cls(**load(fp, **kwargs))

    @classmethod
    def loads(cls, s: AnyStr, format: str | None = None, **kwargs) -> Self:
        """Load data from a string-like object

        Exceptions from the underlying loader are passed up.

        :param s: the string-like object to read from
        :param format: the format to use for loading
        :param kwargs: keyword arguments passed to the underlying loader
        :raises ValueError: if the format is not registered
        :raises NotImplementedError: if loading from string-like object is not supported for the specified format
        """
        if (loads := avoine._get_format(format).loads) is None:
            raise NotImplementedError(f"loading from {format} string is not supported")
        return cls(**loads(s, **kwargs))

    def dump(self, fp: SupportsWrite[AnyStr], format: str | None = None, **kwargs):
        """Dump data to a file-like object

        Exceptions from the underlying dumper are passed up.

        :param fp: the file-like object to write to
        :param format: the format to use for dumping
        :param kwargs: keyword arguments passed to the underlying dumper
        :raises ValueError: if the format is not registered
        :raises NotImplementedError: if dumping to file-like object is not supported for the specified format
        """
        if (dump := avoine._get_format(format).dump) is None:
            raise NotImplementedError(f"dumping to {format} file is not supported")
        dump(asdict(self), fp, **kwargs)

    def dumps(self, format: str | None = None, **kwargs) -> AnyStr:
        """Dump data to a string-like object

        Exceptions from the underlying dumper are passed up.

        :param format: the format to use for dumping
        :param kwargs: keyword arguments passed to the underlying dumper
        :raises ValueError: if the format is not registered
        :raises NotImplementedError: if dumping to string-like object is not supported for the specified format
        :return: the dumped data
        """
        if (dumps := avoine._get_format(format).dumps) is None:
            raise NotImplementedError(f"dumping to {format} string is not supported")
        return dumps(asdict(self), **kwargs)


avoine = Avoine()
