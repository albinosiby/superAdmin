from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from firebase_admin import firestore
from app.services.firebase_service import create_client_user, add_organization_data, get_all_organizations, delete_organization, get_organization, update_organization
import os
from werkzeug.utils import secure_filename
import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    organizations = get_all_organizations()
    return render_template('dashboard.html', organizations=organizations)

@main_bp.route('/add-client', methods=['GET', 'POST'])
def add_client():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            address = request.form.get('address')
            phone = request.form.get('phone')
            org_type = request.form.get('type')
            email = request.form.get('email')
            password = request.form.get('password')
            
            logo_filename = "default_logo.png"
            if 'logo' in request.files:
                file = request.files['logo']
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    # Ensure directory exists
                    upload_folder = os.path.join(current_app.root_path, 'static/images')
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                    
                    file.save(os.path.join(upload_folder, filename))
                    logo_filename = filename

            if not all([name, address, phone, org_type, email, password]):
                 flash("All fields are required", "error")
                 return redirect(url_for('main.add_client'))

            # 1. Create Auth User
            uid = create_client_user(email, password, name)

            # 2. Add Organization Data
            org_data = {
                "name": name,
                "address": address,
                "phone": phone,
                "type": org_type,
                "email": email,
                "logo": logo_filename,
                "createdAt": datetime.datetime.now()
            }

            add_organization_data(uid, org_data)

            flash("Client added successfully", "success")
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            flash(f"Error adding client: {str(e)}", "error")
            return redirect(url_for('main.add_client'))

    return render_template('add_client.html')

@main_bp.route('/delete-client/<uid>', methods=['POST'])
def delete_client(uid):
    try:
        delete_organization(uid)
        flash("Client deleted successfully", "success")
    except Exception as e:
        flash(f"Error deleting client: {str(e)}", "error")
    return redirect(url_for('main.dashboard'))

@main_bp.route('/edit-client/<uid>', methods=['GET', 'POST'])
def edit_client(uid):
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            address = request.form.get('address')
            phone = request.form.get('phone')
            org_type = request.form.get('type')
            email = request.form.get('email')
            
            org_data = {
                "name": name,
                "address": address,
                "phone": phone,
                "type": org_type,
                "email": email
            }

            if 'logo' in request.files:
                file = request.files['logo']
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    upload_folder = os.path.join(current_app.root_path, 'static/images')
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                    file.save(os.path.join(upload_folder, filename))
                    org_data['logo'] = filename
            
            update_organization(uid, org_data)
            flash("Client updated successfully", "success")
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            flash(f"Error updating client: {str(e)}", "error")
            return redirect(url_for('main.edit_client', uid=uid))
    
    # GET request
    org = get_organization(uid)
    if not org:
        flash("Client not found", "error")
        return redirect(url_for('main.dashboard'))
    
    return render_template('edit_client.html', org=org)

@main_bp.route('/client/<uid>')
def view_client(uid):
    org = get_organization(uid)
    if not org:
        flash("Client not found", "error")
        return redirect(url_for('main.dashboard'))
    return render_template('view_client.html', org=org)
