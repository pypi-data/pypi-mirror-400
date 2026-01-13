ENV_PATH = '/home/solcatcher/.env'
CRED_VALUES = {
    "postgres":{
        "prefix":'SOLCATCHER_POSTGRESQL',"defaults":{
        "host":'localhost',
        "port":'5432',
        "user":'solcatcher',
        "name":'solcatcher',
        "password":'solcatcher123!!!456'
    }
        },
    "ampq":{
        "prefix":'SOLCATCHER_AMQP',
        "defaults":{
            "host":'localhost',
            "port":'5672',
            "user":'solcatcher',
            "name":'solcatcher',
            "pass":'solcatcher123'
            }
        }
    }
