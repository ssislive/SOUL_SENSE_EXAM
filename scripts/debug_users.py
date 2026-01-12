from app.db import get_session
from app.models import User

def list_users():
    session = get_session()
    try:
        users = session.query(User).all()
        print(f"Total Users: {len(users)}")
        for u in users:
            print(f"- ID: {u.id}, Username: {u.username}, Created: {u.created_at}")
            
        if not users:
            print("No users found. You may need to Sign Up first.")
            
    except Exception as e:
        print(f"Error querying users: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    list_users()
