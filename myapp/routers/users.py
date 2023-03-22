from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from myapp.models import Base
from myapp.dependencies import database, error_messages
from myapp.database import engine
from myapp.schema.user import UserCreate, UserOut
from myapp.crud.users import UserCrud


Base.metadata.create_all(bind=engine)

db_instance = database.db_dependency
error_msgs = error_messages.UserErrorMessages


router = APIRouter(prefix="/users", tags=["users"])


# CREATE AND PERSIT A NEW USER TO DB IF NOT EXISTS
@router.post("/", response_model=UserOut)
def create_users(user: UserCreate, db: Session = Depends(db_instance)):
    db_user = UserCrud.get_user_by_phone(db, user.phone)
    if db_user:
        raise HTTPException(status_code=400, detail=error_msgs.already_exists)

    try:
        return UserCrud.create_user(db, user)
    except IntegrityError as e:
        error = str(e)

        if "users_password_email_ck" in error:
            raise HTTPException(
                status_code=400, detail="Provide the email and password"
            )

        if "users_phone_email_key" in error:
            raise HTTPException(status_code=400, detail=error_msgs.already_exists)

        raise HTTPException(status_code=400, detail="Something went wrong")


# GET AN ARRAY OF USERS
@router.get("/", response_model=list[UserOut])
def get_all_users(
    db: Session = Depends(db_instance),
    skip: int = Query(default=0),
    limit: int = Query(default=100),
):
    users = UserCrud.get_records(db, skip, limit)

    if len(users) == 0:
        raise HTTPException(status_code=404, detail=error_msgs.no_users)

    return users


user_id_description = "If you don't have the users id, provide any integer less than one and the users phone number or email adress via a query"


# GET A SINGLE USER BY ID
@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int = Path(description=user_id_description),
    phone: str = Query(default=None, description="Retrieve the user by phone number"),
    email: str = Query(default=None, description="Retrive the user by email address"),
    db: Session = Depends(db_instance),
):
    user = None

    if user_id > 0:
        user = UserCrud.get_by_id(db=db, id=user_id)
    else:
        if phone is None and email is None:
            raise HTTPException(
                status_code=400,
                detail="Provide the user's phone number or email address",
            )
        # Only use the email address when phone is not provided
        if phone:
            user = UserCrud.get_user_by_phone(db=db, phone=phone)
        else:
            user = UserCrud.get_user_by_email(db=db, email=email)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
