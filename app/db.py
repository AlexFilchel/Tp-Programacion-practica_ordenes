from sqlmodel import SQLModel, Session, create_engine

BASE_DE_DATOS_URL = "sqlite:///database.db"

engine = create_engine(BASE_DE_DATOS_URL, echo=True)

def crear_base_de_datos():
    SQLModel.metadata.create_all(engine)
    
def get_session():
    with Session(engine) as session:
        yield session