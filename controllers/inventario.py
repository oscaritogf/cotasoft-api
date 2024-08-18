import json
import logging
import pyodbc
from dotenv import load_dotenv
from fastapi import HTTPException, Depends


import firebase_admin

from utils.database import fetch_query_as_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_inventario_count():
    query = f"EXEC contasoft.contar_elementos_inventario"
    
    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query)
        return json.loads(result_json)
    except Exception as e:
        logger.error(f"Error al obtener la cantidad de inventario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
    
async def fetch_prestamo_count():
    query = f"EXEC contasoft.contar_elementos_prestados"

    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query)
        return json.loads(result_json)
    except Exception as e:
        logger.error(f"error al traer los objetos prestados: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al traer los objetos")

async def fetch_entrega_tarde_count():
    query = f"EXEC contasoft.contar_listar_usuarios_entregas_tardias"

    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query)
        return json.loads(result_json)
    except Exception as e:
        logger.error(f"error al traer los objetos prestados: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al traer los objetos")

async def fetch_usuario_entregas_tarde():
    query = f"EXEC contasoft.usuarios_con_entregas_tardias"

    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query)
        return json.loads(result_json)
    except Exception as e:
        logger.error(f"error al traer los objetos prestados: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al traer los objetos")



async def fetch_categorias():
    query = f"SELECT * FROM contasoft.Categoria ORDER BY nombre"
    try:
        logger.info(f"QUERY LIST")
        result = await fetch_query_as_json(query)
        return json.loads(result)
    except HTTPException as e:
        logger.error(f"eroro al traer los datos : {str(e)}")
        raise HTTPException(status_code=500, detail=f"error al traer las categorias")
    

async def fetch_proveedores():
    query = "SELECT * FROM contasoft.Proveedor ORDER BY nombre"
    try:
        logger.info(f"QUERY LIST")
        result = await fetch_query_as_json(query)
        return json.loads(result)
    except HTTPException as e:
        logger.error(f"eroro al traer los datos : {str(e)}")
        raise HTTPException(status_code=500, detail=f"error al traer los proveedores")
    



#trae todo el inventario
async def fetch_inventarios():
    query = f"EXEC contasoft.obtener_inventario_completo"
    try:
        logger.info("Ejecutando consulta de inventario")
        result_json = await fetch_query_as_json(query)
        result = json.loads(result_json)
    except Exception as e:
        logger.error(f"Error al obtener el total inventario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

    if not result:  # Si la lista está vacía
        raise HTTPException(status_code=404, detail="Inventario no encontrado")

    return result
    

#inventario por id
async def fetch_inventario(id_inventario: int):
    query = f"SELECT * FROM contasoft.Inventario WHERE id_inventario = {id_inventario}"
    result_dict = []
    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query)
        result_dict = json.loads(result_json)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if len(result_dict) == 0:
            raise HTTPException(status_code=404, detail="not found")

    return result_dict[0]


async def fetch_update_inventario(id_inventario: int, inventario_data: dict):
    query = """
    EXEC contasoft.actualizar_inventario 
    @id_inventario = ?, 
    @id_proveedor = ?, 
    @id_categoria = ?, 
    @nombre = ?, 
    @cantidad = ?, 
    @precio = ?, 
    @observacion = ?
    """
    
    params = (
        id_inventario,
        inventario_data['id_proveedor'],
        inventario_data['id_categoria'],
        inventario_data['nombre'],
        inventario_data['cantidad'],
        inventario_data['precio'],
        inventario_data['observacion']
    )

    try:
        logger.info(f"Actualizando inventario con ID: {id_inventario}")
        logger.info(f"Parámetros: {params}")
        
        result_json = await fetch_query_as_json(query, params, is_procedure=True)
        logger.info(f"Resultado JSON: {result_json}")
        
        result = json.loads(result_json)
        
        if not result or len(result) == 0:
            raise HTTPException(status_code=500, detail="No se recibió respuesta de la base de datos")
        
        result = result[0]  # Asumiendo que el procedimiento devuelve una fila
        
        if result['status'] != 200:
            raise HTTPException(status_code=result['status'], detail=result['message'])
        
        if result['rows_affected'] == 0:
            raise HTTPException(status_code=404, detail="No se encontró el inventario o no se realizaron cambios")
        
        logger.info(f"Inventario actualizado exitosamente: {result['rows_affected']} fila(s) afectada(s)")
        return {"message": result['message'], "rows_affected": result['rows_affected']}

    except json.JSONDecodeError as e:
        logger.error(f"Error al decodificar JSON: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar la respuesta de la base de datos: {str(e)}")
    except pyodbc.Error as e:
        logger.error(f"Error de base de datos al actualizar el inventario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {str(e)}")
    except Exception as e:
        logger.error(f"Error al actualizar el inventario: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
    







async def fetch_create_inventario(inventario_data: dict):
    query = """
    EXEC contasoft.create_inventario
        @id_proveedor = ?,
        @id_categoria = ?,
        @nombre = ?,
        @cantidad = ?,
        @precio = ?,
        @observacion = ?
    """
    
    params = (
        inventario_data['id_proveedor'],
        inventario_data['id_categoria'],
        inventario_data['nombre'],
        inventario_data['cantidad'],
        inventario_data['precio'],
        inventario_data['observacion']
    )
    
    try:
        logger.info("Creando nuevo inventario")
        result = await fetch_query_as_json(query, params=params, is_procedure=True)
        result_dict = json.loads(result)[0]
        return {"message": "Inventario creado exitosamente", "id": result_dict.get("id")}
    except Exception as e:
        logger.error(f"Error al crear el inventario: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

    