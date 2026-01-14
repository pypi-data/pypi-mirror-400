from typing import Callable, AsyncIterable, TypeVar

from bb_integrations_lib.protocols.pipelines import GeneratorStep

T = TypeVar("T")


class FilterStep(GeneratorStep[T, T]):
    """
    A step that will yield incoming data if filter_func returns true when passed the incoming data.
    """

    def __init__(self, filter_func: Callable[[T], bool], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter_func = filter_func

    def describe(self) -> str:
        return "Filter step execution based on data"

    async def generator(self, i: T) -> AsyncIterable[T]:
        if self.filter_func(i):
            yield i
