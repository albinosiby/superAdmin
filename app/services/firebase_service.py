import firebase_admin
from firebase_admin import auth, firestore
from flask import current_app

def get_db():
    return firestore.client()

def create_client_user(email, password, display_name):
    """Creates a user in Firebase Authentication."""
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name
        )
        return user.uid
    except Exception as e:
        print(f"Error creating user: {e}")
        raise e

def add_organization_data(uid, data):
    """Adds organization details to Firestore."""
    try:
        db = get_db()
        db.collection('organizations').document(uid).set(data)
        return True
    except Exception as e:
        print(f"Error checking Firestore: {e}")
        raise e

def get_all_organizations():
    """Retrieves all organizations from Firestore."""
    try:
        db = get_db()
        docs = db.collection('organizations').stream()
        orgs = []
        for doc in docs:
            org = doc.to_dict()
            org['id'] = doc.id
            orgs.append(org)
        return orgs
    except Exception as e:
        print(f"Error getting organizations: {e}")
        return []

def get_organization(uid):
    """Retrieves a single organization by ID."""
    try:
        db = get_db()
        doc = db.collection('organizations').document(uid).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    except Exception as e:
        print(f"Error getting organization: {e}")
        return None

def delete_organization(uid):
    """Deletes an organization from Firestore and Authentication."""
    try:
        # Delete from Firestore
        db = get_db()
        db.collection('organizations').document(uid).delete()
        
        # Delete from Auth
        auth.delete_user(uid)
        return True
    except Exception as e:
        print(f"Error deleting organization: {e}")
        raise e

def update_organization(uid, data):
    """Updates an organization in Firestore."""
    try:
        db = get_db()
        db.collection('organizations').document(uid).update(data)
        return True
    except Exception as e:
        print(f"Error updating organization: {e}")
        raise e
