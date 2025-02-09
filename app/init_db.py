from app.database import engine, Base
import app.models  

print("Database connection being checked...")

try:
    #Check if tables exist
    print("Tables bf creation:", Base.metadata.tables.keys())

    print("Creating db tables...")

    Base.metadata.create_all(bind=engine)
    
    print("db tables sucessfully created")
    
    #Verify tables afterwards
    print("Tables after creation:", Base.metadata.tables.keys())
except Exception as e:
    print("Fatal error during DB creation:", e)
