from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.orm import Session
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import requests
from app.database import SessionLocal
from app.models.number import Number
from app.models.message import Message
from app.schemas.message import MessageCreate
from app.auth.auth_dependency import get_current_user_id
from app.routers.sse_router import trigger_message_event

router = APIRouter(prefix="/webhook", tags=["webhook"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📌 Endpoint para procesar mensajes entrantes
@router.post("/", status_code=status.HTTP_200_OK)
async def webhook(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()

    # 🔹 Obtener el número al que se escribió y el mensaje del remitente
    to_number = form_data.get('To')
    from_number = form_data.get('WaId')  # El número del remitente solo se registra, no se busca
    message_body = form_data.get('Body')

    if not to_number or not from_number or not message_body:
        raise HTTPException(status_code=400, detail="Invalid data received")

    # 🔎 Eliminar el prefijo 'whatsapp:' del número al que se escribió
    if to_number.startswith("whatsapp:"):
        to_number = to_number.replace("whatsapp:", "")

    print(f"📩 Nuevo mensaje recibido de {from_number} hacia {to_number}: {message_body}")

    # 🔎 Buscar en la base de datos el número al que se escribió
    db_number = db.query(Number).filter(Number.number == to_number).first()
    if not db_number:
        raise HTTPException(status_code=404, detail="Destination number not registered in the system")

    agente_id = db_number.agente_id
    account_sid = db_number.account_sid
    auth_token = db_number.auth_token
    number_id = db_number.id
    agente_status = db_number.status

    # Registrar mensaje entrante en la base de datos
    incoming_message = Message(
            to=to_number,  
            from_=from_number,
            direction='incoming',
            message=message_body,  # <-- Guardar el mensaje recibido
            number_id=number_id
        )
    db.add(incoming_message)
    db.commit()
    await trigger_message_event(incoming_message.id)
    # Consultar el endpoint del agente correspondiente
    if agente_status == 'active':
        endpoint_url = f"http://rypsystems.cl/builder/agents/{agente_id}/ask"
        payload = {"question": message_body}
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "insomnia/10.3.1"
        }

        try:
            response = requests.post(endpoint_url, json=payload, headers=headers)
            if response.status_code == 200:
                response_data = response.json()
                respuesta_final = response_data.get('answer', 'No se recibió una respuesta válida del servicio.')
            else:
                respuesta_final = "❌ Error al consultar el servicio externo."
        except Exception as e:
            respuesta_final = f"❌ Error de conexión: {str(e)}"
    else:
        respuesta_final ="Un humano te contactara!"
    
    outgoing_message = Message(
        to=from_number,
        from_=to_number,  # Indica que el mensaje fue enviado por el sistema
        direction='outgoing',
        message=respuesta_final,  # <-- Guardar el mensaje de respuesta
        number_id=number_id
    )
    db.add(outgoing_message)
    db.commit()

    # Enviar la respuesta utilizando el cliente de Twilio
    try:
        if account_sid and auth_token:
            client = Client(account_sid, auth_token)
            client.messages.create(
                body=f"🤖 Respuesta del asistente: {respuesta_final}",
                from_=f"whatsapp:{to_number}",
                to=f"whatsapp:{from_number}"
            )
        else:
            print("❗ Advertencia: Credenciales de Twilio no disponibles en la base de datos.")
    except Exception as e:
        print(f"❌ Error al enviar el mensaje por Twilio: {str(e)}")

    # Respuesta final para el webhook
    twilio_response = MessagingResponse()
    twilio_response.message(f"🤖 Respuesta del asistente: {respuesta_final}")

    return str(twilio_response)
