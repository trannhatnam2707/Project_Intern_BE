import os
from urllib.parse import quote_plus

import pyodbc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


def _resolve_sql_server_odbc_driver() -> str:
    """
    Pick an installed SQL Server ODBC driver on Windows.
    IM002 often means the driver name in the URL does not exist on this machine.
    """
    configured = (os.getenv("DB_ODBC_DRIVER") or "").strip()
    available = set(pyodbc.drivers())
    preferred = [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
        "ODBC Driver 13 for SQL Server",
        "SQL Server Native Client 11.0",
        "SQL Server",
    ]
    auto_picked = False
    if configured and configured in available:
        return configured
    if configured and configured not in available:
        print(
            f"Warning: DB_ODBC_DRIVER={configured!r} is not installed; "
            "choosing another SQL Server ODBC driver."
        )
        auto_picked = True
    elif not configured:
        auto_picked = True

    for name in preferred:
        if name in available:
            if auto_picked:
                print(f"Using ODBC driver: {name}")
            return name

    for d in sorted(available):
        if "SQL Server" in d:
            if auto_picked:
                print(f"Using ODBC driver: {d}")
            return d

    raise RuntimeError(
        "No SQL Server ODBC driver found. Install Microsoft ODBC Driver 17 or 18 for SQL Server, "
        "or set DB_ODBC_DRIVER in .env to the exact name shown in ODBC Data Source Administrator (64-bit)."
    )


# SQL Server connection
DB_HOST = os.getenv("DB_HOST", "LAPTOP-9TFF98TE")
DB_NAME = os.getenv("DB_NAME", "EcommerceAI")
DB_ODBC_DRIVER = _resolve_sql_server_odbc_driver()

_connect_params = [
    f"driver={quote_plus(DB_ODBC_DRIVER)}",
    "trusted_connection=yes",
]
if "ODBC Driver 17" in DB_ODBC_DRIVER or "ODBC Driver 18" in DB_ODBC_DRIVER:
    _connect_params.extend(["Encrypt=yes", "TrustServerCertificate=yes"])

DATABASE_URL = f"mssql+pyodbc://@{DB_HOST}/{DB_NAME}?" + "&".join(_connect_params)

engine = create_engine(
    DATABASE_URL,
    fast_executemany=True,
    connect_args={
        "unicode_results": True,
    },
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    try:
        with engine.connect():
            print("Database connection OK")
    except Exception as e:
        print("Database connection failed:", e)


test_connection()
