
# Under development

from __future__ import annotations
from typing import TypeAlias, Union, Any
from copy import deepcopy

unknown: TypeAlias = str
lambda_json: TypeAlias = unknown | dict[
            str,
            list[
                Union[list[str], 'lambda_json']
            ]
        ]

def is_unknown(num: Any):
    return isinstance(num, unknown)

class Lambda:
    def __init__(self, json: Any) -> None:
        self._num: lambda_json = self._replace(json)

    def _replace(self, json: Any) -> lambda_json:
        if is_unknown(json):
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
        if is_unknown(other._num): return other.__copy__()
        args: list[str] = other._num['lambda'][0] # type: ignore
        assert length == len(args), f'{length} != {len(args)}' # type: ignore
        for i in range(len(arg)):
            argi = arg[i] if is_unknown(arg[i]) else arg[i]
            other._num = self._become(other._num, argi, args[i]) # type: ignore
        return other

    def _become(self, json: lambda_json, num: lambda_json, un: str) -> lambda_json:
        if is_unknown(json):
            return num if json == un else json
        elif isinstance(json, dict):
            json = deepcopy(json)
            key, value = next(iter(json.items()))
            if key == 'lambda':
                nums = self._become(value[1], num, un) # type: ignore
                value[1] = nums
                return json
            elif key == 'execute':
                for i in range(len(value)): # type: ignore
                    value[i] = self._become(value[i], num, un) # type: ignore
                return json
            else:
                raise NameError(f'Unknown key: {key}')
        else:
            raise TypeError(f'Bad json: {json}')

    def _beta(self, json: lambda_json) -> lambda_json:
        if is_unknown(json):
            return json
        elif isinstance(json, dict):
            new_json = deepcopy(json)
            key, value = next(iter(new_json.items()))
            if key == 'lambda':
                new_body = self._beta(value[1]) # type: ignore
                new_json[key][1] = new_body
                return new_json
            elif key == 'execute':
                temp: lambda_json = value[0] # type: ignore
                if is_unknown(temp): return json
                func: lambda_json = self._beta(temp)
                assert isinstance(func, dict) and 'lambda' in func, f'Unknown lambda: {func}'
                func_args = func['lambda'][0]
                func_body = func['lambda'][1]
                args = value[1:]
                assert len(args) == len(func_args), f'Can\'t match args: {len(args)} != {len(func_args)}'
                new_body = func_body
                for arg_name, arg_value in zip(func_args, args):
                    reduced_arg = self._beta(arg_value) # type: ignore
                    new_body = self._become(new_body, reduced_arg, arg_name) # type: ignore
                return self._beta(new_body) # type: ignore
            else:
                raise NameError(f'Unknown key: {key}')
        else:
            raise TypeError(f'Bad json: {json}')

    def __repr__(self) -> str:
        return str(self._num)

    def __copy__(self) -> Lambda:
        return Lambda(deepcopy(self._num))

    def __eq__(self, value: object) -> bool:
        return (isinstance(value, Lambda) and self._num == value._num) or (isinstance(value, dict) and self._num == value)

    def beta(self) -> Lambda:
        return Lambda(self._beta(self._num))

    @property
    def num(self):
        return self._num

lam_true: lambda_json = {'lambda': [['stdlam::lam_true::x', 'stdlam::lam_true::y'], 'stdlam::lam_true::x']}
lam_false: lambda_json = {'lambda': [['stdlam::lam_true::x', 'stdlam::lam_true::y'], 'stdlam::lam_true::y']}
lam_and: lambda_json = {'lambda': [['stdlam::lam_and::x', 'stdlam::lam_and::y'], {'execute': ['stdlam::lam_and::x', 'stdlam::lam_and::y', lam_false]}]}

def main() -> None:
    a: Lambda = (Lambda(
        {'execute': [
            lam_and, lam_false, lam_true
        ]}
    ).beta().beta())
    print(
        Lambda(
            {'execute': [a, 'true', 'false']}
        ).beta()
    )

if __name__ == '__main__':
    main()
