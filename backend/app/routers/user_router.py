from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.auth.auth_dependency import get_current_user_id
from app.database import SessionLocal
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.models.user import User
from app.auth.password_utils import hash_password
from app.models.user_company import UserCompany
from app.models.company import Company

router = APIRouter(prefix="/users", tags=["users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/search", response_model=UserResponse)
def search_user_by_email(
    email: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.post("/associate", status_code=status.HTTP_201_CREATED)
def associate_user_to_company(
    user_id: int,
    company_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # Verificar que el usuario existe
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verificar que la compañía existe
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Verificar si ya están asociados
    existing_association = db.query(UserCompany).filter(
        UserCompany.user_id == user_id,
        UserCompany.company_id == company_id
    ).first()

    if existing_association:
        raise HTTPException(status_code=400, detail="User already associated with this company")

    # Crear la asociación
    new_association = UserCompany(user_id=user_id, company_id=company_id)
    db.add(new_association)
    db.commit()

    return {"message": "User successfully associated with the company"}

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    company_id: int = Query(..., description="ID of the company"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # Verificar que la compañía existe
    db_company = db.query(Company).filter(Company.id == company_id).first()
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Verificar si el email ya existe
    db_user = db.query(User).filter(User.email == user.email).first()

    if db_user:
        existing_association = db.query(UserCompany).filter(
            UserCompany.user_id == db_user.id,
            UserCompany.company_id == company_id
        ).first()

        if existing_association:
            raise HTTPException(status_code=400, detail="User already associated with this company")

        new_association = UserCompany(user_id=db_user.id, company_id=company_id)
        db.add(new_association)
        db.commit()
        db.refresh(db_user)
        return db_user

    # Si el usuario no existe, se crea y se asocia
    hashed_pw = hash_password(user.password)
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password=hashed_pw,
        status=user.status,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Crear asociación
    new_association = UserCompany(user_id=new_user.id, company_id=company_id)
    db.add(new_association)
    db.commit()

    return new_user

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    return db_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user: UserUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Actualizamos solo campos no nulos
    if user.full_name is not None:
        db_user.full_name = user.full_name
    if user.email is not None:
        db_user.email = user.email
    if user.status is not None:
        db_user.status = user.status
    if user.role is not None:
        db_user.role = user.role

    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")

    db.delete(db_user)
    db.commit()
    return
