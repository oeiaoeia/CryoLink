from flask import jsonify, request

SETUP_SECRET = "change-this-to-a-long-random-string"


def register_setup_route(app):

    @app.route("/api/setup-db")
    def setup_database():

        if request.args.get("key") != SETUP_SECRET:
            return jsonify({"error": "Unauthorized"}), 401

        try:
            from init_db import init_db, seed_data
            init_db()
            seed_data()

            return jsonify({
                "success": True,
                "message": "Database initialized successfully."
            })

        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
