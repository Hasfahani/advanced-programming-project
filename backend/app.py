from flask import Flask, request, jsonify
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(__file__), "database.json")

def load_data():
    """Load media data from JSON file. If file does not exist, create an empty one."""
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
    """List of all available media items."""
    data = load_data()
    return jsonify(data)

# ---------------------------------------------------------
# 2. GET MEDIA BY CATEGORY
# ---------------------------------------------------------
@app.route("/media/category/<category>", methods=["GET"])
def get_media_by_category(category):
    """List of media items in a specific category."""
    data = load_data()
    result = {name: item for name, item in data.items() if item.get("category") == category}
    return jsonify(result)

# ---------------------------------------------------------
# 3. SEARCH (PARTIAL MATCH)
# ---------------------------------------------------------
@app.route("/media/search/<query>", methods=["GET"])
def search_media(query):
    """Search for media items by partial name match (case-insensitive)."""
    data = load_data()
    q = query.lower()
    results = {name: item for name, item in data.items() if q in name.lower()}
    return jsonify(results)

# ---------------------------------------------------------
# 4. GET SINGLE MEDIA ITEM
# ---------------------------------------------------------
@app.route("/media/<name>", methods=["GET"])
def get_media(name):
    """Display metadata of a specific media item."""
    data = load_data()
    item = data.get(name)
    if item is None:
        return jsonify({"error": "Media not found"}), 404
    return jsonify(item)

# ---------------------------------------------------------
# 5. CREATE MEDIA ITEM
# ---------------------------------------------------------
@app.route("/media", methods=["POST"])
def create_media():
    """Create a new media item."""
    data = load_data()
    new_item = request.get_json()

    # Required fields
    required = ["name", "author", "publication_date", "category"]
    for field in required:
        if field not in new_item:
            return jsonify({"error": f"Missing field: {field}"}), 400

    # Set defaults for new features
    new_item.setdefault("status", "available")
    new_item.setdefault("image", "")
    new_item.setdefault("borrowed_by", None)
    new_item.setdefault("borrow_date", None)
    new_item.setdefault("due_date", None)

    name = new_item["name"]
    data[name] = new_item
    save_data(data)
    return jsonify({"status": "created", "item": new_item}), 201

# ---------------------------------------------------------
# 6. DELETE MEDIA ITEM
# ---------------------------------------------------------
@app.route("/media/<name>", methods=["DELETE"])
def delete_media(name):
    data = load_data()
    if name not in data:
        return jsonify({"error": "Media not found"}), 404
    deleted = data.pop(name)
    save_data(data)
    return jsonify({"status": "deleted", "item": deleted}), 200

# ---------------------------------------------------------
# 7. BORROW MEDIA ITEM
# ---------------------------------------------------------
@app.route("/media/<name>/borrow", methods=["POST"])
def borrow_media(name):
    """
    Borrow a media item.
    Requires JSON:
    {
        "borrowed_by": "Student Name",
        "days": 7
    }
    """
    data = load_data()

    if name not in data:
        return jsonify({"error": "Media not found"}), 404

    item = data[name]

    if item.get("status") == "borrowed":
        return jsonify({"error": "Media already borrowed"}), 400

    payload = request.get_json()
    borrower = payload.get("borrowed_by")
    days = payload.get("days")

    if not borrower or not isinstance(days, int):
        return jsonify({"error": "Missing borrower name or days"}), 400

    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=days)

    item["status"] = "borrowed"
    item["borrowed_by"] = borrower
    item["borrow_date"] = borrow_date.strftime("%Y-%m-%d")
    item["due_date"] = due_date.strftime("%Y-%m-%d")

    save_data(data)
    return jsonify({"status": "borrowed", "item": item}), 200

# ---------------------------------------------------------
# 8. RETURN MEDIA ITEM
# ---------------------------------------------------------
@app.route("/media/<name>/return", methods=["POST"])
def return_media(name):
    data = load_data()

    if name not in data:
        return jsonify({"error": "Media not found"}), 404

    item = data[name]

    if item.get("status") != "borrowed":
        return jsonify({"error": "Media is not currently borrowed"}), 400

    # Reset borrow information
    item["status"] = "available"
    item["borrowed_by"] = None
    item["borrow_date"] = None
    item["due_date"] = None

    save_data(data)
    return jsonify({"status": "returned", "item": item}), 200

# ---------------------------------------------------------
# RUN APP
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
