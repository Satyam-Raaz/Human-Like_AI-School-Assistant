from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# NOTE: Move this to an environment variable before deploying anywhere
# real — a hardcoded DB password in source control is a security risk.
URL_DATABASE = 'mysql+pymysql://root:Satyam%409211@localhost:3306/FastApi'

engine = create_engine(URL_DATABASE, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
