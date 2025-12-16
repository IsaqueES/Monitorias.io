from fastapi import APIRouter, HTTPException
from app.core.database import supabase
from app.schemas.models import SubjectCreate, MonitoringCreate
import os

# Define que todas as rotas começam com /api
router = APIRouter(prefix="/api")

ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "minhasenha123")

# --- ROTAS DE LEITURA (PARA O DASHBOARD MOSTRAR OS DADOS) ---

@router.get("/subjects")
def list_subjects_json():
    """Busca todas as matérias e retorna JSON"""
    res = supabase.table("subjects").select("*").execute()
    return res.data

@router.get("/monitorings")
def list_monitorings_json():
    """Busca todas as monitorias e retorna JSON"""
    res = supabase.table("monitorings").select("*, subjects(name)").execute()
    return res.data

# --- ROTAS DE CRIAÇÃO ---

@router.post("/{secret}/subjects")
def create_subject(secret: str, subject: SubjectCreate):
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Senha incorreta")
    res = supabase.table("subjects").insert(subject.dict()).execute()
    return res.data

@router.post("/{secret}/monitorings")
def create_monitoring(secret: str, monitoring: MonitoringCreate):
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Senha incorreta")
    res = supabase.table("monitorings").insert(monitoring.dict()).execute()
    return res.data

# --- ROTAS DE DELETAR (PARA O BOTÃO DA LIXEIRA) ---

@router.delete("/{secret}/subjects/{subject_id}")
def delete_subject(secret: str, subject_id: str):
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Senha incorreta")
    
    # Tenta deletar
    res = supabase.table("subjects").delete().eq("id", subject_id).execute()
    return {"message": "Deletado"}

@router.delete("/{secret}/monitorings/{monitoring_id}")
def delete_monitoring(secret: str, monitoring_id: str):
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Senha incorreta")
    
    res = supabase.table("monitorings").delete().eq("id", monitoring_id).execute()
    return {"message": "Deletado"}

# ... (Mantenha os imports e rotas anteriores)

# ==========================
# ROTAS DE EDIÇÃO (UPDATE)
# ==========================

@router.put("/{secret}/subjects/{subject_id}")
def update_subject(secret: str, subject_id: str, subject: SubjectCreate):
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Senha incorreta")
    
    # Atualiza os dados no Supabase
    res = supabase.table("subjects").update(subject.dict()).eq("id", subject_id).execute()
    return res.data

@router.put("/{secret}/monitorings/{monitoring_id}")
def update_monitoring(secret: str, monitoring_id: str, monitoring: MonitoringCreate):
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Senha incorreta")
    
    res = supabase.table("monitorings").update(monitoring.dict()).eq("id", monitoring_id).execute()
    return res.data

@router.get("/enrollments")
def list_enrollments_json():
    """Busca inscrições trazendo dados do Aluno e da Monitoria"""
    # O select busca: dados da inscrição, nome/email do usuário, nome do monitor e matéria
    res = supabase.table("enrollments").select(
        "*, users(name, email), monitorings(monitor_name, subjects(name))"
    ).execute()
    return res.data

@router.delete("/{secret}/enrollments/{user_id}/{monitoring_id}")
def delete_enrollment(secret: str, user_id: str, monitoring_id: str):
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Senha incorreta")
    
    # Deleta usando os dois IDs para identificar a linha exata
    res = supabase.table("enrollments").delete().eq("user_id", user_id).eq("monitoring_id", monitoring_id).execute()
    return {"message": "Inscrição removida"}