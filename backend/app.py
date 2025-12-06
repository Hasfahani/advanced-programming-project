from flask import Flask, request, jsonify
import json
import os

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

@app.route("/media", methods=["GET"])
def get_all_media():
    """1. List of all available media items."""
    data = load_data()
    return jsonify(data)

@app.route("/media/category/<category>", methods=["GET"])
def get_media_by_category(category):
    """2. List of media items in a specific category."""
    data = load_data()
    result = {name: item for name, item in data.items() if item.get("category") == category}
    return jsonify(result)

@app.route("/media/search/<query>", methods=["GET"])
def search_media(query):
    """3. Search for media items by partial name match (case-insensitive)."""
    data = load_data()
    query_lower = query.lower()
    # Find all items where the query appears in the name
    results = {name: item for name, item in data.items() 
               if query_lower in name.lower()}
    return jsonify(results)

@app.route("/media/<name>", methods=["GET"])
def get_media(name):
    """4. Display metadata of a specific media item."""
    data = load_data()
    item = data.get(name)
    if item is None:
        return jsonify({"error": "Media not found"}), 404
    return jsonify(item)

@app.route("/media", methods=["POST"])
def create_media():
    """5. Create a new media item."""
    data = load_data()
    new_item = request.get_json()

    # Simple validation
    required_fields = ["name", "author", "publication_date", "category"]
    for field in required_fields:
        if field not in new_item:
            return jsonify({"error": f"Missing field: {field}"}), 400

    # Set defaults for new fields
    if "status" not in new_item:
        new_item["status"] = "available"
    if "image" not in new_item:
        new_item["image"] = ""

    name = new_item["name"]
    data[name] = new_item
    save_data(data)
    return jsonify({"status": "created", "item": new_item}), 201

@app.route("/media/<name>", methods=["DELETE"])
def delete_media(name):
    """6. Delete a specific media item."""
    data = load_data()
    if name not in data:
        return jsonify({"error": "Media not found"}), 404
    deleted = data.pop(name)
    save_data(data)
    return jsonify({"status": "deleted", "item": deleted}), 200

@app.route("/media/<name>/borrow", methods=["PUT"])
def borrow_media(name):
    """7. Borrow a media item (change status to 'borrowed')."""
    data = load_data()
    if name not in data:
        return jsonify({"error": "Media not found"}), 404
    
    if data[name].get("status") == "borrowed":
        return jsonify({"error": "Media already borrowed"}), 400
    
    data[name]["status"] = "borrowed"
    save_data(data)
    return jsonify({"status": "borrowed", "item": data[name]}), 200

@app.route("/media/<name>/return", methods=["PUT"])
def return_media(name):
    """8. Return a borrowed media item (change status to 'available')."""
    data = load_data()
    if name not in data:
        return jsonify({"error": "Media not found"}), 404
    
    if data[name].get("status") != "borrowed":
        return jsonify({"error": "Media is not borrowed"}), 400
    
    data[name]["status"] = "available"
    save_data(data)
    return jsonify({"status": "returned", "item": data[name]}), 200

if __name__ == "__main__":
    # debug=True is handy while developing
    app.run(debug=True)
