from peewee import *

db = PostgresqlDatabase(database='image2list',
                        user='root',
                        password='root',
                        host='0.0.0.0',
                        port=5432)

class AccessToken(Model):
    user_id = CharField()
    access_token = CharField()
    refresh_token = CharField()
    expires_at = BigIntegerField()
    
    class Meta:
        database = db
    
db.connect()
db.create_tables([AccessToken])