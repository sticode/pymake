import pickle
import os
import time
import math

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
    
def get_stamp():
    stamp = time.time()
    stamp = math.ceil(stamp)
    return stamp
    
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
    
    def connect(self):
        return

class project:
    
    def __init__(self, name = None):
        self.name = name
        self.stamp = 0
        self.id = 0
        self.workspace_id = 0
        
class build:
    
    def __init__(self, name = None, state = None):
        self.name = name
        self.state = state
        self.stamp = 0
        self.id = 0
        self.project_id = 0

class build_log:
    
    def __init__(self, build_id = 0):
        self.build_id = build_id
        self.id = 0
        self.log = ""
        self.stamp = 0
        

class mysql_connector(connector):
    
    def __init__(self, settings):
        connector.__init__(self, settings.host, settings.user, settings.key, settings.schema)
        self.type = connector.MySQL
        self.init_tables()
    
    def init_tables(self):
        tables = []
        tables.append("CREATE TABLE IF NOT EXISTS workspaces (workspace_id INTEGER NOT NULL AUTO_INCREMENT, workspace_name VARCHAR(255), stamp INTEGER NOT NULL, PRIMARY KEY(workspace_id) ) ")
        tables.append("CREATE TABLE IF NOT EXISTS projects ( project_id INTEGER NOT NULL AUTO_INCREMENT, workspace_id INTEGER NOT NULL, project_name VARCHAR(255), stamp INTEGER NOT NULL, PRIMARY KEY(project_id) )")
        tables.append("CREATE TABLE IF NOT EXISTS builds ( build_id INTEGER NOT NULL AUTO_INCREMENT, project_id INTEGER NOT NULL, build_name VARCHAR(255), state VARCHAR(255), stamp INTEGER NOT NULL, PRIMARY KEY(build_id) )")
        tables.append("CREATE TABLE IF NOT EXISTS build_logs (log_id INTEGER NOT NULL AUTO_INCREMENT, build_id INTEGER NOT NULL, logs TEXT, stamp INTEGER NOT NULL, PRIMARY KEY(log_id) ) ")

        con = self.connect()
        
        for t in tables:
            
            cursor = con.cursor()
            cursor.execute(t)
        
        self.close()
    
    def get_builds(self, project_id, build_name = None):
        builds = []
        con = self.con
        query = "SELECT build_id, project_id, build_name, state, stamp FROM builds WHERE project_id = %d ORDER BY build_id DESC" % (project_id)
        if build_name is not None:
            query = "SELECT build_id, project_id, build_name, state, stamp FROM builds WHERE project_id = %d AND build_name = '%s' ORDER BY build_id DESC" % (project_id, build_name)
    
        cursor = con.cursor()
        cursor.execute(query)
        
        for row in cursor:
            b = build()
            b.id = row[0]
            b.project_id = row[1]
            b.name = row[2]
            b.state = row[3]
            b.stamp = row[4]
            builds.append(b)
        
        return builds
    
    def get_build(self, project_id, build_name):
        con = self.con
        query = "SELECT build_id, project_id, build_name, state, stamp FROM builds WHERE project_id = %d AND build_name = '%s' ORDER BY build_id DESC" % (project_id, build_name)
        cursor = con.cursor()
        cursor.execute(query)
        
        row = cursor.fetchone()
        
        if row is not None:
            _build = build()
            _build.id = row[0]
            _build.project_id = row[1]
            _build.state = row[2]
            _build.stamp = row[3]
            return _build
        else:
            return None
    
    def insert_build(self, obuild):
        con = self.con
        obuild.stamp = get_stamp()
        query = "INSERT INTO builds (project_id, build_name, state, stamp) VALUES (%d, '%s', '%s', %d)" % (obuild.project_id, obuild.name, obuild.state, obuild.stamp)
        cursor = con.cursor()
        cursor.execute(query)
        
        con.commit()
        
        b2 = self.get_build(obuild.project_id, obuild.name)
        obuild.id = b2.id
    
    def insert_build_log(self, log):
        con = self.con
        log.stamp = get_stamp()
        
        query = "INSERT INTO build_logs ( build_id, logs, stamp ) VALUES (%d, '%s', '%d')" % (log.build_id, log.log, log.stamp)
        cursor = con.cursor()
        cursor.execute(query)
        con.commit()
    
    def update_build(self, obuild):
        con = self.con
        obuild.stamp = get_stamp()
        query = "UPDATE builds SET build_name = '%s', state = '%s', stamp = %d WHERE build_id = %d" % (obuild.name, obuild.state, obuild.stamp, obuild.id)
        cursor = con.cursor()
        cursor.execute(query)
        
        con.commit()
    
    def get_projects(self, workspace_id):
        projs = []
        con = self.con
        query = "SELECT project_id, project_name, workspace_id, stamp FROM projects WHERE workspace_id = %d" % (workspace_id)
        
        cursor = con.cursor()
        cursor.execute(query)
        
        for row in cursor:
            proj = project()
            proj.id = row[0]
            proj.name = row[1]
            proj.workspace_id = row[2]
            proj.stamp = row[3]
            projs.append(proj)
        
        return projs
    
    def get_project(self, project_name):
        
        con = self.con
        query = "SELECT project_id, project_name, workspace_id, stamp FROM projects WHERE project_name = '%s'" % (project_name)
        
        cursor = con.cursor()
        cursor.execute(query)
        
        row = cursor.fetchone()
        
        if row is not None:
            p = project()
            p.id = row[0]
            p.name = row[1]
            p.workspace_id = row[2]
            p.stamp = row[3]
            return p
        else:
            return None
    
    def insert_project(self, proj):
        
        proj.stamp = get_stamp()
        
        query = "INSERT INTO projects (project_name, workspace_id, stamp) VALUES ('%s', %d)" % (proj.name, proj.workspace_id, proj.stamp)
        
        con = self.con
        cursor = con.cursor()
        cursor.execute(query)
        con.commit()
        
        p2 = self.get_project(proj.name)
        
        proj.id = p2.id
        
    def update_project(self, proj):
        proj.stamp = get_stamp()
        
        query = "UPDATE projects SET project_name = '%s', workspace_id = %d, stamp = %d WHERE project_id = %d" % (proj.name, proj.workspace_id, proj.stamp, proj.id)
    
        cursor = self.con.cursor()
        cursor.execute(query)
        cursor.commit()
    
    def save_project(self, project):
        if project.id == 0:
            db_proj = self.get_project(project.name)
            if db_proj is not None:
                project.id = db_proj.id
            else:
                self.insert_project(project)
        else:
            self.update_project(project)
        
    def connect(self):
        self.con = mysql.connect(self.host, self.user, self.key, self.schema)
        return self.con
    
    def close(self):
        self.con.commit()
        self.con.close()
        

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
    
    
if __name__ == '__main__':
    
    settings = db_settings()
    settings.user = 'bytedump'
    settings.schema = 'bytedump'
    settings.type = 'MySQL'
    
    connect = create_connector(settings)
    
    connect.connect()
    
    builds = connect.get_builds(1)
    
    for b in builds:
        print b.id, b.name, b.state, b.stamp
    
    
    
    connect.close()
