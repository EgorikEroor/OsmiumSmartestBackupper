from sqlalchemy import Column, String, create_engine,Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from pathlib import Path
folder_database = Path.home() / 'AppData' / 'Local' / 'OsmiumSmartestBackupper' / 'Database'
database_engine = create_engine(f"sqlite:///{folder_database / 'database_files.db'}")
Database = declarative_base()
class Resources(Database):
    __tablename__ = 'Files'
    uuid = Column(String,primary_key = True)
    name = Column(String)
    size = Column(String)
    archived = Column(Boolean)
    data_delete = Column(String)
def create_database():
    Database.metadata.create_all(database_engine)
