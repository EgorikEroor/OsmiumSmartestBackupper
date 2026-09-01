from database import create_database
from include_backup_copy import include_backup_copy
def main():
    create_database()
    include_backup_copy()
if __name__=='__main__':
    main()