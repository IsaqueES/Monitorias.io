from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import auth, views, admin  # <--- 1. IMPORTANTE: Importar o admin aqui

app = FastAPI()

# Configuração de Arquivos Estáticos (CSS, Imagens)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Incluindo as Rotas
app.include_router(auth.router)
app.include_router(views.router)
app.include_router(admin.router)  # <--- 2. IMPORTANTE: Adicionar essa linha

# O servidor agora sabe que as rotas /api/... existem!
