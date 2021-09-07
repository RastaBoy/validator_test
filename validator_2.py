from dataclasses import Field as DataclassesField
from dataclasses import asdict, dataclass
from dataclasses import fields
from typing import Any, Callable, Iterable, List, Optional, Union, Sequence, TypeVar

STR_ALIASES = {
    Union: str(Union),
    Iterable : str(Iterable),
    Any : str(Any),
}

@dataclass
class Validator():

    def __post_init__(self):
        self._run_validate()

    def _run_validate(self):
        for field in fields(self):
            self._is_field_valid(field)

    @staticmethod
    def _is_supported_alias(annotation : str):
        for str_alias in STR_ALIASES.values():
            if annotation.startswith(str_alias):
                return True
        return False

    @staticmethod
    def _is_typing_alias(annotation: str):
        str_aliases = STR_ALIASES.values()
        prefixes = [alias[:alias.find('.')] for alias in str_aliases]
        return annotation.startswith(tuple(prefixes))

    def _get_alias_method(self, annotation: str):
        if annotation.startswith(STR_ALIASES[Union]):
            return self._is_union_instance
        elif annotation.startswith(STR_ALIASES[Iterable]):
            return self._is_iterable_instance
        elif annotation.startswith(STR_ALIASES[Any]):
            return self._is_any_instance

    def _is_instance(self, value : Any, _type : type) -> bool:
        if self._is_typing_alias(str(_type)):
            if not self._is_supported_alias(str(_type)):
                return False
            method = self._get_alias_method(str(_type))
            if method is not None:
                result = method(value, _type)
                if result:
                    return result
        else: 
            try:
                result = isinstance(value, _type)
            except Exception as e:
                print(str(e))
                return False
            return result

        return False
    
    def _is_union_instance(self, value, _type : type):
        for item_annotation in _type.__args__:
            if self._is_instance(value, item_annotation):
                return True
        return False

    def _is_iterable_instance(self, value, _type : type):
        _type = _type.__args__[0]
        for i, item_value in enumerate(value):
            if not self._is_instance(item_value, _type):
                return False
        
        return True
    
    def _is_any_instance(self, value, _type : type):
        return True

    def _is_field_valid(self, field: DataclassesField):
        self._field_name = field.name
        self._field_value = getattr(self, field.name)
        self._field_type = field.type

        return self._is_instance(self._field_value, self._field_type)    





@dataclass
class MyClass(Validator):
    '''
    myfield: Union[]
        Проверка ебаная
    '''
    myfield : Union[Iterable[int], int] 
    str_field : str
    int_field : int
    list_field : Iterable[str]
    

try:
    test = MyClass(myfield=[12, 'sas'], str_field='sas', int_field=12, list_field=[1, 'sas'])
    print(test)
except Exception as e:
    print(str(e))

