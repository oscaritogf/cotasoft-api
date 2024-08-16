# utils/database.py

from dotenv import load_dotenv
import os
import pyodbc
import logging
import json
from decimal import Decimal

load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

driver = os.getenv('SQL_DRIVER')
server = os.getenv('SQL_SERVER')
database = os.getenv('SQL_DATABASE')
username = os.getenv('SQL_USERNAME')
password = os.getenv('SQL_PASSWORD')

connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

async def get_db_connection():
    try:
        logger.info(f"Intentando conectar a la base de datos con la cadena de conexión: {connection_string}")
        conn = pyodbc.connect(connection_string, timeout=10)
        logger.info("Conexión exitosa a la base de datos.")
        return conn
    except pyodbc.Error as e:
        logger.error(f"Database connection error: {str(e)}")
        raise Exception(f"Database connection error: {str(e)}")


async def fetch_query_as_json(query, params=None, is_procedure=False):
    conn = await get_db_connection()
    cursor = conn.cursor()
    logger.info(f"Ejecutando query: {query}")
    try:
        if is_procedure:
            cursor.execute(query, params)
        else:
            cursor.execute(query, params) if params else cursor.execute(query)
        
        if cursor.description:  # Si hay resultados
            columns = [column[0] for column in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            json_result = json.dumps(results, cls=DecimalEncoder)
        else:  # Si no hay resultados (por ejemplo, en INSERT o UPDATE)
            json_result = json.dumps([{"rowcount": cursor.rowcount}])
        
        conn.commit()  # línea para confirmar la transacción
        return json_result

    except pyodbc.Error as e:
        conn.rollback()  
        raise Exception(f"Error ejecutando el query: {str(e)}")
    finally:
        cursor.close()
        conn.close()
