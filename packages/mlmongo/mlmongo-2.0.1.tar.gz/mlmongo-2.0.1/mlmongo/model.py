import typing
from warnings import warn
import annotated_types
from bson import ObjectId
from pydantic import AliasChoices, AliasPath, BaseModel, PydanticUserError
from pydantic.fields import FieldInfo
from pydantic.config import JsonDict
from typing import Any, Callable, Generic, Literal, overload, TypeVar
from pydantic_core import PydanticUndefined


T = TypeVar('T')

class AMGIt(Generic[T]):
    def __init__(self, ait, cls:T, if_get_cls=False):
        self._it = ait
        self.if_get_cls = if_get_cls
        self._cls = cls
        self._sem = cls.MGConfig.getSem()
    
    async def __anext__(self)->T|Any:
        async with self._sem:
            value = await self._it.__anext__()
        return self._cls(**value) if self.if_get_cls else value
    
    def __aiter__(self):
        return self
    
    async def to_list(self)->list[T|Any]:
        return [mes async for mes in self]
    
    async def first(self)->T|Any:
        return await self.__anext__()
    
    async def last(self)->T|Any:
        return (await self.to_list())[-1]

class MGIt(Generic[T]):
    def __init__(self, it, cls:T, if_get_cls=False):
        self._it = it
        self.if_get_cls = if_get_cls
        self._cls = cls
    
    def __next__(self)->T|Any:
        value = self._it.__next__()
        return self._cls(**value) if self.if_get_cls else value
    
    def __iter__(self):
        return self
    
    def to_list(self)->list[T|Any]:
        return [mes for mes in self]
    
    def first(self)->T|Any:
        return self.__next__()
    
    def last(self)->T|Any:
        return self.to_list()[-1]
    
class _MGFieldInfo(FieldInfo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fkey = None 
    
    def __set_name__(self, owner, name):
        self.fkey = self.alias if self.alias else name
    
    def __str__(self):
        assert self.fkey is not None, '_MGFieldInfo.fkey is None'
        return self.fkey
    
    # 查询动作
    def __gt__(self, value): return {self.fkey: {'$gt': value}}
    def __ge__(self, value): return {self.fkey: {'$gte': value}}
    def __lt__(self, value): return {self.fkey: {'$lt': value}}
    def __le__(self, value): return {self.fkey: {'$lte': value}}
    def __eq__(self, value): return {self.fkey: value}
    def __ne__(self, value): return {self.fkey: {'$ne': value}}
    def __mod__(self, value):  return {self.fkey: {'$regex': value}}
    def in_(self, ls:list): return {self.fkey: {'$in': ls}}
    def not_in_(self, ls:list): return {self.fkey: {'$nin': ls}}    

_Unset: Any = PydanticUndefined
@overload 
def MGField(
    default: Any,
    *,
    alias: str | None = _Unset,
    alias_priority: int | None = _Unset,
    validation_alias: str | AliasPath | AliasChoices | None = _Unset,
    serialization_alias: str | None = _Unset,
    title: str | None = _Unset,
    field_title_generator: Callable[[str, FieldInfo], str] | None = _Unset,
    description: str | None = _Unset,
    examples: list[Any] | None = _Unset,
    exclude: bool | None = _Unset,
    discriminator: str | None = _Unset,
    deprecated: str | bool | None = _Unset,
    json_schema_extra: JsonDict | Callable[[JsonDict], None] | None = _Unset,
    frozen: bool | None = _Unset,
    validate_default: bool | None = _Unset,
    repr: bool = _Unset,
    init: bool | None = _Unset,
    init_var: bool | None = _Unset,
    kw_only: bool | None = _Unset,
    pattern: str | typing.Pattern[str] | None = _Unset,
    strict: bool | None = _Unset,
    coerce_numbers_to_str: bool | None = _Unset,
    gt: annotated_types.SupportsGt | None = _Unset,
    ge: annotated_types.SupportsGe | None = _Unset,
    lt: annotated_types.SupportsLt | None = _Unset,
    le: annotated_types.SupportsLe | None = _Unset,
    multiple_of: float | None = _Unset,
    allow_inf_nan: bool | None = _Unset,
    max_digits: int | None = _Unset,
    decimal_places: int | None = _Unset,
    min_length: int | None = _Unset,
    max_length: int | None = _Unset,
    union_mode: Literal['smart', 'left_to_right'] = _Unset,
    fail_fast: bool | None = _Unset,
    **extra,
) -> Any: ...
@overload 
def MGField(
    default: Any,
    *,
    alias: str | None = _Unset,
    alias_priority: int | None = _Unset,
    validation_alias: str | AliasPath | AliasChoices | None = _Unset,
    serialization_alias: str | None = _Unset,
    title: str | None = _Unset,
    field_title_generator: Callable[[str, FieldInfo], str] | None = _Unset,
    description: str | None = _Unset,
    examples: list[Any] | None = _Unset,
    exclude: bool | None = _Unset,
    discriminator: str | None = _Unset,
    deprecated: str | bool | None = _Unset,
    json_schema_extra: JsonDict | Callable[[JsonDict], None] | None = _Unset,
    frozen: bool | None = _Unset,
    validate_default: bool | None = _Unset,
    repr: bool = _Unset,
    init: bool | None = _Unset,
    init_var: bool | None = _Unset,
    kw_only: bool | None = _Unset,
    pattern: str | typing.Pattern[str] | None = _Unset,
    strict: bool | None = _Unset,
    coerce_numbers_to_str: bool | None = _Unset,
    gt: annotated_types.SupportsGt | None = _Unset,
    ge: annotated_types.SupportsGe | None = _Unset,
    lt: annotated_types.SupportsLt | None = _Unset,
    le: annotated_types.SupportsLe | None = _Unset,
    multiple_of: float | None = _Unset,
    allow_inf_nan: bool | None = _Unset,
    max_digits: int | None = _Unset,
    decimal_places: int | None = _Unset,
    min_length: int | None = _Unset,
    max_length: int | None = _Unset,
    union_mode: Literal['smart', 'left_to_right'] = _Unset,
    fail_fast: bool | None = _Unset,
    **extra,
): ...
@overload
def MGField(
    *,
    default_factory: Callable[[], _MGFieldInfo] | Callable[[dict[str, Any]], _MGFieldInfo],
    alias: str | None = _Unset,
    alias_priority: int | None = _Unset,
    validation_alias: str | AliasPath | AliasChoices | None = _Unset,
    serialization_alias: str | None = _Unset,
    title: str | None = _Unset,
    field_title_generator: Callable[[str, FieldInfo], str] | None = _Unset,
    description: str | None = _Unset,
    examples: list[Any] | None = _Unset,
    exclude: bool | None = _Unset,
    discriminator: str | None = _Unset,
    deprecated: str | bool | None = _Unset,
    json_schema_extra: JsonDict | Callable[[JsonDict], None] | None = _Unset,
    frozen: bool | None = _Unset,
    validate_default: bool | None = _Unset,
    repr: bool = _Unset,
    init: bool | None = _Unset,
    init_var: bool | None = _Unset,
    kw_only: bool | None = _Unset,
    pattern: str | typing.Pattern[str] | None = _Unset,
    strict: bool | None = _Unset,
    coerce_numbers_to_str: bool | None = _Unset,
    gt: annotated_types.SupportsGt | None = _Unset,
    ge: annotated_types.SupportsGe | None = _Unset,
    lt: annotated_types.SupportsLt | None = _Unset,
    le: annotated_types.SupportsLe | None = _Unset,
    multiple_of: float | None = _Unset,
    allow_inf_nan: bool | None = _Unset,
    max_digits: int | None = _Unset,
    decimal_places: int | None = _Unset,
    min_length: int | None = _Unset,
    max_length: int | None = _Unset,
    union_mode: Literal['smart', 'left_to_right'] = _Unset,
    fail_fast: bool | None = _Unset,
    **extra,
): ...
@overload
def MGField(  # No default set
    *,
    alias: str | None = _Unset,
    alias_priority: int | None = _Unset,
    validation_alias: str | AliasPath | AliasChoices | None = _Unset,
    serialization_alias: str | None = _Unset,
    title: str | None = _Unset,
    field_title_generator: Callable[[str, FieldInfo], str] | None = _Unset,
    description: str | None = _Unset,
    examples: list[Any] | None = _Unset,
    exclude: bool | None = _Unset,
    discriminator: str | None = _Unset,
    deprecated: str | bool | None = _Unset,
    json_schema_extra: JsonDict | Callable[[JsonDict], None] | None = _Unset,
    frozen: bool | None = _Unset,
    validate_default: bool | None = _Unset,
    repr: bool = _Unset,
    init: bool | None = _Unset,
    init_var: bool | None = _Unset,
    kw_only: bool | None = _Unset,
    pattern: str | typing.Pattern[str] | None = _Unset,
    strict: bool | None = _Unset,
    coerce_numbers_to_str: bool | None = _Unset,
    gt: annotated_types.SupportsGt | None = _Unset,
    ge: annotated_types.SupportsGe | None = _Unset,
    lt: annotated_types.SupportsLt | None = _Unset,
    le: annotated_types.SupportsLe | None = _Unset,
    multiple_of: float | None = _Unset,
    allow_inf_nan: bool | None = _Unset,
    max_digits: int | None = _Unset,
    decimal_places: int | None = _Unset,
    min_length: int | None = _Unset,
    max_length: int | None = _Unset,
    union_mode: Literal['smart', 'left_to_right'] = _Unset,
    fail_fast: bool | None = _Unset,
    **extra,
) -> Any: ...
def MGField( 
    default: Any = PydanticUndefined,
    *,
    default_factory: Callable[[], Any] | Callable[[dict[str, Any]], Any] | None = _Unset,
    alias: str | None = _Unset,
    alias_priority: int | None = _Unset,
    validation_alias: str | AliasPath | AliasChoices | None = _Unset,
    serialization_alias: str | None = _Unset,
    title: str | None = _Unset,
    field_title_generator: Callable[[str, FieldInfo], str] | None = _Unset,
    description: str | None = _Unset,
    examples: list[Any] | None = _Unset,
    exclude: bool | None = _Unset,
    discriminator: str | None = _Unset,
    deprecated: str | bool | None = _Unset,
    json_schema_extra: JsonDict | Callable[[JsonDict], None] | None = _Unset,
    frozen: bool | None = _Unset,
    validate_default: bool | None = _Unset,
    repr: bool = _Unset,
    init: bool | None = _Unset,
    init_var: bool | None = _Unset,
    kw_only: bool | None = _Unset,
    pattern: str | typing.Pattern[str] | None = _Unset,
    strict: bool | None = _Unset,
    coerce_numbers_to_str: bool | None = _Unset,
    gt: annotated_types.SupportsGt | None = _Unset,
    ge: annotated_types.SupportsGe | None = _Unset,
    lt: annotated_types.SupportsLt | None = _Unset,
    le: annotated_types.SupportsLe | None = _Unset,
    multiple_of: float | None = _Unset,
    allow_inf_nan: bool | None = _Unset,
    max_digits: int | None = _Unset,
    decimal_places: int | None = _Unset,
    min_length: int | None = _Unset,
    max_length: int | None = _Unset,
    union_mode: Literal['smart', 'left_to_right'] = _Unset,
    fail_fast: bool | None = _Unset,
    **extra,
) -> Any:
    assert not extra.pop('const', None)
    min_items = extra.pop('min_items', None)  # type: ignore
    if min_items is not None:
        warn('`min_items` is deprecated and will be removed, use `min_length` instead', DeprecationWarning)
        if min_length in (None, _Unset):
            min_length = min_items  # type: ignore
    max_items = extra.pop('max_items', None)  # type: ignore
    if max_items is not None:
        warn('`max_items` is deprecated and will be removed, use `max_length` instead', DeprecationWarning)
        if max_length in (None, _Unset):
            max_length = max_items  # type: ignore
    unique_items = extra.pop('unique_items', None)  # type: ignore
    if unique_items is not None:
        raise PydanticUserError(
            (
                '`unique_items` is removed, use `Set` instead'
                '(this feature is discussed in https://github.com/pydantic/pydantic-core/issues/296)'
            ),
            code='removed-kwargs',
        )
    allow_mutation = extra.pop('allow_mutation', None)  # type: ignore
    if allow_mutation is not None:
        warn('`allow_mutation` is deprecated and will be removed. use `frozen` instead', DeprecationWarning)
        if allow_mutation is False:
            frozen = True
    regex = extra.pop('regex', None)  # type: ignore
    if regex is not None:
        raise PydanticUserError('`regex` is removed. use `pattern` instead', code='removed-kwargs')
    if extra:
        warn(
            'Using extra keyword arguments on `Field` is deprecated and will be removed.'
            ' Use `json_schema_extra` instead.'
            f' (Extra keys: {", ".join(k.__repr__() for k in extra.keys())})',
            DeprecationWarning,
        )
        if not json_schema_extra or json_schema_extra is _Unset:
            json_schema_extra = extra  # type: ignore
    if (
        validation_alias
        and validation_alias is not _Unset
        and not isinstance(validation_alias, (str, AliasChoices, AliasPath))
    ):
        raise TypeError('Invalid `validation_alias` type. it should be `str`, `AliasChoices`, or `AliasPath`')
    if serialization_alias in (_Unset, None) and isinstance(alias, str):
        serialization_alias = alias
    if validation_alias in (_Unset, None):
        validation_alias = alias
    include = extra.pop('include', None)  # type: ignore
    if include is not None:
        warn('`include` is deprecated and does nothing. It will be removed, use `exclude` instead', DeprecationWarning)
    return _MGFieldInfo(default=default,
                        default_factory=default_factory,
                        alias=alias,
                        alias_priority=alias_priority,
                        validation_alias=validation_alias,
                        serialization_alias=serialization_alias,
                        title=title,
                        field_title_generator=field_title_generator,
                        description=description,
                        examples=examples,
                        exclude=exclude,
                        discriminator=discriminator,
                        deprecated=deprecated,
                        json_schema_extra=json_schema_extra,
                        frozen=frozen,
                        pattern=pattern,
                        validate_default=validate_default,
                        repr=repr,
                        init=init,
                        init_var=init_var,
                        kw_only=kw_only,
                        coerce_numbers_to_str=coerce_numbers_to_str,
                        strict=strict,
                        gt=gt,
                        ge=ge,
                        lt=lt,
                        le=le,
                        multiple_of=multiple_of,
                        min_length=min_length,
                        max_length=max_length,
                        allow_inf_nan=allow_inf_nan,
                        max_digits=max_digits,
                        decimal_places=decimal_places,
                        union_mode=union_mode,
                        fail_fast=fail_fast,
                    )

class MGConfig:
    url:str
    db:str
    col:str
    default_ids:tuple[str] = ('_id',)
    
class MGFunction:
    @staticmethod
    def not_(query:dict)->dict:
        return {'$not': query}
    
    @staticmethod
    def or_(*querys:dict)->dict:
        assert querys, 'querys is empty'
        return {'$or': querys}
    
    @staticmethod
    def and_(*querys:dict)->dict:
        if querys:
            return {'$and': querys}
        else:
            return {}

    @staticmethod
    def data_set_(data:dict|BaseModel):
        return {'$set': data if isinstance(data, dict) else data.model_dump()}
    
    @staticmethod
    def set_(field:_MGFieldInfo|str, value): 
        return {'$set': {str(field) : value}}
    
    @staticmethod
    def unset_(field:_MGFieldInfo|str): 
        """删除字段"""
        return {'$unset': {str(field): 1}}
    
    @staticmethod
    def add_(field:_MGFieldInfo|str, value: float): 
        """加"""
        return {'$inc': {str(field): value}}
    
    @staticmethod
    def mul_(field:_MGFieldInfo|str, value: float): 
        """乘"""
        return {'$mul': {str(field): value}}
    
    @staticmethod
    def push_(field:_MGFieldInfo|str, value): 
        """向列表中添加元素"""
        return {'$push': {str(field): value}}
    
    @staticmethod
    def pull_(field:_MGFieldInfo|str, value): 
        """从列表中删除元素"""
        return {'$pull': {str(field): value}}
    
    @staticmethod
    def field_link_(other:'MongoModel', local_field:_MGFieldInfo|str, foreign_field:_MGFieldInfo|str, as_field:str='foreign_data'):
        return [{'$lookup': {
                        'from': other.MGConfig.col,
                        'localField': str(local_field),
                        'foreignField': str(foreign_field),
                        'as': as_field
                    }
                }]

class MongoModel(BaseModel):
    id_: object|None = MGField(default=None, exclude=True, alias='_id')
    
    class MGConfig(MGConfig):
        pass
    
    @property
    def _id(self)->str|None:
        return self.id_ and str(self.id_)
    
    @classmethod
    def mgt_get_id_query(cls, ids)->dict:
        assert len(cls.MGConfig.default_ids)==len(ids), 'ids数量与default_ids数量不一致'
        return {key: (ObjectId(value) if key=='_id' else value) for key, value in zip(cls.MGConfig.default_ids, ids)}
    
    def mgt_get_key_value(self)->dict|str:
        dt={}
        for key in self.MGConfig.default_ids:
            dt[key] = self.id_ if key=='_id' else getattr(self, key)
            if dt[key] is None: return key
        return dt
    
    @staticmethod
    def mgt_merge_acts(acts:list[dict[str, dict]]|dict)->dict[str, dict]:
        merged:dict[str, dict] = {}
        for act in ([acts] if isinstance(acts, dict) else acts): 
            for op, value in act.items():
                if op in merged:
                    # 如果操作符已存在，合并字段字典
                    merged[op].update(value)
                else:
                    # 如果操作符不存在，直接添加
                    merged[op] = value
        return merged