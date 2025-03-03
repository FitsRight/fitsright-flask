import pprint
from flask import Blueprint, Flask, request, jsonify
from sqlalchemy import desc, text, func
import datetime


# Blueprint Configuration
dashboard_url = Blueprint(
    "dashboard_url", __name__, template_folder="html", static_folder="static"
)

from app import db

@dashboard_url.route('/signup_json', methods=['GET'])
def signup_json():
    print("signup_json")
    try:
        users = db.session.execute(
            text("""
                 SELECT 
                    date_trunc('month', created_at) AS month,
                    COUNT(*) AS user_count
                FROM 
                    public.users_customers
                WHERE 
                    created_at >= date_trunc('month', CURRENT_DATE - INTERVAL '5 months')
                    AND created_at < date_trunc('month', CURRENT_DATE + INTERVAL '1 month')
                GROUP BY 
                    date_trunc('month', created_at)
                ORDER BY 
                    month ASC;
            """)
        ).fetchall()
        list_users = [signup_rows(r) for r in users]
        print(list_users)
        return jsonify(list_users)

    except Exception as e:
        return jsonify({"error": "An error occurred", "message": str(e)}), 500

def signup_rows(row):
    return dict(
        month=str(row.month),
        user_count=row.user_count
    )
    
