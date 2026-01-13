from agno.db.mysql import MySQLDb
from agno.tracing import setup_tracing
from agno.db.sqlite import SqliteDb

db = SqliteDb(db_file="tmp/agents.db")

# Setup your Database
mysql_db = MySQLDb(db_url="mysql+pymysql://vc_agent:aihuashen%402024@rm-2ze0q808gqplb1tz72o.mysql.rds.aliyuncs.com:3306/digital-life2")


# setup_tracing(db=mysql_db) # Call this once at startup #TODO 003