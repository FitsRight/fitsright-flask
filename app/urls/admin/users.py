from flask import Blueprint, Flask, request, jsonify
from sqlalchemy import desc, text, func
import datetime


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
                    COUNT(m.tid) AS scan_count
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
    return dict(
        users_customers_id=str(row.users_customers_id),
        full_name=row.full_name,
        user_email=row.user_email,
        created_at=row.created_at,
        status=row.status,
        user_tokens=row.user_tokens,
        scan_count=row.scan_count,
    )
