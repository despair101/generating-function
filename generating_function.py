from typing_extensions import Callable, Iterable, Self
from functools import lru_cache

Number = int | float

def div(a: Number, b: Number):
    if isinstance(a, int) and isinstance(b, int) and a % b == 0:
        return a // b
    return a / b


class GeneratingFunction:
    __slots__ = ["func"]

    def __init__(self, func: Callable[[int], Number]):
        self.func = func

    @staticmethod
    def const(value: Number):
        return GeneratingFunction(lambda i: value if i == 0 else 0)

    @staticmethod
    def finite(values: Iterable[Number]):
        return GeneratingFunction(lambda i: values[i] if i < len(values) else 0)

    def __add__(self, other: Number | Self):
        if isinstance(other, Number):
            return self + self.const(other)
        return GeneratingFunction(lambda i: self.func(i) + other.func(i))

    def __radd__(self, other: Number):
        return self + other

    def __sub__(self, other: Number | Self):
        return self + (-other)

    def __rsub__(self, other: Number):
        return (-self) + other

    def __mul__(self, other: Number | Self):
        if isinstance(other, Number):
            return self * self.const(other)
        return GeneratingFunction(lambda i: sum(self.func(j) * other.func(i-j) for j in range(i + 1)))

    def __rmul__(self, other: Number):
        return self * other

    def __truediv__(self, other: Number | Self):
        if isinstance(other, Number):
            return GeneratingFunction(lambda i: div(self.func(i), other))
        return self * other**(-1)

    def __rtruediv__(self, other: Number):
        return self**(-1) * other

    def __pow__(self, pow: int):
        if pow == 0:
            return self.const(1)
        if pow == -1:
            inv = lru_cache(maxsize=200)(lambda i:
                                         div(1, self.func(0)) if i == 0 else
                                         div(-sum(inv(j) * self.func(i - j) for j in range(i)), self.func(0)))
            return GeneratingFunction(inv)
        if pow < 0:
            return (self**(-1))**(-pow)
        result = self ** 0
        current_func = GeneratingFunction(self.func)
        while pow > 0:
            if pow % 2 == 1:
                result *= current_func
            current_func *= current_func
            pow //= 2
        return result

    def __neg__(self):
        return GeneratingFunction(lambda i: -self.func(i))

    def __getitem__(self, key: int) -> Number | list[Number]:
        if isinstance(key, slice):
            return list(map(self.func, range(*key.indices(key.stop))))
        return self.func(key)

    def __format__(self, format_spec: str) -> str:
        try:
            out_len = int(format_spec)
        except:
            out_len = 10
        return ' + '.join([f'{self.func(i)}x^{i}' for i in range(out_len)]) + ' + ...'

    def __str__(self) -> str:
        return f"{self}"

    def derivative(self):
        return GeneratingFunction(lambda i: (i + 1) * self.func(i + 1))

    def __iter__(self) -> Iterable[Number]:
        i = 0
        while True:
            yield self.func(i)
            i += 1