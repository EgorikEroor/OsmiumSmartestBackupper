from database import create_database
from registry import create_button
from logic import resource_logic
def main():
    create_database()
    resource_logic()
if __name__ == '__main__':
    main()