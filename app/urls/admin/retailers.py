import pprint
import uuid
from flask import Blueprint, Flask, request, jsonify
from sqlalchemy import desc, text, func
import datetime
from pydantic import BaseModel

# Blueprint Configuration
retailers_url = Blueprint(
    "retailers_url", __name__, template_folder="html", static_folder="static"
)

from app import db

@retailers_url.route('/retailers_json', methods=['GET'])
def retailers_json():
    try:
        # Improved query using JOIN instead of subquery
        query = text("""
            SELECT 
                r.retailers_id, 
                r.retailers_type, 
                r.name, 
                r.website, 
                r.description, 
                r.status, 
                COUNT(CASE WHEN rs.status = 'Active' THEN rs.retailers_sizes_id ELSE NULL END) as retailers_count,
                r.cpc, 
                r.cpa 
            FROM 
                public.retailers r
            LEFT JOIN 
                public.retailers_sizes rs ON r.retailers_id = rs.retailers_id
            GROUP BY 
                r.retailers_id, r.retailers_type, r.name, r.website, r.description, r.status, r.CPC, r.CPA
            ORDER BY 
                r.name ASC
        """)
        
        bookings = db.session.execute(query).fetchall()
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
        retailers_count=row.retailers_count,
        cpc=row.cpc,
        cpa=row.cpa
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
        CPC = data.get('CPC')
        CPA = data.get('CPA')
        
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
                    status = :status,
                    CPC = :CPC,
                    CPA = :CPA
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
                "id": retailers_id,
                "CPC": CPC,
                "CPA": CPA
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
        CPC = data.get('CPC')
        CPA = data.get('CPA')

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
                    status = :status,
                    CPC = :CPC,
                    CPA = :CPA
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
                "retailers_id": retailers_id ,
                "CPC": CPC,
                "CPA": CPA
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

# Flask route to handle the user login
@retailers_url.route('/retailers_sizes_json/<int:rref>', methods=['GET'])
def retailers_sizes_json(rref):
    try:
        bookings = db.session.execute(
            text(
                f"""SELECT public.system_genders.name as gender_name, public.sizes_categories.name as categorie_name, public.sizes_uk.name as size_name, public.retailers_sizes.* 
                FROM public.retailers_sizes
                INNER JOIN public.sizes_categories on public.sizes_categories.sizes_categories_id = public.retailers_sizes.sizes_categories_id
                INNER JOIN public.system_genders on public.system_genders.system_genders_id = public.sizes_categories.system_genders_id
                INNER JOIN public.sizes_uk on public.sizes_uk.sizes_uk_id = public.retailers_sizes.sizes_uk_id
                WHERE public.retailers_sizes.retailers_id = :rref
                ORDER BY gender_name, public.sizes_uk.sort, categorie_name, size_name ASC"""
            ),
            {"rref": rref}
        ).fetchall()
        list_bookings = [retailers_sizes_rows(r) for r in bookings]
        return jsonify(list_bookings)

    except Exception as e:
        return jsonify({"error": "An error occurred", "message": str(e)}), 500

def retailers_sizes_rows(row):
    return dict(
        retailers_sizes_id=row.retailers_sizes_id,
        gender_name=row.gender_name,
        categorie_name=row.categorie_name,
        size_name=row.size_name,
        neck=row.neck,
        neck_to=row.neck_to,
        chest=row.chest,
        chest_to=row.chest_to,
        under_bust=row.under_bust,
        under_bust_to=row.under_bust_to,
        waist=row.waist,
        waist_to=row.waist_to,
        hip=row.hip,
        hip_to=row.hip_to,
    )

# Flask route to handle the user login
@retailers_url.route('/get_categories/<int:gref>', methods=['GET'])
def get_catergories_json(gref):
    try:
        bookings = db.session.execute(
            text(
                "SELECT public.sizes_categories.sizes_categories_id, public.sizes_categories.name FROM public.sizes_categories WHERE system_genders_id = :gref ORDER BY name ASC"
            ),
            {"gref": gref}
        ).fetchall()
        options = "".join(
            f"<option value='{r.sizes_categories_id}'>{r.name}</option>" for r in bookings
        )

        bookings = db.session.execute(
            text(
                "SELECT public.sizes_uk.sizes_uk_id, public.sizes_uk.name FROM public.sizes_uk WHERE system_genders_id=:gref ORDER BY public.sizes_uk.sort, public.sizes_uk.name ASC"
            ),
            {"gref": gref}
        ).fetchall()
        sizes = "".join(
            f"<option value='{r.sizes_uk_id}'>{r.name}</option>" for r in bookings
        )

        return jsonify({"options": options, "sizes": sizes})

    except Exception as e:
        return jsonify({"error": "An error occurred", "message": str(e)}), 500

@retailers_url.route('/add_retailer_size', methods=['POST'])
def add_retailer_size():
    try:
        # Get data from the request body
        data = request.get_json()
        # Validate required fields
        retailers_id = int(data.get('retailers_id', 0))
        sizes_units_id = int(data.get('sizes_units_id', 0))
        sizes_categories_id = int(data.get('sizes_categories_id', 0))
        sizes_uk_id = int(data.get('sizes_uk_id', 0))

        from sqlalchemy import text

        db.session.execute(
            text(
                """
                INSERT INTO public.retailers_sizes (
                    retailers_id,
                    sizes_units_id,
                    sizes_categories_id,
                    sizes_uk_id,
                    date_added,
                    date_modified,
                    status,
                    size_type
                ) 
                VALUES (
                    :retailers_id,
                    :sizes_units_id,
                    :sizes_categories_id,
                    :sizes_uk_id,
                    :date_added,
                    :date_modified,
                    :status,
                    :size_type
                )
                """
            ),
            {
                "retailers_id": retailers_id,
                "sizes_units_id": sizes_units_id,
                "sizes_categories_id": sizes_categories_id,
                "sizes_uk_id": sizes_uk_id,
                "date_added": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "date_modified": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "Active",
                "size_type": "Fixed",
            }
        )
        db.session.commit()



        return jsonify({"message": "Retailer Size added successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500

@retailers_url.route('/update_retailer_size', methods=['POST'])
def update_retailer_size():
    try:
        # Get data from the request body
        data = request.get_json()
        # Validate required fields
        retailers_sizes_id = int(data.get('retailers_sizes_id', 0))
        neck = float(data.get('neck', 0)),
        neck_to = float(data.get('neck_to', 0)),
        chest = float(data.get('chest', 0)),
        chest_to = float(data.get('chest_to', 0)),
        under_bust = float(data.get('under_bust', 0)),
        under_bust_to = float(data.get('under_bust_to', 0)),
        waist = float(data.get('waist', 0)),
        waist_to = float(data.get('waist_to', 0)),
        hip = float(data.get('hip', 0)),
        hip_to = float(data.get('hip_to', 0)),

        # from sqlalchemy import text

        db.session.execute(
            text(
                """
                UPDATE public.retailers_sizes
                SET 
                    neck = :neck,
                    neck_to = :neck_to,
                    chest = :chest,
                    chest_to = :chest_to,
                    under_bust = :under_bust,
                    under_bust_to = :under_bust_to,
                    waist = :waist,
                    waist_to = :waist_to,
                    hip = :hip,
                    hip_to = :hip_to,
                    date_modified = :date_modified
                WHERE retailers_sizes_id = :retailers_sizes_id
                """
            ),
            {
                "neck": neck,
                "neck_to": neck_to,
                "chest": chest,
                "chest_to": chest_to,
                "under_bust": under_bust,
                "under_bust_to": under_bust_to,
                "waist": waist,
                "waist_to": waist_to,
                "hip": hip,
                "hip_to": hip_to,
                "date_modified": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "retailers_sizes_id": retailers_sizes_id 
            }
        )
        db.session.commit()



        return jsonify({"message": "Retailer Size updated successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500


@retailers_url.route('/delete_retailer_size', methods=['POST'])
def delete_retailer_size():
    try:
        # Get data from the request body
        data = request.get_json()
        # Validate required fields
        retailers_sizes_id = int(data.get('retailers_sizes_id', 0))
        # from sqlalchemy import text

        db.session.execute(
            text(
                """
                DELETE FROM public.retailers_sizes
                WHERE retailers_sizes_id = :retailers_sizes_id
                """
            ),
            {
                "retailers_sizes_id": retailers_sizes_id 
            }
        )
        db.session.commit()

        return jsonify({"message": "Retailer Size updated successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500


# Flask route to handle the user login
@retailers_url.route('/sizes_json', methods=['GET'])
def sizes_json():
    try:
        bookings = db.session.execute(
            text(
                f"""SELECT public.system_genders.name as gender_name, public.sizes_uk.* 
                FROM public.sizes_uk
                INNER JOIN public.system_genders on public.system_genders.system_genders_id=public.sizes_uk.system_genders_id
                ORDER BY public.sizes_uk.system_genders_id, public.sizes_uk.sort ASC """
            )
        ).fetchall()
        list_bookings = [sizes_rows(r) for r in bookings]
        return jsonify(list_bookings)

    except Exception as e:
        return jsonify({"error": "An error occurred", "message": str(e)}), 500
def sizes_rows(row):
    return dict(
        sizes_uk_id=row.sizes_uk_id,
        gender_name=row.gender_name,
        name=row.name,
        system_genders_id=row.system_genders_id,
        sort=row.sort,
        status=row.status,
        grouping_type=row.grouping_type
    )

class SortUpdate(BaseModel):
    id: int
    sort: int
    
@retailers_url.post("/sizes_update_sort")
async def sizes_update_sort():
    
    try:
        data = request.get_json() 

        for row in data:
            print(row["id"])

            db.session.execute(
                text(
                    """
                    UPDATE public.sizes_uk
                    SET 
                        sort = :sort
                    WHERE sizes_uk_id = :sizes_uk_id
                    """
                ),
                {
                    "sort": row["sort"],
                    "sizes_uk_id": row["id"]
                }
            )
            db.session.commit()

        return {"message": "Sort order updated successfully"}

    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500

@retailers_url.route('/promotions_json', methods=['GET'])
def promotions_json():
    try:
        bookings = db.session.execute(
            text(
                "SELECT public.offers.id, public.offers.base64, public.offers.url_redirect FROM public.offers ORDER by url_redirect ASC"
            )
        ).fetchall()
        list_bookings = [promotions_rows(r) for r in bookings]
        return jsonify(list_bookings)

    except Exception as e:
        return jsonify({"error": "An error occurred", "message": str(e)}), 500

def promotions_rows(row):
    return dict(
        id=str(row.id),
        base64=row.base64,
        url_redirect=row.url_redirect
    )

@retailers_url.route('/edit_offer', methods=['POST'])
def edit_offer():
    try:
        data = request.get_json()
        # Validate required fields
        id = data.get('id')
        base64 = data.get('base64')
        url_redirect = data.get('url_redirect')

        # Check if the retailer exists
        retailer = db.session.execute(
            text("SELECT * FROM public.offers WHERE id = :id"),
            {"id": id}
        ).fetchone()

        if not retailer:
            return jsonify({"error": "Retailer not found"}), 404     

        db.session.execute(
        text(
                """
                UPDATE public.offers
                SET 
                    base64 = :base64,
                    url_redirect = :url_redirect
                WHERE id = :id
                """
            ),
            {
                "base64": base64,
                "url_redirect": url_redirect,
                "id": id 
            }
        )

        db.session.commit()

        return jsonify({"message": "Retailer updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500


@retailers_url.route('/add_offer', methods=['POST'])
def add_offer():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'base64' not in data or 'url_redirect' not in data:
            return jsonify({"error": "Missing required fields"}), 400
            
        base64 = data.get('base64')
        url_redirect = data.get('url_redirect')

        db.session.execute(
            text(
                """
                    INSERT INTO public.offers(
                    id, base64, url_redirect)
                    VALUES (:id, :base64, :url_redirect);
                """
            ),
            {
                "id": str(uuid.uuid4()),
                "base64": base64,
                "url_redirect": url_redirect
            }
        )

        db.session.commit()

        return jsonify({"message": "Offer added successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500


@retailers_url.route('/delete_offer', methods=['POST'])
def delete_offer():
    try:
        data = request.get_json()
        id = data.get('offer_id')
        
        print(id)

        db.session.execute(
            text(
                """
                    DELETE FROM public.offers WHERE id = :id;
                """
            ),
            {
                "id": str(id),
            }
        )

        db.session.commit()

        return jsonify({"message": "Offer added successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred", "message": str(e)}), 500

