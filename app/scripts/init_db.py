import subprocess
import sys
import os

def init_database():
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    # Run migrations
    print("Running database migrations...")
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    
    print("\nDatabase initialization completed successfully!")

if __name__ == "__main__":
    init_database() 