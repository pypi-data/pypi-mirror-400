
# Note: All module don't have commant.

from __future__ import annotations
from typing import TypeAlias, Callable, Union
from math import log, sqrt
from copy import deepcopy

unknown: TypeAlias = str
number: TypeAlias = int | float

algebra_json: TypeAlias = Union[
        unknown,
        number,
        dict[
            str,
            list[Union[unknown, number, 'algebra_json']]
        ]
]

SYMBOL_CONFIG: dict[str, dict[str, int | str]] = {
    'ln': {'priority': 4, 'arity': 1, 'format': 'ln({0})'},
    'sqrt': {'priority': 4, 'arity': 1, 'format': 'sqrt({0})'},

    '**': {'priority': 3, 'arity': 2, 'format': '{0} ** {1}', 'assoc': 'right'},
    '*': {'priority': 2, 'arity': 2, 'format': '{0} * {1}', 'assoc': 'left'},
    '/': {'priority': 2, 'arity': 2, 'format': '{0} / {1}', 'assoc': 'left'},
    '+': {'priority': 1, 'arity': 2, 'format': '{0} + {1}', 'assoc': 'left'},
    '-': {'priority': 1, 'arity': 2, 'format': '{0} - {1}', 'assoc': 'left'},
}

def is_al(num: object) -> bool:
    return isinstance(num, (int, float, str))

def is_number(num: object) -> bool:
    return isinstance(num, (int, float))

def is_unknown(num: object) -> bool:
    return isinstance(num, str)

def _expr_to_str(expr: algebra_json, parent_priority: int = 0, is_right_child: bool = False) -> str:
    if is_number(expr):
        return str(expr)
    elif is_unknown(expr):
        return expr # type: ignore
    elif isinstance(expr, dict):
        op, args = next(iter(expr.items()))
        if op not in SYMBOL_CONFIG:
            return str(expr)
        cfg: dict[str, int | str] = SYMBOL_CONFIG[op]
        priority: int = cfg['priority'] # type: ignore
        arity: int = cfg['arity'] # type: ignore
        assoc: str = cfg.get('assoc', 'left') # type: ignore
        if arity == 1:
            child = _expr_to_str(args[0], priority)
            return cfg['format'].format(child) # type: ignore
        elif arity == 2:
            left = _expr_to_str(args[0], priority, is_right_child=False)
            right_priority = priority - 1 if assoc == 'right' else priority
            right = _expr_to_str(args[1], right_priority, is_right_child=True)
            expr_str: str = cfg['format'].format(left, right) # type: ignore
            if priority < parent_priority:
                return f"({expr_str})"
            elif priority == parent_priority:
                if (assoc == 'left' and not is_right_child) or (assoc == 'right' and is_right_child):
                    return expr_str
                else:
                    return f"({expr_str})"
            else:
                return expr_str
        else:
            return str(expr)
    else:
        return str(expr)

class Algebra:
    # ----method---- #

    def _unknown(self, un: unknown | Algebra) -> unknown:
        if is_unknown(un):
            return un  # type: ignore
        elif isinstance(un, Algebra):
            temp: algebra_json = un._num
            if is_unknown(temp):
                return temp # type: ignore
            raise TypeError(f'Unknown type: {type(temp).__name__}.')
        raise TypeError(f'Unknown type: {type(un).__name__}.')

    def _get(self, num: Algebra | number | algebra_json | unknown) -> algebra_json:
        if isinstance(num, Algebra):
            return num._num
        elif is_al(num) or isinstance(num, dict) :
            return num
        else:
            raise TypeError(f'Unknown type: {type(num).__name__}.')

    # ----init---- #

    def __init__(self, num: Algebra | number | algebra_json | unknown) -> None:
        self._num: algebra_json = self._get(num)

    # ----add---- #

    def __add__(self, num: Algebra | number) -> Algebra:
        null: Algebra = Algebra(0)
        r: algebra_json = self._get(num)
        
        null._num = {'+': [self._num, r]}
        return null
    
    def __radd__(self, num: Algebra | number) -> Algebra:
        return self.__add__(num)

    # ----sub---- #

    def __sub__(self, num: Algebra | number) -> Algebra:
        null: Algebra = Algebra(0)
        r: algebra_json = self._get(num)
        
        null._num = {'-': [self._num, r]}
        return null
    
    def __rsub__(self, num: Algebra | number) -> Algebra:
        null: Algebra = Algebra(0)
        r: algebra_json = self._get(num)
        
        null._num = {'-': [r, self._num]}
        return null

    # ----mul---- #

    def __mul__(self, num: Algebra | number) -> Algebra:
        null: Algebra = Algebra(0)
        r: algebra_json = self._get(num)
        
        null._num = {'*': [self._num, r]}
        return null

    def __rmul__(self, num: Algebra | number) -> Algebra:
        return self.__mul__(num)

    # ----pow---- #

    def __pow__(self, num: Algebra | number) -> Algebra:
        null: Algebra = Algebra(0)
        r: algebra_json = self._get(num)
        
        null._num = {'**': [self._num, r]}
        return null

    def __rpow__(self, num: Algebra | number) -> Algebra:
        null: Algebra = Algebra(0)
        r: algebra_json = self._get(num)
        
        null._num = {'**': [r, self._num]}
        return null 

    # ----div---- #

    def __truediv__(self, num: Algebra | number) -> Algebra:
        null: Algebra = Algebra(0)
        r: algebra_json = self._get(num)
        
        null._num = {'/': [self._num, r]}
        return null

    def __rtruediv__(self, num: Algebra | number) -> Algebra:
        null: Algebra = Algebra(0)
        r: algebra_json = self._get(num)
        
        null._num = {'/': [r, self._num]}
        return null

    # ----some methods---- #

    def _derivative(self, num: algebra_json, un: unknown) -> Algebra:
        if is_number(num):
            return Algebra(0)
        elif is_unknown(num):
            return Algebra(1) if num==un else Algebra(0)
        elif isinstance(num, dict):
            key, value = next(iter(num.items()))
            d: Callable = lambda v: self._derivative(v, un)

            if key == '+':
                f: algebra_json = value[0]
                g: algebra_json = value[1]
                return d(f) + d(g)
            elif key == '-':
                f: algebra_json = value[0]
                g: algebra_json = value[1]
                return d(f) - d(g)
            elif key == '*':
                f: algebra_json = value[0]
                g: algebra_json = value[1]
                return d(f) * value[1] + d(g) * value[0]
            elif key == '/':
                f: algebra_json = value[0]
                g: algebra_json = value[1]
                return (d(f) * g - d(g) * f) / (Algebra(g) * Algebra(g))
            elif key == '**':
                f: algebra_json = value[0]
                g: algebra_json = value[1]
                dg: Algebra = d(g)
                log_part: Algebra = dg * aln(Algebra(f))
                return Algebra(f) ** Algebra(g) * (log_part + g * d(f) / f)
            elif key == 'ln':
                f: algebra_json = value[0]
                return d(f) / Algebra(f)
            elif key == 'sqrt':
                f: algebra_json = value[0]
                return d(f) / (2 * asqrt(Algebra(f)))
            else: raise TypeError(f'Unknown operator: {key}.')
        else: raise TypeError(f'Unknown type: {type(num).__name__}.')

    def _simplify(self, num: algebra_json) -> algebra_json:
        temp: algebra_json = None # type: ignore
        if is_al(num):
            temp = num
        elif isinstance(num, dict):
            key, value = next(iter(num.items()))
            for i in range(len(value)): value[i] = self._simplify(value[i])
            if key == '+':
                if value[0] == 0: temp = value[1]
                elif value[1] == 0: temp = value[0]
                elif is_number(value[0]) and is_number(value[1]): temp = value[0] + value[1] # type: ignore
                else: temp = num
            elif key == '-':
                if value[1] == 0: temp = value[0]
                elif is_number(value[0]) and is_number(value[1]): temp = value[0] - value[1] # type: ignore
                else: temp = num
            elif key == '*':
                if value[1] == 0 or value[0] == 0: temp = 0
                elif value[1] == 1: temp = value[0]
                elif value[0] == 1: temp = value[1]
                elif is_number(value[0]) and is_number(value[1]): temp = value[0] * value[1] # type: ignore
                else: temp = num
            elif key == '/':
                if value[1] == 0: raise ZeroDivisionError('Zero can\' be a DIVNUMBER.')
                elif value[0] == 0: temp = 0
                elif value[1] == 1: temp = value[0]
                elif is_number(value[0]) and is_number(value[1]): temp = value[0] / value[1] # type: ignore
                else: temp = num
            elif key == '**':
                if value[1] == 1: temp = value[0]
                elif value[0] == 0 and value[1] == 0: raise ValueError('0 ** 0 isn\'t right.')
                elif value[0] == 0: temp = 0
                elif value[1] == 0: temp = 1
                elif is_number(value[0]) and is_number(value[1]): temp = value[0] ** value[1] # type: ignore
                else: temp = num
            elif key == 'ln':
                if is_number(value[0]): temp = log(value[0]) # type: ignore
                else: temp = num
            elif key == 'sqrt':
                if is_number(value[0]): temp = sqrt(value[0]) # type: ignore
                else: temp = num
            else: raise TypeError(f'Unknown operator: {key}.')
        else: raise TypeError(f'Unknown type: {type(num).__name__}.')
        return temp

    def _getvalue(self, num: algebra_json, v: number, un: unknown) -> number:
        if is_number(num): return num # type: ignore
        elif isinstance(num, unknown):
            if num != un: raise NameError(f'Can\'t get value: {num}.')
            return v
        elif isinstance(num, dict):
            key, value = next(iter(num.items()))
            g: Callable = lambda num: self._getvalue(num, v, un)
            if key == '+': return g(value[0]) + g(value[1])
            elif key == '*': return g(value[0]) * g(value[1])
            elif key == '-': return g(value[0]) - g(value[1])
            elif key == '/': return g(value[0]) / g(value[1])
            elif key == '**': return g(value[0]) ** g(value[1])
            elif key == 'ln': return log(g(value[0]))
            elif key == 'sqrt': return sqrt(g(value[0]))
            else: raise TypeError(f'Unknown operator: {key}.')
        else: raise TypeError(f'Unknown type: {type(num).__name__}.')

    def _getvalue2(self, num: algebra_json, v: number, un: unknown) -> Algebra:
        if is_number(num): return Algebra(num)
        elif isinstance(num, unknown):
            if num != un: return Algebra(num)
            return Algebra(v)
        elif isinstance(num, dict):
            key, value = next(iter(num.items()))
            g2: Callable = lambda num: self._getvalue2(num, v, un)
            if key == '+': return g2(value[0]) + g2(value[1])
            elif key == '*': return g2(value[0]) * g2(value[1])
            elif key == '-': return g2(value[0]) - g2(value[1])
            elif key == '/': return g2(value[0]) / g2(value[1])
            elif key == '**': return g2(value[0]) ** g2(value[1])
            elif key == 'ln': return aln(g2(value[0])) # type: ignore
            elif key == 'sqrt': return asqrt(g2(value[0])) # type: ignore
            else: raise TypeError(f'Unknown operator: {key}.') 
        else: raise TypeError(f'Unknown type: {type(num).__name__}.')

    # ----else---- #

    def __repr__(self) -> str:
        return str(self._num)

    def __str__(self) -> str:
        return _expr_to_str(self._num)

    def __copy__(self) -> Algebra:
        null: Algebra = Algebra(0)
        null._num = deepcopy(self._num)
        return null

    @property
    def num(self) -> algebra_json:
        return self._num

    # ----show---- #

    def derivative(self, un: unknown | Algebra) -> Algebra:
        return self._derivative(self._num, self._unknown(un))

    def simplify(self) -> Algebra:
        """
        This is basic.
        You're welcome to do better it.
        """
        return Algebra(self._simplify(self._num))

    def getvalue(self, value: number, un: unknown | Algebra) -> int | float:
        return self._getvalue(self._num, value, self._unknown(un))

    def getalgebra(self, value: number, un: unknown | Algebra) -> Algebra:
        return self._getvalue2(self._num, value, self._unknown(un))

def aln(num: Algebra | number) -> Algebra | number:  # type: ignore
    if is_number(num): return log(num) # type: ignore
    elif isinstance(num, Algebra):
        num: Algebra = num.__copy__()
        num._num = {'ln': [num._num]} # type: ignore
        return num
    else: raise TypeError(f'Unknown type: {num}.')

def asqrt(num: Algebra | number) -> Algebra | number: # type: ignore
    if is_number(num): return sqrt(num) # type: ignore
    elif isinstance(num, Algebra):
        num: Algebra = num.__copy__()
        num._num = {'sqrt': [num._num]} # type: ignore
        return num
    else: raise TypeError(f'Unknown type: {num}.')

def alog(num: Algebra | number, num2: Algebra | number) -> Algebra | number: # type: ignore
    if is_number(num) and is_number(num2): return log(num, num2) # type: ignore
    else: return aln(num) / aln(num2)

X: Algebra = Algebra('x')
Y: Algebra = Algebra('y')
Z: Algebra = Algebra('z')

if __name__ == '__main__':
    a: Algebra = asqrt(aln(X) / X) # type: ignore
    print(X)
    print((a.derivative(X)))
