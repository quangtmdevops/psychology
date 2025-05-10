import sys
print(f"Python path: {sys.path}")
print(f"Python version: {sys.version}")

try:
    import uvicorn
    print("Uvicorn version:", uvicorn.__version__)
except Exception as e:
    print("Error importing uvicorn:", str(e))

try:
    import fastapi
    print("FastAPI version:", fastapi.__version__)
except Exception as e:
    print("Error importing fastapi:", str(e))

try:
    import sqlalchemy
    print("SQLAlchemy version:", sqlalchemy.__version__)
except Exception as e:
    print("Error importing sqlalchemy:", str(e)) 