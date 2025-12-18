import firebase_admin
from firebase_admin import auth, firestore, db as rtdb, storage
import datetime
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

def initialize_organization_rtdb(uid):
    """Initializes the Realtime Database structure for a new organization."""
    try:
        # User requested: root node 'organizations' -> {uid} -> 3 sub nodes
        # Initializing as objects to ensure they are treated as branches
        ref = rtdb.reference(f'organizations/{uid}')
        ref.set({
            'rfid_write': {'_init': 1},
            'rfid_read': {'_init': 1},
            'bus_location': {
                'latitude': 0.0,
                'longitude': 0.0
            }
        })
        return True
    except Exception as e:
        print(f"Error initializing RTDB: {e}")
        raise e

def upload_logo_to_storage(file, uid):
    """Uploads a logo file to Firebase Storage and returns the public URL."""
    try:
        bucket = storage.bucket()
        # Create a blob (file) in the bucket with a unique path
        # organizations/{uid}/logo.{ext}
        filename = file.filename
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'png'
        blob_path = f"organizations/{uid}/logo.{ext}"
        blob = bucket.blob(blob_path)

        # Upload the file content
        blob.upload_from_file(file, content_type=file.content_type)
        
        # Make the blob public
        blob.make_public()

        return blob.public_url
    except Exception as e:
        print(f"Error uploading logo to storage: {e}")
        return None

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
    """Deletes an organization from Firestore, Authentication, and RTDB."""
    try:
        # Delete from Firestore
        db = get_db()
        db.collection('organizations').document(uid).delete()
        
        # Delete from RTDB
        rtdb.reference(f'organizations/{uid}').delete()

        # Delete logo from Storage (best effort)
        try:
           bucket = storage.bucket()
           # Try to delete likely extensions, or list and delete
           # For simplicity, let's assume one is there or iterate
           blobs = bucket.list_blobs(prefix=f"organizations/{uid}/")
           for blob in blobs:
               blob.delete()
        except Exception as e:
            print(f"Error deleting artifacts from storage: {e}")

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
