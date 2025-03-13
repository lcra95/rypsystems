from fastapi import APIRouter, Request, HTTPException
import os
from app.utils.logger import logger  # Para depurar mejor

router = APIRouter(prefix="/webhook", tags=["instagram_webhook"])

# Token de verificación que definiste en Meta for Developers
VERIFICATION_TOKEN = ""

# 📌 Endpoint para manejar la verificación del webhook de Instagram
@router.get("/instagram")
async def verify_instagram_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    # Validar que el token sea correcto
    if mode == "subscribe" and token == VERIFICATION_TOKEN:
        logger.info(f"✅ [Instagram] Webhook verificado correctamente. {VERIFICATION_TOKEN}")
        return VERIFICATION_TOKEN  # ✅ Devuelve SOLO el challenge como texto plano
    else:
        logger.warning("❌ [Instagram] Error en la verificación del Webhook.")
        raise HTTPException(status_code=403, detail="Verificación fallida")

# 📌 Endpoint para recibir eventos en tiempo real desde Instagram
@router.post("/instagram")
async def handle_instagram_event(request: Request):
    data = await request.json()
    logger.info(f"📩 [Instagram] Evento recibido: {data}")
    return {"status": "Evento recibido"}
