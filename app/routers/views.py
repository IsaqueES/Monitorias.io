from fastapi import APIRouter, Request, Query, Form, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.core.database import supabase
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Pega a senha do arquivo .env ou usa um padrão
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "minhasenha123")

# ==========================================
# ROTAS PÚBLICAS E DE USUÁRIO
# ==========================================

@router.get("/")
async def root():
    """Redireciona a raiz para a home"""
    return RedirectResponse(url="/home")

@router.get("/login")
async def login_page(request: Request):
    """Exibe a página de login/registro"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/home")
async def home(request: Request, user_id: str = Query(None)):
    """Página inicial com as matérias"""
    # 1. Busca todas as matérias
    res = supabase.table("subjects").select("*").execute()
    subjects = res.data
    
    # 2. Se tiver ID de usuário, busca os dados dele
    user_data = None
    if user_id:
        u_res = supabase.table("users").select("*").eq("id", user_id).execute()
        if u_res.data:
            user_data = u_res.data[0]

    return templates.TemplateResponse("home.html", {
        "request": request, 
        "subjects": subjects, 
        "user": user_data
    })

@router.get("/about")
async def about(request: Request, user_id: str = Query(None)):
    """Página Sobre"""
    user_data = None
    if user_id:
        u_res = supabase.table("users").select("*").eq("id", user_id).execute()
        if u_res.data: user_data = u_res.data[0]

    return templates.TemplateResponse("about.html", {
        "request": request,
        "user": user_data,
        "stats": "+100mil alunos ajudados"
    })

@router.get("/user/id={id}")
async def user_profile(request: Request, id: str):
    """Perfil do usuário com suas inscrições"""
    # Busca dados do usuário
    u_res = supabase.table("users").select("*").eq("id", id).execute()
    user_data = u_res.data[0] if u_res.data else None
    
    # Busca monitorias inscritas (com join em monitorias e matérias)
    enroll_res = supabase.table("enrollments").select(
        "*, monitorings(*, subjects(name))"
    ).eq("user_id", id).execute()
    
    enrolled_monitorings = enroll_res.data

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user_data,
        "monitorings": enrolled_monitorings
    })

@router.post("/user/unsubscribe")
async def unsubscribe(user_id: str = Form(...), monitoring_id: str = Form(...)):
    """Ação de desinscrever-se"""
    supabase.table("enrollments").delete().eq("user_id", user_id).eq("monitoring_id", monitoring_id).execute()
    return RedirectResponse(url=f"/user/id={user_id}", status_code=303)

@router.get("/monitoria/id={id_materia}")
async def monitoria_list(request: Request, id_materia: str, q: str = Query(None), user_id: str = Query(None)):
    """Lista de monitorias de uma matéria específica"""
    # Prepara a query básica
    query = supabase.table("monitorings").select("*").eq("subject_id", id_materia)
    
    # Se tiver busca, filtra pelo nome do monitor
    if q:
        query = query.ilike("monitor_name", f"%{q}%")
    
    res = query.execute()
    monitorings = res.data
    
    # Busca o nome da matéria para exibir no título
    subj_res = supabase.table("subjects").select("name").eq("id", id_materia).execute()
    subject_name = subj_res.data[0]['name'] if subj_res.data else "Matéria"

    # Dados do usuário logado
    user_data = None
    if user_id:
        u_res = supabase.table("users").select("*").eq("id", user_id).execute()
        if u_res.data: user_data = u_res.data[0]

    return templates.TemplateResponse("monitoria.html", {
        "request": request,
        "monitorings": monitorings,
        "subject_name": subject_name,
        "user": user_data,
        "user_id": user_id 
    })

# No final do arquivo views.py

@router.post("/monitoria/subscribe")
async def subscribe(user_id: str = Form(...), monitoring_id: str = Form(...), subject_id: str = Form(...)):
    """Ação de inscrever-se com feedback de sucesso"""
    try:
        supabase.table("enrollments").insert({
            "user_id": user_id,
            "monitoring_id": monitoring_id
        }).execute()
        
        # SUCESSO: Adiciona &status=success na URL
        return RedirectResponse(
            url=f"/monitoria/id={subject_id}?user_id={user_id}&status=success", 
            status_code=303
        )
    except:
        # ERRO (ou já inscrito): Adiciona &status=error
        return RedirectResponse(
            url=f"/monitoria/id={subject_id}?user_id={user_id}&status=error", 
            status_code=303
        )
# ==========================================
# ROTAS DO ADMIN (PROTEGIDAS)
# ==========================================

@router.get("/admin/login")
async def admin_login_page(request: Request):
    """Exibe a tela de login do admin"""
    return templates.TemplateResponse("admin_login.html", {"request": request})

@router.post("/admin/login")
async def admin_login_action(request: Request, password: str = Form(...)):
    """Verifica a senha e define o cookie de autorização"""
    if password == ADMIN_SECRET:
        response = RedirectResponse(url="/admin", status_code=303)
        # Define um cookie que dura 60 minutos (3600 segundos)
        response.set_cookie(key="admin_token", value="authorized", max_age=3600)
        return response
    else:
        # Se errou, volta para o login com erro
        return templates.TemplateResponse("admin_login.html", {
            "request": request, 
            "error": "Senha incorreta!"
        })

@router.get("/admin/logout")
async def admin_logout():
    """Remove o cookie e sai do admin"""
    response = RedirectResponse(url="/home", status_code=303)
    response.delete_cookie("admin_token")
    return response


@router.get("/admin")
async def admin_dashboard(request: Request):
    """Rota protegida: Só entra se tiver o cookie"""
    token = request.cookies.get("admin_token")
    
    # SE NÃO TIVER COOKIE, BLOQUEIA
    if token != "authorized":
        return RedirectResponse(url="/admin/login")
    
    # SE TIVER COOKIE, MOSTRA O PAINEL
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "admin_secret": ADMIN_SECRET 
    })