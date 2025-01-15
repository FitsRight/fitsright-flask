from flask import Blueprint, Flask, request, jsonify
from sqlalchemy import desc, text, func
import datetime


# Blueprint Configuration
retailers_url = Blueprint(
    "retailers_url", __name__, template_folder="html", static_folder="static"
)

from app import db

# Flask route to handle the user login
@retailers_url.route('/retailers_json', methods=['GET'])
def retailers_json():
    try:
        bookings = db.session.execute(
            text(
                "SELECT * FROM public.retailers ORDER by name ASC"
            )
        ).fetchall()
        list_bookings = [retailers_rows(r) for r in bookings]
        return jsonify(list_bookings)

    except Exception as e:
        return jsonify({"error": "An error occurred", "message": str(e)}), 500
    
def retailers_rows(row):
    return dict(
        retailers_id=str(row.retailers_id),
        retailers_type=row.retailers_type,
        name=row.name,
        website=row.website,
        description=row.description,
        status=row.status,
    )


@retailers_url.route('/add_retailer', methods=['POST'])
def add_retailer():
    try:
        # Get data from the request body
        data = request.get_json()
        # Validate required fields
        retailers_id = data.get('retailers_id')
        retailers_type = data.get('retailers_type')
        name = data.get('name')
        website = data.get('website')
        description = data.get('description')
        sort_order = data.get('order')
        status = data.get('status')
        currentTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not name or not website or not sort_order:
            return jsonify({"error": "Missing required fields"}), 400

        db.session.execute(
            text(
                """
                UPDATE public.retailers
                SET 
                    retailers_type = :retailers_type,
                    name = :name,
                    website = :website,
                    image = :image,
                    description = :description,
                    date_modified = :date_modified,
                    status = :status
                WHERE id = :id
                """
            ),
            {
                "retailers_type": retailers_type,
                "name": name,
                "website": website,
                "image": '',
                "description": description,
                "date_modified": currentTime,
                "status": status,
                "id": retailers_id  # The retailer ID you want to update
            }
        )
        db.session.commit()


        return jsonify({"message": "Retailer added successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500

@retailers_url.route('/edit_retailer', methods=['POST'])
def edit_retailer():
    try:
        data = request.get_json()
        # Validate required fields
        retailers_id = data.get('retailers_id')
        retailers_type = data.get('retailers_type')
        name = data.get('name')
        website = data.get('website')
        description = data.get('description')
        status = data.get('status')

        # Check if the retailer exists
        retailer = db.session.execute(
            text("SELECT * FROM public.retailers WHERE retailers_id = :retailers_id"),
            {"retailers_id": retailers_id}
        ).fetchone()

        if not retailer:
            return jsonify({"error": "Retailer not found"}), 404
        
        db.session.execute(
        text(
                """
                UPDATE public.retailers
                SET 
                    retailers_type = :retailers_type,
                    name = :name,
                    website = :website,
                    description = :description,
                    date_modified = :date_modified,
                    status = :status
                WHERE retailers_id = :retailers_id
                """
            ),
            {
                "retailers_type": retailers_type,
                "name": name,
                "website": website,
                "description": description,
                "date_modified": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": status,
                "retailers_id": retailers_id 
            }
        )


        db.session.commit()

        return jsonify({"message": "Retailer updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500

@retailers_url.route('/delete_retailer', methods=['POST'])
def delete_retailer():
    try:
        data = request.get_json()
        # Validate required fields
        retailers_id = data.get('retailers_id')

        # Check if the retailer exists
        retailer = db.session.execute(
            text("SELECT * FROM public.retailers WHERE retailers_id = :retailers_id"),
            {"retailers_id": retailers_id}
        ).fetchone()

        if not retailer:
            return jsonify({"error": "Retailer not found"}), 404

        # Delete the retailer from the database
        db.session.execute(
            text("DELETE FROM public.retailers WHERE retailers_id = :retailers_id"),
            {"retailers_id": retailers_id}
        )
        db.session.commit()

        return jsonify({"message": "Retailer deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500
