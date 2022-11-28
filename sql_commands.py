from sqlalchemy import create_engine
import creds

engine = create_engine("mysql+pymysql://" + creds.user_mysql + ":" + creds.pass_mysql + "@" + creds.host_mysql + "/" + creds.db_mysql)

#CREAR TABLA NUEVA
# sql = "CREATE TABLE keyword_volumes (execution_timestamp DATETIME, keyword VARCHAR(50), timeframe VARCHAR(20), datetime DATETIME, volume INTEGER)"
# engine.execute(sql)

#ELIMINAR TABLA
# sql = "DROP TABLE IF EXISTS weekly_keyword_searches"
# engine.execute(sql)

#SELECT
#sql = "SELECT DISTINCT execution_timestamp FROM keyword_volumes ORDER BY execution_timestamp DESC LIMIT 100"
sql = "SELECT COUNT(*) FROM gtrends.keyword_volumes"
result = engine.execute(sql)
for row in result:
    print(row)


#print(engine.table_names())