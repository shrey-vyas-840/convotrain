from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg://postgres:vsmv_6870@localhost:5432/restaurant_knowledge_os",
    echo=True,
)

print("creating connection...")

with engine.connect() as conn:
    print("CONNECTED")

print("DONE")