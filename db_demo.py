from sqlalchemy import create_engine, text


DATABASE_URL = "sqlite:///./bank_data.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def fetch_all_banks():
    query = text("SELECT * FROM banks")

    with engine.connect() as connection:
        result = connection.execute(query)

        rows = result.fetchall()

        for row in rows:
            print(dict(row._mapping))


fetch_all_banks()