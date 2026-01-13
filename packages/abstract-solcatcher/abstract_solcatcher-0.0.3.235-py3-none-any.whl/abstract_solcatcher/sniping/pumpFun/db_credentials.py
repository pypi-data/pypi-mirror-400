from abstract_security import *
def get_dbConfig_keys():
  return ["dbname","user","password","host","port"]
def get_rabbitmq_keys():
  return ["user","password","host","queue"]
def get_db_env_key(key,dbProgram=None,dbType=None):
  dbProgram=dbProgram or 'solcatcher'
  dbType=dbType or 'database'
  return f"{dbProgram.upper()}_{dbType.upper()}_{key.upper()}"
def get_db_env_value(key,env_path=None):
  return get_env_value(key=key,path=env_path)
def get_env_data(keys,dbProgram=None,dbType=None,env_path=None):
  dbProgram=dbProgram or 'solcatcher'
  dbType=dbType or 'database'
  db_js = {}
  for key in keys:
    db_env_key = get_db_env_key(key=key,dbProgram=dbProgram,dbType=dbType)
    db_js[key]= get_db_env_value(key=db_env_key,env_path=env_path)
  return db_js
def get_db_url(**kwargs):
  DB_CONFIG = kwargs or get_db_config()
  return f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
def get_db_config():
  return get_env_data(get_dbConfig_keys(),dbProgram='solcatcher',dbType='database')
DB_CONFIG = get_db_config()
RABBIT_CONFIG = get_env_data(get_rabbitmq_keys(),dbProgram='solcatcher',dbType='rabbitmq')
