from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from myapp.dependencies import error_utils, error_messages
from myapp.models import Base
from myapp.dependencies import database
from myapp.database.sqlalchemy_config import engine
from myapp.schema.user import UserCreate, UserOut
from myapp.crud.users import UserCrud


Base.metadata.create_all(bind=engine)

db_instance = database.db_dependency
error_msgs = error_messages.UserErrorMessages


def handle_data_error(error_message):
    # TODO: Implement better handling upto testing
    raise HTTPException(status_code=400, detail="Invalid data type for some feilds ")


def handle_integrity_error(error_message):
    if "users_password_email_ck" in error_message:
        raise HTTPException(status_code=400, detail="Provide the email and password")

    if "users_phone_email_key" in error_message:
        raise HTTPException(status_code=400, detail=error_msgs.already_exists)

    error_utils.raise_server_error()


router = APIRouter(prefix="/users", tags=["users"])


# CREATE AND PERSIT A NEW USER TO DB IF NOT EXISTS
@router.post("/", response_model=UserOut, status_code=201)
def create_users(user: UserCreate, db: Session = Depends(db_instance)):
    db_user = UserCrud.get_user_by_phone(db, user.phone)
    if db_user:
        raise HTTPException(status_code=400, detail=error_msgs.already_exists)

    try:
        return UserCrud.create(db, user)
    except IntegrityError as error:
        handle_integrity_error(str(error))
    except Exception:
        error_messages.dev_error_tracer("Unhandled exception in create users")
        error_utils.raise_server_error()


# GET AN ARRAY OF USERS
@router.get("/", response_model=list[UserOut], status_code=200)
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
@router.get("/{user_id}", response_model=UserOut, status_code=200)
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

        if phone:
            user = UserCrud.get_user_by_phone(db=db, phone=phone)
        else:  # Email address
            user = UserCrud.get_user_by_email(db=db, email=email)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
