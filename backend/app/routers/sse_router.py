import time
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
from app.database import SessionLocal
from app.models.message import Message
from app.utils.logger import logger

router = APIRouter(prefix="/sse", tags=["sse"])

# Almacén de eventos organizado por número
event_streams = {}
KEEP_ALIVE_INTERVAL = 10  # 🔥 Keep-Alive cada 10 segundos para evitar cortes

# Función para enviar eventos a clientes específicos
async def notify_clients(phone_number, message_data):
    try:
        logger.info(f"🔔 [NOTIFY] Enviando mensaje a: {phone_number}")
        
        if phone_number in event_streams:
            for queue in event_streams[phone_number]:
                await queue.put(message_data)
            logger.info(f"✅ [NOTIFY] Mensaje enviado a la cola de eventos para el número {phone_number}")
        else:
            logger.warning(f"❌ [NOTIFY] No hay suscriptores para el número {phone_number}")

        # 🔥 Notificar a los que escuchan **TODOS** los mensajes (para administradores)
        if "all" in event_streams:
            for queue in event_streams["all"]:
                await queue.put(message_data)
            logger.info("✅ [NOTIFY] Mensaje enviado a los suscriptores de 'all'.")
    except Exception as e:
        logger.error(f"❌ [NOTIFY] Error al enviar mensaje: {str(e)}")

# Endpoint SSE para que el frontend se suscriba
@router.get("/events/{phone_number}")
async def sse_events(phone_number: str, request: Request):
    try:
        logger.info(f"📡 [SSE] Se intentó suscribir al número: {phone_number}")

        phone_number = f"+{phone_number.strip()}"
        logger.info(f"📡 [SSE] Número corregido para la suscripción: {phone_number}")

        queue = asyncio.Queue()

        if phone_number not in event_streams:
            logger.info(f"➕ [SSE] Creando nueva cola para el número: {phone_number}")
            event_streams[phone_number] = []
        else:
            logger.info(f"✅ [SSE] Cola existente encontrada para el número: {phone_number}")

        event_streams[phone_number].append(queue)
        logger.info(f"✅ [SSE] Suscripción exitosa para el número: {phone_number}")

        async def event_generator(queue, phone_number):
            try:
                # 🔹 Mensaje inicial para confirmar la conexión
                yield "data: Conexión establecida correctamente\n\n"

                while True:
                    try:
                        # 🔹 Esperar por un mensaje en la cola, con timeout para mantener activo el flujo
                        data = await asyncio.wait_for(queue.get(), timeout=KEEP_ALIVE_INTERVAL)
                        logger.info(f"📩 [SSE] Enviando evento SSE: {data}")
                        yield f"data: {data}\n\n"
                    except asyncio.TimeoutError:
                        # 🔹 Enviar un mensaje de `keep-alive` si no hay actividad por X segundos
                        logger.info(f"🔄 [SSE] Enviando keep-alive para {phone_number}")
                        yield f"data: \n\n"

            except asyncio.CancelledError:
                logger.warning(f"❌ [SSE] La conexión SSE para {phone_number} fue cancelada.")
                event_streams[phone_number].remove(queue)
            except Exception as e:
                logger.error(f"❌ [SSE] Error inesperado en event_generator: {str(e)}")
                yield f"data: Error inesperado, se intentará reconectar...\n\n"

        return StreamingResponse(
            event_generator(queue, phone_number), 
            media_type="text/event-stream", 
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",  # 🔥 Evita que Nginx almacene en buffer el stream
                "Connection": "keep-alive",
                "Retry-After": "3"          # 🔄 Forzar retry cada 3 segundos si la conexión falla
            }
        )

    except Exception as e:
        logger.error(f"❌ [SSE] Error en la suscripción SSE: {str(e)}")
        raise HTTPException(status_code=500, detail="Error en la suscripción SSE")

# Función para disparar eventos cuando se recibe un mensaje
async def trigger_message_event(message_id: int):
    try:
        logger.info(f"🚨 [TRIGGER] Iniciando trigger de evento para mensaje ID: {message_id}")
        db = SessionLocal()
        try:
            message = db.query(Message).filter(Message.id == message_id).first()
            if message:
                phone_number = message.to
                logger.info(f"✅ [TRIGGER] Número encontrado en el mensaje: {phone_number}")

                message_data = {
                    "id": message.id,
                    "from": message.from_,
                    "to": message.to,
                    "message": message.message,
                    "created_at": str(message.created_at)
                }
                await notify_clients(phone_number, message_data)
            else:
                logger.warning(f"❌ [TRIGGER] No se encontró el mensaje con ID: {message_id}")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"❌ [TRIGGER] Error en trigger_message_event: {str(e)}")
