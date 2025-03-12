from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.number import NumberCreate, NumberUpdate, NumberResponse
from app.schemas.company_number import CompanyNumberCreate
from app.models.number import Number
from app.models.company_number import CompanyNumber
from app.models.company import Company
from app.auth.auth_dependency import get_current_user_id

router = APIRouter(prefix="/numbers", tags=["numbers"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 📌 Crear un número (con asociación opcional a una compañía)
@router.post("/", response_model=NumberResponse, status_code=status.HTTP_201_CREATED)
def create_number(
    number: NumberCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    db_number = db.query(Number).filter(Number.number == number.number).first()
    if db_number:
        raise HTTPException(status_code=400, detail="Number already exists")

    # Crear el número
    new_number = Number(**number.dict(exclude={"company_id"}))
    db.add(new_number)
    db.commit()
    db.refresh(new_number)

    # Asociar a la compañía si se envió el `company_id`
    if number.company_id:
        db_company = db.query(Company).filter(Company.id == number.company_id).first()
        if not db_company:
            raise HTTPException(status_code=404, detail="Company not found")

        new_association = CompanyNumber(company_id=number.company_id, number_id=new_number.id)
        db.add(new_association)
        db.commit()

    return new_number

# 📌 Obtener todos los números
@router.get("/", response_model=list[NumberResponse])
def get_numbers(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    return db.query(Number).all()

# 📌 Asociar un número existente a una compañía existente
@router.post("/associate", status_code=status.HTTP_201_CREATED)
def associate_number_to_company(
    association: CompanyNumberCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # Verificar número
    db_number = db.query(Number).filter(Number.id == association.number_id).first()
    if not db_number:
        raise HTTPException(status_code=404, detail="Number not found")

    # Verificar compañía
    db_company = db.query(Company).filter(Company.id == association.company_id).first()
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Verificar si ya están asociados
    existing_association = db.query(CompanyNumber).filter(
        CompanyNumber.number_id == association.number_id,
        CompanyNumber.company_id == association.company_id
    ).first()

    if existing_association:
        raise HTTPException(status_code=400, detail="Number already associated with this company")

    # Crear asociación
    new_association = CompanyNumber(**association.dict())
    db.add(new_association)
    db.commit()

    return {"message": "Number successfully associated with the company"}

# 📌 Buscar número por valor
@router.get("/search", response_model=NumberResponse)
def search_number_by_value(
    number: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    db_number = db.query(Number).filter(Number.number == number).first()
    if not db_number:
        raise HTTPException(status_code=404, detail="Number not found")
    return db_number
