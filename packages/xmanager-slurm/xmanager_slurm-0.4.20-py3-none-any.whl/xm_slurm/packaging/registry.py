import dataclasses
import typing as tp

from xmanager import xm

T_co = tp.TypeVar("T_co", covariant=True)
P = tp.ParamSpec("P")
ExecutableSpecT = tp.TypeVar("ExecutableSpecT", bound=xm.ExecutableSpec)


@dataclasses.dataclass(frozen=True)
class IndexedContainer(tp.Generic[T_co]):
    index: int
    value: T_co


RegistrationCallable = tp.Callable[
    [tp.Sequence[IndexedContainer[xm.Packageable]]],
    tp.Sequence[IndexedContainer[xm.Executable]],
]


_REGISTRY: dict[tp.Type[xm.ExecutableSpec], RegistrationCallable] = {}


def register(
    *typs: tp.Type[ExecutableSpecT],
) -> tp.Callable[[RegistrationCallable], RegistrationCallable]:
    def decorator(
        registration_callable: RegistrationCallable,
    ) -> RegistrationCallable:
        global _REGISTRY
        for typ in typs:
            _REGISTRY[typ] = registration_callable
        return registration_callable

    return decorator


def route(
    typ: tp.Type[ExecutableSpecT],
    packageables: tp.Sequence[IndexedContainer[xm.Packageable]],
) -> tp.Sequence[IndexedContainer[xm.Executable]]:
    global _REGISTRY
    return _REGISTRY[typ](packageables)
