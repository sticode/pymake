import pickle
import os

db_type = { 'MySQL' : False, 'SQLite' : False }

try:
    import MySQLdb as mysql
    db_type['MySQL'] = True
except:
    db_type['MySQL'] = False

try:
    import sqlite3
    db_type['SQLite'] = True
except:
    db_type['SQLite'] = False
    
    
class db_settings:
    
    def __init__(self):
        self.user = ''
        self.key = ''
        self.host = 'localhost'
        self.schema = ''
        self.type = None
    
def save_settings(settings, file = 'db.conf'):
    
    fp = open(file, 'w')
    
    pickle.dump(settings, fp)
    
    fp.close()
    
def load_settings(file = 'db.conf'):
    
    if os.path.exists(file):
        
        fp = open(file, 'r')
        
        settings = pickle.load(fp)
        
        fp.close()
        
        return settings
    else:
        return db_settings()

    

class connector:
    (MySQL, SQLite) = (0 , 1)
    
    def __init__(self, host = 'localhost', user = 'root', key = '', schema = ''):
        self.host = host
        self.user = user
        self.key = key
        self.schema = schema
        self.type = None

class project:
    
    def __init__(self, name):
        self.name = name
        self.id = 0
        
class build:
    
    def __init__(self, name, state):
        self.name = name
        self.state = state
        self.id = 0
        self.project_id = 0

class mysql_connector(connector):
    
    def __init__(self, settings):
        connector.__init__(self, settings.host, settings.user, settings.password, settings.schema)
        self.type = MySQL

class sqlite_connector(connector):
    
    def __init__(self, settigns):
        connector.__init__(self)
        self.schema = settings.schema
        self.type = SQLite
    
    def connect(self):
        return sqlite3.connect(self.schema)
    

def create_connector(settings):
    
    if settings.type == 'MySQL':
        return mysql_connector(settings)
    elif settings.type == 'SQLite':
        return sqlite_connector(settings)
    else:
        return None
