
#controllers/firebase.py
import os
import requests
import json
import logging
import traceback

from dotenv import load_dotenv
from fastapi import HTTPException, Depends


import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from utils.database import fetch_query_as_json, get_db_connection
from utils.security import create_jwt_token
import requests
from models.UserLogin import UserRegister
from models.Prueba import UserLogin
#Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


# Inicializar la app de Firebase Admin
cred = credentials.Certificate("secrets/admin-firebasesdk.json")
firebase_admin.initialize_app(cred)


async def register_user_firebase(user: UserRegister):
    try:
        user_record = firebase_auth.create_user(
            email=user.email,
            password=user.password
        )

        conn = await get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "EXEC contasoft.insertar_usuario @id_rol = ?, @universidad_id = ?, @primer_nombre = ?, @segundo_nombre = ?, @primer_apellido = ?, @segundo_apellido = ?, @email = ?, @telefono = ?",
                user.id_rol,
                user.universidad_id,
                user.primer_nombre,
                user.segundo_nombre,
                user.primer_apellido,
                user.segundo_apellido,
                user.email,
                user.telefono
            )
            conn.commit()
            return {
                "success": True,
                "message": "Usuario registrado exitosamente"
            }
        except Exception as e:
            firebase_auth.delete_user(user_record.uid)
            conn.rollback()
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error al registrar usuario: {e}"
        )


async def login_user_firebase(user: UserLogin):
    try:
       
        logger.info(f"Iniciando proceso de login para el usuario: {user.email}")
       
        api_key = os.getenv("FIREBASE_API_KEY") 
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        payload = {
            "email": user.email,
            "password": user.password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        response_data = response.json()

        if "error" in response_data:
            raise HTTPException(
                status_code=400,
                detail=f"Error al autenticar usuario: {response_data['error']['message']}"
            )

        query = f"""SELECT 
                        email, 
                        primer_nombre,
                        primer_apellido,
                        active 
                        FROM contasoft.Usuarios WHERE email = '{user.email}'"""
        try:
            logger.info(f"QUERY LIST")
            result_json = await fetch_query_as_json(query)
            result_dict = json.loads(result_json)
            return {
                "message": "Usuario autenticado exitosamente",
                "idToken": create_jwt_token(
                    result_dict[0]["primer_nombre"],
                    result_dict[0]["primer_apellido"],
                    user.email,
                    result_dict[0]["active"]
                )
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    except Exception as e:
        logger.error(f"Error en login_user_firebase: {str(e)}")
        logger.error(traceback.format_exc())
        error_detail = {
            "type": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        
        
        raise HTTPException(
            status_code=400,
            detail=f"Error al registrar usuario: {error_detail}"
        )