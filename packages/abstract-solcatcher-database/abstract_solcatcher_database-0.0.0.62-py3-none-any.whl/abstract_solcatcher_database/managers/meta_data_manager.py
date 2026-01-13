from abstract_utilities import get_any_value,SingletonMeta
import logging,os,json,requests
from abstract_pandas import pd
from abstract_apis import getRequest
from ..query_functions.call_functions.call_meta_data import get_meta_data
from ..utils.image_utils import *
from typing import *

metaDataLowerKeys = {
    'image': 'image',
    'uri': 'uri',
    'name':'name',
    'symbol': 'symbol',
    'twitter': 'twitter',
    'website': 'website',
    'description': 'description',
    'supply': 'supply',
    'mintauthority': 'mintAuthority',
    'freezeauthority': 'freezeAuthority',
    'ismutable': 'isMutable',
    'creators': 'creators',
    'updateauthority': 'updateAuthority',
    'createdon': 'createdOn',
    'primarysalehappened': 'createdOn',

}
metaDataTypeKeys = {
    'image': str,
    'uri': str,
    'name':str,
    'symbol': str,
    'twitter': str,
    'website': str,
    'description': str,
    'supply': int,
    'mintAuthority': str,
    'freezeAuthority': str,
    'isMutable': bool,
    'creators': str,
    'updateAuthority': str,
    'createdOn': int,
    'primarySaleHappened': bool,

}
metaDataCheckKeys = {
    'image': True,
    'uri': True,
    'name':True,
    'symbol': True,
    'twitter': True,
    'website': True,
    'description': True,
    'supply': True,
    'mintAuthority': True,
    'freezeAuthority': True,
    'isMutable': True,
    'creators': True,
    'updateAuthority': True,
    'createdOn': True,
    'primarySaleHappened': True,
    
}
metadata_check_bools = {
    'image': True,
    'uri': True,
    'name':True,
    'symbol': True,
    'twitter': True,
    'website': True,
    'description': True,
    'supply': False,
    'mintAuthority': False,
    'freezeAuthority': False,
    'isMutable': False,
    'creators': False,
    'updateAuthority': False,
    'createdOn': False,
    'primarySaleHappened': False,
    
}
def get_meta_data_value(key,dict_obj):
    value=None
    value = dict_obj.get(key)
    if value != None:
        return value
    key_lower = key.lower().replse(' ','_')
    keys = metaDataLowerKeys.get(key_lower)
    if keys:
        for key in make_list(keys):
            value = dict_obj.get(key)
            if value != None:
                return value
    return value
def getMetaChecks(values: Dict[str, Any]) -> Dict[str, Any]:
    """
    Constructs and returns a dictionary of metadata checks based on metaKeys.
    For certain keys (e.g. 'updateAuthority', 'freezeAuthority', 'mintAuthority'),
    the value is forced to False.
    """
    filter_checks = {}
    false_bools = ['updateAuthority', 'freezeAuthority', 'mintAuthority']
    for key in metaKeys:
        value = values.get(make_check_bool(key))
        if value:
            filter_checks[key] = value
            if key in false_bools:
                filter_checks[key] = False
    return filter_checks
metaKeys = list(metaDataTypeKeys.keys())

def make_insert(key):
    key = key.replace(' ', '_').upper()
    return f"-{key}-"
def make_insert_bool(key):
    key = key.replace(' ', '_').upper()
    return f"-{key}_BOOL-"
def make_check_bool(key):
    key = key.replace(' ', '_').upper()
    return f"-{key}_CHECK-"
def deKeyKey(key):
    return key.lower()[1:-1].replace('_',' ')
def getBool(key, value):
    return isinstance(value, metaDataTypeKeys.get(key))
class metaDataManager(metaclass=SingletonMeta):
    def __init__(self):
        self.allMetaData = {}
        self.metaDataCheckKeys=metaDataCheckKeys
        self.metaDataTypeKeys = metaDataTypeKeys
    def changeTally(self,event,values):
        lower_key = deKeyKey(event)
        regularMetakey = metaDataLowerKeys.get(lower_key)
        self.metaDataCheckKeys[regularMetakey] = values[event]
    def processMetaData(self,mint,imageData=True):
        if not self.allMetaData.get(mint):
            metaData = get_meta_data(mint=mint)
            self.get_meta_vars(metaData,imageData)
            self.allMetaData[mint] = {"processed":self.datas_js,'bools':self.bool_js}
        return self.allMetaData[mint]
    def filter_meta_data(self,mint,filterMetaChecks={}):
        metaData_js = self.processMetaData(mint)
        bools = metaData_js['bools']
        self.allMetaData[mint]['filtered']=True
        for key,check in self.metaDataCheckKeys.items():
            if check and not bools.get(key):
                self.allMetaData[mint]['filtered']=False
                break
        return self.allMetaData[mint]['filtered']
    def get_meta_vars(self,metaData,imageData=True):
        self.datas_js = {}
        self.bool_js = {}
        self.metaData = self.get_uri(metaData,imageData)
        for key in metaKeys:
            self.get_from_any_meta(key,metaData)
    def get_from_any_meta(self,key,metaData):
        values = get_any_value(metaData, key) or None
        value = values[0] if values and isinstance(values, list) else values
        self.bool_js[key] =getBool(key, value)
        self.datas_js[key] = value
        return value
    def get_uri(self,metaData,imageData=True):
        key = 'uri'
        self.get_from_any_meta(key,metaData)
        
        if self.bool_js[key] and imageData:
           try:
                metaData[0].update(get_image_vars(self.datas_js[key]) or {})
           except:
                pass
        return metaData
            

