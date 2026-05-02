from flask import jsonify

def validate_required(data, fields):
    if not data:
        return jsonify({
            "error": "Request body must be valid JSON",
            "missing_fields": fields
        }), 422

    missing = [field for field in fields if field not in data or data[field] in [None, ""]]

    if missing:
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing
        }), 422

    return None