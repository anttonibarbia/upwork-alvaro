from sqlalchemy import create_engine
import creds

engine = create_engine("mysql+pymysql://" + creds.user_mysql + ":" + creds.pass_mysql + "@" + creds.host_mysql + "/" + creds.db_mysql)

#CREAR TABLA NUEVA
# sql = "CREATE TABLE keyword_volumes (execution_timestamp DATETIME, keyword VARCHAR(50), timeframe VARCHAR(20), datetime DATETIME, volume INTEGER)"
# engine.execute(sql)

#ELIMINAR TABLA
# sql = "DROP TABLE IF EXISTS weekly_keyword_searches"
# engine.execute(sql)

print(engine.table_names())