from fastapi import FastAPI, Request, Depends, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from utils.database import fetch_query_as_json
from models.UserLogin import UserRegister


from controllers.o365 import login_o365 , auth_callback_o365
from controllers.google import login_google , auth_callback_google
from controllers.firebase import register_user_firebase, login_user_firebase

from utils.security import validate
from models.Prueba import UserLogin
from models.Inventario import InventarioUpdate, InventarioCreate
from controllers.inventario import fetch_inventarios, fetch_inventario, fetch_update_inventario, fetch_inventario_count, fetch_prestamo_count, fetch_create_inventario, fetch_categorias, fetch_proveedores, fetch_entrega_tarde_count, fetch_usuario_entregas_tarde
from fastapi.middleware.cors import CORSMiddleware
import json


app = FastAPI()


# Configuración del middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

@app.get("/")
async def hello():
    return {
        "Hello": "World"
        , "version": "0.1.15"
    }
@app.get("/inventario/count")
async def inventarioCount(responce: Response):
    responce.headers["Cache-Control"] = "no-store"
    return await fetch_inventario_count()

@app.get('/prestamos/count')
async def prestamoCount(responce: Response):
    responce.headers["Cache-Control"] = "no-store"
    return await fetch_prestamo_count()

@app.get('/entrega/count')
async def entregaCount(responce: Response):
    responce.headers["Cache-Control"] = "no-store"
    return await fetch_entrega_tarde_count()

@app.get('/entrega/tarde')
async def entregaTarde(responce: Response):
    responce.headers["Cache-Control"] = "no-store"
    return await fetch_usuario_entregas_tarde()



@app.get('/categorias/nombre')
async def categorias(responce: Response):
    responce.headers["Cache-Control"] = "no-store"
    return await fetch_categorias()

@app.get('/proveedores/nombre')
async def proveedores(responce: Response):
    responce.headers["Cache-Control"] = "no-store"
    return await fetch_proveedores()

@app.get("/inventario")
async def inventario(responce: Response):
    responce.headers["Cache-Control"] = "no-store"
    return await fetch_inventarios()

@app.get("/inventario/{id_inventario}")
async def inventario(responce: Response, id_inventario: int):
    responce.headers["Cache-Control"] = "no-cache"
    return await fetch_inventario(id_inventario)

@app.put("/inventario/{id_inventario}")
async def inventario_update(response: Response, id_inventario: int, inventario: InventarioUpdate):
    response.headers["Cache-Control"] = "no-store"
    try:
        result = await fetch_update_inventario(id_inventario, inventario.dict())
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/inventario")
async def inventario_create(response: Response, inventario: InventarioCreate):
    response.headers["Cache-Control"] = "no-store"
    try:
        result = await fetch_create_inventario(inventario.dict())
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/login")
async def login():
    return await login_o365()

@app.get("/auth/callback")
async def authcallback(request: Request):
    return await auth_callback_o365(request)

@app.get("/login/google")
async def logingoogle():
      return await login_google()

@app.get("/auth/google/callback")
async def authcallbackgoogle(request: Request):
    return await auth_callback_google(request)

@app.post("/register")
async def register(user: UserRegister):
    return await register_user_firebase(user)


@app.post("/login/custom")
async def login_custom(user: UserLogin):
    return await login_user_firebase(user)

@app.get("/user")
@validate
async def user(request: Request):
    return {
        "email": request.state.email
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)