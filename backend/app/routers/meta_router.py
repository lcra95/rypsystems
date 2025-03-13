from fastapi import APIRouter, Request, HTTPException
import os
from app.utils.logger import logger

router = APIRouter(prefix="/webhook", tags=["meta_webhook"])

# Token de verificación que definiste en Meta for Developers
VERIFICATION_TOKEN = "e9c2ec1c256e455e434702446c0d2cdf35839a5e"

# 📌 Endpoint para manejar la verificación del webhook de Meta
@router.get("/facebook")
async def verify_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    # Validar que el token sea correcto
    if mode == "subscribe" and token == VERIFICATION_TOKEN:
        logger.info(f"✅ [Facebook] Webhook verificado correctamente. {challenge}")
        return challenge
    else:
        logger.warning("❌ [Facebook] Error en la verificación del Webhook.")
        raise HTTPException(status_code=403, detail="Verificación fallida")

# 📌 Endpoint para recibir eventos en tiempo real
@router.post("/facebook")
async def handle_facebook_event(request: Request):
    data = await request.json()
    logger.info(f"📩 [Facebook] Evento recibido: {data}")
    return {"status": "Evento recibido"}
