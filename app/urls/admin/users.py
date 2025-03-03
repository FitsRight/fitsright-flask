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

            bit_value = '1' if is_admin else '0'
            db.session.execute(
                text("UPDATE public.users_customers SET is_admin = CAST(:bit_value AS BIT(1)) WHERE users_customers_id = :user_id"),
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

