
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine



load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL não encontrada. "
        "Configure a variável no arquivo .env "
        "ou nos Secrets do Streamlit Cloud."
    )


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
)

