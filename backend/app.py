from flask import Flask, request, jsonify
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Path to JSON "database"
DATA_FILE = os.path.join(os.path.dirname(__file__), "database.json")


# ---------------------------------------------------------
# DATA HELPERS
# ---------------------------------------------------------
def load_data():
    """Load media data from JSON file."""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    """Save media data to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------------------------------------------------
# 1. GET ALL MEDIA
# ---------------------------------------------------------
@app.route("/media", methods=["GET"])
def get_all_media():
    """
    Returns all media items.
    Used by the frontend to populate the main list.
    """
    data = load_data()
    return jsonify(data)


# ---------------------------------------------------------
# 2. GET MEDIA BY CATEGORY
# ---------------------------------------------------------
@app.route("/media/category/<category>", methods=["GET"])
def get_media_by_category(category):
    """
    Returns all media items of a specific category
    (Book, Film, Series).
    """
    data = load_data()
    filtered = {
        name: item
        for name, item in data.items()
        if item.get("category") == category
    }
    return jsonify(filtered)


# ---------------------------------------------------------
# 3. SEARCH MEDIA (PARTIAL MATCH)
# ---------------------------------------------------------
@app.route("/media/search/<query>", methods=["GET"])
def search_media(query):
    """
    Search media items by partial name match (case-insensitive).
    """
    data = load_data()
    query = query.lower()

    results = {
        name: item
        for name, item in data.items()
        if query in name.lower()
    }
    return jsonify(results)


# ---------------------------------------------------------
# 4. GET SINGLE MEDIA ITEM
# ---------------------------------------------------------
@app.route("/media/<name>", methods=["GET"])
def get_single_media(name):
    """
    Returns full metadata for a single media item.
    Used for the details panel in the UI.
    """
    data = load_data()
    item = data.get(name)

    if item is None:
        return jsonify({"error": "Media not found"}), 404

    return jsonify(item)


# ---------------------------------------------------------
# 5. CREATE MEDIA ITEM (ADMIN / CODE USE)
# ---------------------------------------------------------
@app.route("/media", methods=["POST"])
def create_media():
    """
    Create a new media item.
    This endpoint exists for completeness, but the UI
    will not expose it.
    """
    data = load_data()
    new_item = request.get_json()

    required_fields = ["name", "author", "publication_date", "category"]
    for field in required_fields:
        if field not in new_item:
            return jsonify({"error": f"Missing field: {field}"}), 400

    new_item.setdefault("status", "available")
    new_item.setdefault("image", "")
    new_item.setdefault("borrowed_by", None)
    new_item.setdefault("borrow_date", None)
    new_item.setdefault("due_date", None)

    data[new_item["name"]] = new_item
    save_data(data)

    return jsonify({"status": "created"}), 201


# ---------------------------------------------------------
# 6. DELETE MEDIA ITEM (ADMIN / CODE USE)
# ---------------------------------------------------------
@app.route("/media/<name>", methods=["DELETE"])
def delete_media(name):
    """
    Delete a media item.
    Not exposed in the UI.
    """
    data = load_data()

    if name not in data:
        return jsonify({"error": "Media not found"}), 404

    data.pop(name)
    save_data(data)

    return jsonify({"status": "deleted"}), 200


# ---------------------------------------------------------
# 7. BORROW MEDIA ITEM
# ---------------------------------------------------------
@app.route("/media/<name>/borrow", methods=["POST"])
def borrow_media(name):
    """
    Borrow a media item.

    Expected JSON:
    {
        "borrowed_by": "Student Name",
        "days": 7
    }
    """
    data = load_data()

    if name not in data:
        return jsonify({"error": "Media not found"}), 404

    item = data[name]

    if item["status"] == "borrowed":
        return jsonify({"error": "Media already borrowed"}), 400

    payload = request.get_json()
    borrower = payload.get("borrowed_by")
    days = payload.get("days")

    if not borrower or not isinstance(days, int):
        return jsonify({"error": "Invalid borrow data"}), 400

    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=days)

    item["status"] = "borrowed"
    item["borrowed_by"] = borrower
    item["borrow_date"] = borrow_date.strftime("%Y-%m-%d")
    item["due_date"] = due_date.strftime("%Y-%m-%d")

    save_data(data)
    return jsonify({"status": "borrowed"}), 200


# ---------------------------------------------------------
# 8. RETURN MEDIA ITEM
# ---------------------------------------------------------
@app.route("/media/<name>/return", methods=["POST"])
def return_media(name):
    """
    Return a borrowed media item.
    """
    data = load_data()

    if name not in data:
        return jsonify({"error": "Media not found"}), 404

    item = data[name]

    if item["status"] != "borrowed":
        return jsonify({"error": "Media is not borrowed"}), 400

    item["status"] = "available"
    item["borrowed_by"] = None
    item["borrow_date"] = None
    item["due_date"] = None

    save_data(data)
    return jsonify({"status": "returned"}), 200


# ---------------------------------------------------------
# RUN SERVER
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
