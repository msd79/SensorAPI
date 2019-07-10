class DB():
    
    def __init__(self, dbmodule):
        self.user = 'pi'
        self.password = 'raspberry'
        self.dbname = 'sensortagdb'
        self.dbmodule = dbmodule

    def generateQueryString(self, timestamp ,data, comment):
        return "insert into ambienttemp(timestamp ,data,comment) values ('%s', '%s', '%s')"%(timestamp, data, comment)


    def insert(self, query):
        connect = self.dbmodule.connect(user=self.user, password=self.password, database= self.dbname)
        cursor = connect.cursor()
        try:
          cursor.execute(query)
          connect.commit()
        except:
            return "Error"
        finally:            
            connect.close()
        return "Success"
    
    def select(self, query):
        connect = self.dbmodule.connect(user=self.user, password=self.password, database= self.dbname)
        cursor = connect.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        connect.close()
        return rows
