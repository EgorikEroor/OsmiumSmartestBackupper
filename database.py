from pathlib import Path
import os
from sqlalchemy import create_engine,Column,String,Boolean
from sqlalchemy.orm import declarative_base
folder_database=Path(os.environ.get('LOCALAPPDATA',Path.home()/'AppData'/'Local'))/'OsmiumSmartestBackupper'/'Database'
database_engine=create_engine(f"sqlite:///{folder_database/'database_files.db'}")
Database=declarative_base()
class Resources(Database):
    __tablename__='Resources'
    uuid=Column(String,primary_key=True)
    name=Column(String)
    size=Column(String)
    archived=Column(Boolean)
    data_delete=Column(String)
def create_database():
    folder_database.mkdir(parents=True,exist_ok=True)
    Database.metadata.create_all(database_engine)
