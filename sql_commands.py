from sqlalchemy import create_engine
import config

engine = create_engine("mysql+pymysql://" + config.user_mysql + ":" + config.pass_mysql + "@" + config.host_mysql + "/" + config.db_mysql)

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