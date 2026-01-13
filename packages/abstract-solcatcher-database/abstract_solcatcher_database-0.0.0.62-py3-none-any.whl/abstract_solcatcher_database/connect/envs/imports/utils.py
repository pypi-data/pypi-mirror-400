from abstract_utilities import get_env_value as get_env_value,eatAll
from .init_imports import *
from .constants import *
def get_env_val(key,path=None):
    path = path or ENV_PATH
    return get_env_value(key=key,path=path)
def if_list_get_single(obj):
    while True:
        if obj != None and isinstance(obj,list) and len(obj) == 1:
            obj = obj[0]
        else:
            break
    
    return obj

def get_credential_values(typ):
    return CRED_VALUES.get(typ)
def update_defaults(dict_obj,defaults_obj):
    if not defaults_obj:
        return dict_obj
    nuValue = {}
    for key,value in dict_obj.items():
        nuValue[key] = value or defaults_obj.get(key)
    return nuValue
def get_creds(prefix,path=None,defaults=None):
    defaults=defaults or {}
    prefix = prefix.upper()
    prefix = eatAll(prefix,['_'])
    cred_keys = ["host","port","user",{"dbname":["name","dbname"]},{"password":["password","pass"]}]
    creds_js = {}
    for key in cred_keys:
        if isinstance(key,dict):
            for key,values in key.items():
                for value in values:
                    temp_key = f"{prefix}_{value.upper()}"
                    temp_value = get_env_val(temp_key,path=path)
                    if temp_value:
                        creds_js[key] = temp_value
                        break
        else:
             
             temp_key = f"{prefix}_{key.upper()}"
             creds_js[key] = get_env_val(temp_key,path)
    return update_defaults(creds_js,defaults)
def create_db_url(prefix=None,user=None,host=None,dbname=None,port=None,password=None,**kwargs):
    prefix=prefix or 'postgres'
    if prefix == 'postgres':
        prefix = 'postgresql'
    return f"{prefix}://{user}:{password}@{host}:{port}/{dbname}"
def get_db_url(typ=None,path=None,prefix=None):
    typ= typ or 'postgres'
    creds = get_credentials(typ=typ,path=path,prefix=prefix)
    return create_db_url(prefix=typ,**creds)
def get_credentials(typ,path=None,prefix=None,defaults=None):
    values={}
    values["prefix"]=prefix
    values["defaults"]=defaults
    values = update_defaults(CRED_VALUES.get(typ),values)
    return get_creds(path=path,**values)

def getConnection(dbname=None,
            user=None,
            password=None,
            host=None,
            port=None):
    return psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
def getConnectionWithCreds(typ,path=None,prefix=None):
    creds = get_credentials(typ=typ,path=path,prefix=prefix)
    return getConnection(**creds)
def get_connection(typ=None,path=None,prefix=None):
    typ=typ or 'postgres'
    return getConnectionWithCreds(typ=typ,path=path,prefix=prefix)
