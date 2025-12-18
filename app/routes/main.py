from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from firebase_admin import firestore
from app.services.firebase_service import create_client_user, add_organization_data, get_all_organizations, delete_organization, get_organization, update_organization, initialize_organization_rtdb, upload_logo_to_storage
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
            
            # Fee Details
            fee_type = request.form.get('fee_type')
            term_count = request.form.get('term_count')
            
            fee_details = {}
            if fee_type == 'Yearly':
                fee_details['paymentType'] = 'Yearly One Time'
            elif fee_type == 'Termly':
                fee_details['paymentType'] = 'Termly'
                if term_count:
                    fee_details['numberOfTerms'] = int(term_count)
            else:
                fee_details['paymentType'] = fee_type
            
            logo_filename = "default_logo.png"
            if 'logo' in request.files:
                file = request.files['logo']
                if file and file.filename != '':

                    
                    # Temporarily save to upload
                    # Actually, we can pass the stream directly if helper supports it.
                    # My helper uses file.upload_from_file so we can pass the request.files['logo'] directly if we don't save it first.
                    # However, create_client_user needs to happen FIRST to get the UID.
                    # So we hold the file object.
                    logo_filename = "pending"

            if not all([name, address, phone, org_type, email, password]):
                 flash("All fields are required", "error")
                 return redirect(url_for('main.add_client'))

            # 1. Create Auth User
            uid = create_client_user(email, password, name)

            # 1.5 Upload Logo if present
            logo_url = "default_logo.png"
            if 'logo' in request.files:
                file = request.files['logo']
                if file and file.filename != '':
                    url = upload_logo_to_storage(file, uid)
                    if url:
                         logo_url = url

            # 2. Add Organization Data
            org_data = {
                "name": name,
                "address": address,
                "phone": phone,
                "type": org_type,
                "email": email,

                "feeDetails": fee_details,
                "logo": logo_url,
                "createdAt": datetime.datetime.now()
            }

            add_organization_data(uid, org_data)
            
            # 3. Initialize RTDB
            initialize_organization_rtdb(uid)

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
            
            # Fee Details
            fee_type = request.form.get('fee_type')
            term_count = request.form.get('term_count')
            
            fee_details = {}
            if fee_type == 'Yearly':
                fee_details['paymentType'] = 'Yearly One Time'
            elif fee_type == 'Termly':
                fee_details['paymentType'] = 'Termly'
                if term_count:
                    fee_details['numberOfTerms'] = int(term_count)
            else:
                fee_details['paymentType'] = fee_type
            
            org_data = {
                "name": name,
                "address": address,
                "phone": phone,
                "type": org_type,

                "email": email,
                "feeDetails": fee_details
            }

            if 'logo' in request.files:
                file = request.files['logo']
                if file and file.filename != '':
                    # Update logo in storage
                    url = upload_logo_to_storage(file, uid)
                    if url:
                        org_data['logo'] = url
            
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
