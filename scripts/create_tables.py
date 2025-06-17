import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.db import engine
from app.models.price import Base

print("Creating database tables...")
# This command creates all tables defined in the models that inherit from Base
Base.metadata.create_all(bind=engine)
print("Tables created successfully.")