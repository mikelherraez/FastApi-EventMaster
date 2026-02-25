import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

print("DATABASE_URL =", DATABASE_URL)
if DATABASE_URL is None:
    raise ValueError("DATABASE_URL no está definida. "
        "Asegúrate de añadirla en tu archivo .env o en Railway Environment Variables"
    )

engine = create_engine(DATABASE_URL,connect_args={"sslmode": "require"})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()