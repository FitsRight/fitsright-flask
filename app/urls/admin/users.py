import hashlib
from flask import Blueprint, Flask, request, jsonify
from sqlalchemy import desc, text, func
import datetime
from werkzeug.security import generate_password_hash
from sqlalchemy import cast, types
from app.models.accounts.accounts_model import User


# Blueprint Configuration
users_url = Blueprint(
    "users_url", __name__, template_folder="html", static_folder="static"
)

from app import db

# Flask route to handle the user login
@users_url.route('/users_json', methods=['GET'])
def users_json():
    try:
        users = db.session.execute(
            text("""
                SELECT 
                    u.users_customers_id, 
                    u.full_name, 
                    u.user_email, 
                    u.status, 
                    u.user_tokens,
                    u.created_at,
                    COUNT(m.tid) AS scan_count,
                    u.is_admin
                FROM 
                    public.users_customers u
                LEFT JOIN 
                    public.measurements m 
                ON 
                    u.users_customers_id = m.users_customers_id
                GROUP BY 
                    u.users_customers_id, u.full_name, u.user_email, u.status, u.user_tokens
                ORDER BY 
                    u.user_email ASC;
            """)
        ).fetchall()
        list_users = [user_rows(r) for r in users]
        return jsonify(list_users)

    except Exception as e:
        return jsonify({"error": "An error occurred", "message": str(e)}), 500
    
def user_rows(row):    
    formatted_date = row.created_at.strftime("%Y-%m-%d %H:%M:%S.%f")

    return dict(
        users_customers_id=str(row.users_customers_id),
        full_name=row.full_name,
        user_email=row.user_email,
        created_at=formatted_date,
        status=row.status,
        user_tokens=row.user_tokens,
        scan_count=row.scan_count,
        is_admin=row.is_admin
    )

# Flask route to handle the user login
@users_url.route('/users_scans_json', methods=['POST'])
def users_scans_json():
    data = request.get_json()
    user_id = data.get('userId')
    
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    # Execute the database query with the user_id parameter
    users = db.session.execute(
        text("""
            SELECT tid, scanned_at, error_in_scan FROM public.measurements
            WHERE users_customers_id = :users_customers_id
            ORDER BY scanned_at DESC
        """),
        {"users_customers_id": user_id}
    ).fetchall()
    
    # Convert the database results to a list of dictionaries for JSON serialization
    scans_data = []
    for i, scan in enumerate(users):
    # Format the datetime to be compatible with HTML datetime-local input
        scan_date = None
        if scan.scanned_at:
            # Truncate the microseconds to milliseconds or remove them entirely
            scan_date = scan.scanned_at.strftime('%Y-%m-%dT%H:%M:%S')
            # Alternative: Keep milliseconds but not microseconds
            # scan_date = scan.scanned_at.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
        
        scans_data.append({
            "id": i + 1,
            "tid": scan.tid,
            "scanDate": scan_date,
            "error": scan.error_in_scan if hasattr(scan, 'error_in_scan') else None
        })
    
    # Return the data as JSON
    return jsonify(scans_data)


@users_url.route('/edit_user', methods=['POST'])
def edit_user():
    try:
        data = request.get_json()
        # Validate required fields
        users_customers_id = data.get('users_customers_id')
        user_tokens = data.get('user_tokens')
        is_admin = data.get('is_admin')  
        user_password = data.get('user_password')

        # Check if the retailer exists
        customers = db.session.execute(
            text("SELECT * FROM public.users_customers WHERE users_customers_id = :id"),
            {"id": users_customers_id}
        ).fetchone()

        if not customers:
            return jsonify({"error": "customer not found"}), 404     

        try:
            
            bit_value = 1 if is_admin else 0
            db.session.execute(
                text("UPDATE public.users_customers SET is_admin = :bit_value WHERE users_customers_id = :user_id"),
                {'bit_value': bit_value, 'user_id': users_customers_id}
            )

            current_user = User.query.filter_by(users_customers_id=users_customers_id).first()

            if current_user:
                current_user.user_tokens = int(user_tokens)
                
                if user_password != "":
                    current_user.user_password = hashlib.md5(user_password.encode()).hexdigest()

                db.session.commit()
            else:
                print("User not found!")

        except Exception as e:
            db.session.rollback()  # Roll back transaction to avoid locks
            print("Error:", e)  # Print the actual error message


        return jsonify({"message": "Customer updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500

@users_url.route('/update_scan_date', methods=['POST'])
def update_scan_date():
    try:
        data = request.get_json()
        # Validate required fields
        users_customers_id = data.get('userId')
        tid = data.get('scanId')
        scan_date = data.get('newDate')  

        db.session.execute(
            text("UPDATE public.measurements SET scanned_at = :scanned_at WHERE tid = :tid"),
            {'scanned_at': datetime.datetime.fromisoformat(scan_date), 'tid': str(tid)}
        )

        db.session.commit()

        return jsonify({"message": "Customer updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500

@users_url.route('/measurements_json', methods=['GET'])
def measurements_json():
    try:
        measurements = db.session.execute(
            text("""
                SELECT * FROM public.measurements_order
                ORDER BY display_order ASC 
            """)
        ).fetchall()
        
        measurement_data = []
        
        for i, measurement in enumerate(measurements):            
            measurement_data.append({
                "id": measurement.id,
                "measurement_name": measurement.measurement_name,
                "display_order": measurement.display_order,
                "category": measurement.category,
                "display_name": measurement.display_name,
                "display_yn": measurement.display_yn,
            })
        
        return jsonify(measurement_data)

    except Exception as e:
        return jsonify({"error": "An error occurred", "message": str(e)}), 500
  
@users_url.route('/update_measurement', methods=['POST'])
def update_measurement():
    try:
        data = request.get_json()
        print("Received data:", data)  # Debugging line
        if data.get('display_yn') == True:
            d_yn = 1
        else:
            d_yn = 0

        db.session.execute(
                text("UPDATE public.measurements_order SET category = :category, display_name = :display_name, display_yn = :display_yn WHERE id = :id"),
                {'category': data.get('category'), 'display_name': data.get('display_name'), 'display_yn': d_yn, 'id': data.get('id')}
            )
        
        db.session.commit()

        return jsonify({"message": "measurement updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500

@users_url.route('/update_measurement_order', methods=['POST'])
def update_measurement_order():
    try:
        data = request.get_json()
        for display_order, record_id in enumerate(data, start=1):
            db.session.execute(
                text("UPDATE public.measurements_order SET display_order = :display_order WHERE id = :id"),
                {'display_order': display_order, 'id': record_id}
            )
        
        db.session.commit()

        return jsonify({"message": "measurement updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500


