# from datetime import UTC, datetime, timedelta

# from fastapi import Depends, FastAPI, HTTPException
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from jose import jwt
# from passlib.context import CryptContext
# from sqlmodel import Field, Session, SQLModel, create_engine, select

# # --- CONFIGURATION ---
# SECRET_KEY = "your-super-secret-key"  # Keep this safe!
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# # --- MODELS ---
# class User(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     username: str = Field(index=True, unique=True)
#     hashed_password: str


# # --- UTILS ---
# def hash_password(password: str):
#     return pwd_context.hash(password)


# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)


# def create_access_token(data: dict):
#     to_encode = data.copy()
#     expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# # --- APP & DB ---
# app = FastAPI()
# sqlite_url = "sqlite:///database.db"
# engine = create_engine(sqlite_url)


# @app.on_event("startup")
# def on_startup():
#     SQLModel.metadata.create_all(engine)


# # --- ROUTES ---


# @app.post("/register")
# def register_user(username: str, password: str):
#     with Session(engine) as session:
#         hashed = hash_password(password)
#         user = User(username=username, hashed_password=hashed)
#         session.add(user)
#         session.commit()
#         return {"msg": "User created"}


# @app.post("/token")
# def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     with Session(engine) as session:
#         statement = select(User).where(User.username == form_data.username)
#         user = session.exec(statement).first()

#         if not user or not verify_password(form_data.password, user.hashed_password):
#             raise HTTPException(status_code=400, detail="Incorrect username or password")

#         access_token = create_access_token(data={"sub": user.username})
#         return {"access_token": access_token, "token_type": "bearer"}


# @app.get("/users/me")
# def read_users_me(token: str = Depends(oauth2_scheme)):
#     # This route is now protected!
#     return {"token": token, "info": "This is a secret area."}
