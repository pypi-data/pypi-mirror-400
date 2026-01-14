
from __future__ import annotations
from typing import TypeAlias, Union, Any
from copy import deepcopy

def _to_str(num: Any) -> str:
    return str(num)

unknown: TypeAlias = str
lambda_json: TypeAlias = Union[unknown, dict[
    str,
    list[Union[list[str], 'Lambda', 'lambda_json']]
]]

def is_unknown(num: Any) -> bool:
    return isinstance(num, unknown)

class Lambda:
    def __init__(self, json: Any) -> None:
        self._num: lambda_json = self._replace(json)

    def _replace(self, json: Any) -> lambda_json:
        if self.empty(json):
            return {}
        elif is_unknown(json):
            return json
        elif isinstance(json, dict):
            json = deepcopy(json)
            key, value = next(iter(json.items()))
            if key == 'lambda':
                json['lambda'][1] = self._replace(value[1])
                return json
            elif key == 'execute':
                for i in range(len(value)):
                    value[i] = self._replace(value[i])
                json['execute'] = value
                return json
            else:
                raise NameError(f'Unknown key: {key}')
        elif isinstance(json, Lambda):
            return json._num
        else:
            raise TypeError(f'Bad json: {json}')

    def _parse(self, arg: list[lambda_json]) -> Lambda:
        length: int = len(arg)
        other = self.__copy__()
        if is_unknown(other._num):
            return other.__copy__()
        args: list[str] = other._num['lambda'][0]  # type: ignore[index]
        assert length == len(args), f'{length} != {len(args)}'
        for i in range(len(arg)):
            argi = arg[i] if is_unknown(arg[i]) else arg[i]
            other._num = self._become(other._num, argi, args[i])  # type: ignore[assignment]
        return other

    def _become(self, json: lambda_json, num: lambda_json, un: str) -> lambda_json:
        if self.empty(json):
            return {}
        elif is_unknown(json):
            return num if json == un else json
        elif isinstance(json, dict):
            json = deepcopy(json)
            key, value = next(iter(json.items()))
            if key == 'lambda':
                if un in value[0]:  # type: ignore[operator]
                    return json
                nums = self._become(value[1], num, un)  # type: ignore[arg-type]
                value[1] = nums
                return json
            elif key == 'execute':
                for i in range(len(value)):
                    value[i] = self._become(value[i], num, un)  # type: ignore[arg-type]
                return json
            else:
                raise NameError(f'Unknown key: {key}')
        else:
            raise TypeError(f'Bad json: {json}')

    def _beta(self, json: lambda_json) -> lambda_json:
        if self.empty(json):
            return {}
        elif is_unknown(json):
            return json
        elif isinstance(json, dict):
            new_json = deepcopy(json)
            key, value = next(iter(new_json.items()))
            if key == 'lambda':
                new_body = self._beta(value[1])  # type: ignore[arg-type]
                new_json[key][1] = new_body
                return new_json
            
            elif key == 'execute':
                func = self._beta(value[0])  # type: ignore[index]
                if not (isinstance(func, dict) and 'lambda' in func):
                    new_args = [self._beta(arg) for arg in value[1:]]  # type: ignore[arg-type]
                    return {'execute': [func] + new_args} # type: ignore
                func_args = func['lambda'][0]
                func_body = func['lambda'][1]
                args = value[1:]
                new_body = func_body
                for arg_name, arg_value in zip(func_args, args):  # type: ignore[arg-type]
                    reduced_arg = self._beta(arg_value)  # type: ignore[arg-type]
                    new_body = self._become(new_body, reduced_arg, arg_name)  # type: ignore[arg-type]
                    new_body = self._beta(new_body)
                remaining_args = func_args[len(args):]  # type: ignore[slice]
                if remaining_args:
                    return {'lambda': [remaining_args, new_body]} # type: ignore
                else:
                    return self._beta(new_body) # type: ignore
            else:
                raise NameError(f'Unknown key: {key}')
        else:
            raise TypeError(f'Bad json: {json}')

    def _getstr(self, num: lambda_json, symbol: str, end: str, sep: str) -> str:
        assert isinstance(symbol, str), f'Unknown symbol: {symbol}'
        assert isinstance(end, str), f'Unknown end: {end}'
        assert isinstance(sep, str), f'Unknown sep: {sep}'
        if self.empty(num):
            return ''
        elif is_unknown(num):
            return num # pyright: ignore[reportReturnType]
        elif isinstance(num, dict):
            key, value = next(iter(num.items()))
            if key == 'lambda':
                str_list: list[str] = []
                for i in value[0]:  # type: ignore[iterable]
                    str_list.append(f'{symbol.format(i)}.')
                body_str = self._getstr(value[1], symbol, end, sep)  # type: ignore[arg-type]
                return end.format(''.join(str_list), body_str)
            elif key == 'execute':
                for i in range(len(value)):
                    value[i] = self._getstr(value[i], symbol, end, sep) # pyright: ignore[reportArgumentType]
                execute_str = sep.join(map(_to_str, value)) # pyright: ignore[reportArgumentType]
                return f'({execute_str})'
            else:
                raise NameError(f'Unknown key: {key}')
        else:
            raise TypeError(f'Unknown type: {type(num)}, num: {num}')

    def __repr__(self) -> str:
        return str(self._num)

    def __str__(self) -> str:
        return self.getstr()

    def __copy__(self) -> Lambda:
        return Lambda(deepcopy(self._num))

    def __eq__(self, value: object) -> bool:
        return (isinstance(value, Lambda) and self._num == value._num) or (isinstance(value, dict) and self._num == value)

    def beta(self) -> Lambda:
        return Lambda(self._beta(self._num))

    def getstr(self, symbol: str = 'lambda {0}', end: str = '{0}{1}', sep: str = ' ') -> str:
        return self._getstr(self._num, symbol, end, sep)

    def empty(self, json: lambda_json) -> bool:
        return json == {}

    @property
    def num(self) -> lambda_json:
        return self._num

# Init

L: str = 'lambda'
E: str = 'execute'

argx  : str = 'x'
argy  : str = 'y'
argz  : str = 'z'
argf  : str = 'f'
argbx : str = 'bx'
argby : str = 'by'

argx2 : str = 'x2'
argy2 : str = 'y2'
argz2 : str = 'z2'
argf2 : str = 'f2'
argby2: str = 'by2'

lam_none: Lambda = Lambda({})

lam_true : Lambda = Lambda({L: [[argx, argy], argx]})
lam_false: Lambda = Lambda({L: [[argx, argy], argy]})

_inf_tool: Lambda = Lambda({L: [[argx], {E: [argx, argx]}]})

zero : Lambda = Lambda({L: [[argf, argx], argx]})
one  : Lambda = Lambda({L: [[argf, argx], {E: [argf, argx]}]})
two  : Lambda = Lambda({L: [[argf, argx], {E: [argf, {E: [argf, argx]}]}]})
three: Lambda = Lambda({L: [[argf, argx], {E: [argf, {E: [argf, {E: [argf, argx]}]}]}]})
four : Lambda = Lambda({L: [[argf, argx], {E: [argf, {E: [argf, {E: [argf, {E: [argf, argx]}]}]}]}]})
five : Lambda = Lambda({L: [[argf, argx], {E: [argf, {E: [argf, {E: [argf, {E: [argf, {E: [argf, argx]}]}]}]}]}]})
inf  : Lambda = Lambda({L: [[argx], {E: [_inf_tool, _inf_tool]}]})

pair: Lambda = Lambda({L: [[argx, argy], {L: [[argf], {E: [argf, argx, argy]}]}]})
fst : Lambda = Lambda({L: [[argx], {E: [argx, lam_true]}]})
snd : Lambda = Lambda({L: [[argx], {E: [argx, lam_false]}]})

initial_pair: Lambda = Lambda({E: [pair, zero, zero]})

# Bool

lam_and: Lambda = Lambda({L: [[argbx, argby], {E: [argbx, argby, lam_false]}]})
lam_or : Lambda = Lambda({L: [[argbx, argby], {E: [argbx, lam_true, argby]}]})
lam_not: Lambda = Lambda({L: [[argbx       ], {E: [argbx, lam_false, lam_true]}]})

lam_ifelse: Lambda = Lambda({L: [[argbx, argx, argy], {E: [argbx, argx, argy]}]})
lam_if    : Lambda = Lambda({L: [[argbx, argx], {E: [argbx, argx, lam_none]}]})

# Number

lam_succ: Lambda = Lambda({L: [[argx], {L: [[argf, argx2], {E: [argf, {E: [argx, argf, argx2]}]}]}]})
lam_add : Lambda = Lambda({L: [[argx, argy], {L: [[argf, argx2], {E: [argx, argf, {E: [argy, argf, argx2]}]}]}]})
shift   : Lambda = Lambda({L: [[argx], {E: [pair, {E: [snd, argx]}, {E: [lam_succ, {E: [snd, argx]}]}]}]})

predecessor: Lambda = Lambda({L: [[argx], {E: [fst, {E: [argx, shift, initial_pair]}]}]})

def beta(num: Lambda) -> Lambda:
    assert isinstance(num, Lambda), f'Unknown num: {num}'
    return num.beta()

def btos(num: Lambda) -> str:
    beta_json: lambda_json = beta(Lambda({E: [num, 'true', 'false']}))._num
    assert isinstance(beta_json, str), f'Bad Lambda: {num}'
    return beta_json

def estr(num: Lambda) -> str:
    return num.getstr(symbol='λ{0}')

def main() -> None:
    lambda_inst1: Lambda = Lambda({'execute': [lam_and, lam_false, lam_true]})
    print("and(false, true) =", btos(lambda_inst1.beta()))

    lambda_inst2: Lambda = Lambda({'execute': [lam_add, one, two]})
    print("one + two =", estr(lambda_inst2.beta()))

    lambda_inst3: Lambda = Lambda({'execute': [lam_succ, zero]})
    print("succ(zero) =", estr(lambda_inst3.beta()))

if __name__ == '__main__':
    main()
