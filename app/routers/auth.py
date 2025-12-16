from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import RedirectResponse
from app.core.database import supabase

router = APIRouter()

@router.post("/register")
async def register(name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    res = supabase.table("users").insert({
        "name": name, 
        "email": email, 
        "password": password
    }).execute()
    
    if not res.data:
        raise HTTPException(status_code=400, detail="Erro ao registrar")
    
    return RedirectResponse(url="/login", status_code=303)

@router.post("/login")
async def login(response: Request, email: str = Form(...), password: str = Form(...)):
    res = supabase.table("users").select("*").eq("email", email).eq("password", password).execute()
    
    if not res.data:
        return RedirectResponse(url="/login?error=invalid", status_code=303)
    
    user_id = res.data[0]['id']
    redirect_url = f"/home?user_id={user_id}" 
    return RedirectResponse(url=redirect_url, status_code=303)