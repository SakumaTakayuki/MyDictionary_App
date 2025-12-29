from db.session import engine, Base
import db.model


def init_db():
    print(Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("DB initialized")
