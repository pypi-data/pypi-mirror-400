import warnings
from pydantic import BaseModel
from typing import Any, Generator, Self
from .model import MGIt, MGField, MGFunction, MGConfig as _MGConfig, MongoModel as _MongoModel
from pymongo import MongoClient

    
class MGConfig(_MGConfig):
    @classmethod
    def _getClient(cls):
        cls._client = MongoClient(cls.url)
        return cls._client[cls.db][cls.col]
    
    @classmethod
    def getConnect(cls):
        if not hasattr(cls, '_client'): cls._client=cls._getClient()
        return cls._client

class MongoModel(_MongoModel):
    class MGConfig(MGConfig):
        pass
    
    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        super().__pydantic_init_subclass__(**kwargs)
        # 自动注册子类字段
        for field_name, field_info in cls.model_fields.items():
            setattr(cls, field_name, field_info)
    
    @classmethod
    def mg_find(cls, *querys: dict, cig:dict=None, is_get_dt:bool=False)->Self|dict|None:
        result = cls.MGConfig.getConnect().find_one(MGFunction.and_(*querys), cig or {})
        return result and (result if cig or is_get_dt else cls(**result))
    
    @classmethod
    def mg_id_find(cls, *ids:str|object|Any, cig:dict=None, is_get_dt:bool=False)->Self|dict|None:
        result = cls.MGConfig.getConnect().find_one(cls.mgt_get_id_query(ids), cig or {})
        return result and (result if cig or is_get_dt else cls(**result))
    
    @classmethod
    def mg_find_all(cls, *querys: dict, cig:dict=None, is_get_dt:bool=False,
                        sort_map: dict[str, int]=None, skip:int=None, limit:int=None)->MGIt[Self|dict]:
        cursor  = cls.MGConfig.getConnect().find(MGFunction.and_(*querys),  cig if cig else {})
        if sort_map: cursor=cursor.sort(sort_map)
        if skip: cursor=cursor.skip(skip)
        if limit: cursor=cursor.limit(limit)
        return MGIt(cursor, cls, if_get_cls=not is_get_dt and not cig)
            
    @classmethod
    def mg_find_onekey_all(cls, key:str, *querys: dict, 
                              sort_map: dict[str, int]=None, skip:int=None, limit:int=None)->MGIt[Any]:
        cursor  = cls.MGConfig.getConnect().find(MGFunction.and_(*querys), {'_id':0, key:1})
        if sort_map: cursor=cursor.sort(sort_map)
        if skip: cursor=cursor.skip(skip)
        if limit: cursor=cursor.limit(limit)
        def temp():
            for dt in cursor:
                yield dt[key]
                
        return MGIt(temp(), cls)
    
    @classmethod
    def mg_find_onecol(cls, key:str, *querys: dict, default=None):
        dt = (cls.MGConfig.getConnect().find_one(MGFunction.and_(*querys), {'_id':0, key:1})) or {}
        return dt.get(key, default)
    
    @classmethod
    def mg_id_find_onecol(cls, key:str, *ids:str|object|Any, default=None):
        dt = (cls.MGConfig.getConnect().find_one(cls.mgt_get_id_query(ids), {'_id':0, key:1})) or {}
        return dt.get(key, default)
    
    @classmethod
    def mg_count(cls, *querys: dict)->int:
        return cls.MGConfig.getConnect().count_documents(MGFunction.and_(*querys))
     
    @classmethod       
    def mg_update_one(cls, act:dict[str, dict]|list[dict[str, dict]], *querys: dict, upsert=True)->dict:
        return cls.MGConfig.getConnect().update_one(MGFunction.and_(*querys), cls.mgt_merge_acts(act), upsert=upsert).raw_result
    
    @classmethod       
    def mg_id_update(cls, act:dict[str, dict]|list[dict[str, dict]], *ids:str|object|Any, upsert=True)->dict:
        return cls.MGConfig.getConnect().update_one(cls.mgt_get_id_query(ids), cls.mgt_merge_acts(act), upsert=upsert).raw_result
    
    @classmethod
    def mg_update(cls, act:dict[str, dict]|list[dict[str, dict]], *querys: dict)->dict:
        return (cls.MGConfig.getConnect().update_many(MGFunction.and_(*querys), cls.mgt_merge_acts(act))).raw_result
    
    @classmethod
    def mg_del_field(self, fields: list[str], *querys: dict)->dict:
        assert fields
        return self.MGConfig.getConnect().update_many(MGFunction.and_(*querys), {'$unset':{f:'' for f in fields}}).raw_result
    
    @classmethod
    def mg_pop(cls, *querys: dict)->Self|None:
        try:
            dt = (cls.MGConfig.getConnect().find_one_and_delete(MGFunction.and_(*querys))) or {}
            return cls(**dt)
        except Exception as e:
            return None
    
    @classmethod
    def mg_insert(cls, data:Self|dict)-> Self:
        data = cls(**data) if isinstance(data, dict) else data
        data.id_ = (cls.MGConfig.getConnect().insert_one(data if isinstance(data, dict) else data.model_dump())).inserted_id
        return data
    
    @classmethod
    def mg_insert_many(cls, datas: list[Self|dict]):
        if not datas: return None
        return cls.MGConfig.getConnect().insert_many([(data.model_dump() if isinstance(data, BaseModel) else data) for data in datas])
    
    @classmethod
    def mg_delete(cls, *querys: dict)->dict:
        return cls.MGConfig.getConnect().delete_many(MGFunction.and_(*querys)).raw_result
    
    @classmethod
    def mg_id_delete(cls, *ids: str|object|Any)->dict:
        return cls.MGConfig.getConnect().delete_many(cls.mgt_get_id_query(ids)).raw_result
    
    @classmethod
    def mg_aggregate(cls, data:list)->MGIt[dict]:
        return MGIt(cls.MGConfig.getConnect().aggregate(data), cls)
        
    def mg_self_sync(self):
        """同步数据库到对象"""
        kv = self.mgt_get_key_value()
        if isinstance(kv, str): return warnings.warn(f'{kv} is None')
        newer = self.mg_id_find(value)
        if newer:
            for key, value in newer.model_dump().items():
                if hasattr(self, key): setattr(self, key, value)
        else:
            warnings.warn(f'数据库中没有对应数据 - keys: {kv}')
    
    def mg_self_save(self, /, is_force_new=False, check_id=False, is_replace=True):
        """保存对象数据到数据库"""
        kv = self.mgt_get_key_value()
        if check_id and isinstance(kv, str): raise ValueError(f'{kv} is None')
        if is_force_new or kv=='_id':
            self.id_ = (self.MGConfig.getConnect().insert_one(self.model_dump())).inserted_id
        elif isinstance(kv, dict): 
            if is_replace:
                self.MGConfig.getConnect().replace_one(kv, self.model_dump(), upsert=True)
            else:
                self.MGConfig.getConnect().update_one(kv, {'$set': self.model_dump()}, upsert=True)
        else:
            raise ValueError(f'{kv} is None')
    
    def mg_self_delete(self)->dict:
        kv = self.mgt_get_key_value()
        if isinstance(kv, str): return warnings.warn(f'{kv} is None')
        result = (self.MGConfig.getConnect().delete_many(kv)).raw_result
        self.id_ = None
        return result
