"""
Basic tests for the Online Library backend API
"""
import requests
import json

BACKEND_URL = "http://127.0.0.1:5000"

def test_get_all_media():
    """Test: GET /media - should return all media items"""
    print("Testing: GET all media...")
    response = requests.get(f"{BACKEND_URL}/media")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert isinstance(data, dict), "Response should be a dictionary"
    print("✓ GET all media works")

def test_add_media():
    """Test: POST /media - should create a new media item"""
    print("Testing: POST add media...")
    new_media = {
        "name": "Test Book",
        "author": "Test Author",
        "publication_date": "2025",
        "category": "Book"
    }
    response = requests.post(f"{BACKEND_URL}/media", json=new_media)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    data = response.json()
    assert data["status"] == "created", "Status should be 'created'"
    print("✓ POST add media works")

def test_get_specific_media():
    """Test: GET /media/<name> - should return specific media item"""
    print("Testing: GET specific media...")
    response = requests.get(f"{BACKEND_URL}/media/Test Book")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["name"] == "Test Book", "Media name should match"
    print("✓ GET specific media works")

def test_search_media():
    """Test: GET /media/search/<query> - should return matching media"""
    print("Testing: Search media (partial match)...")
    response = requests.get(f"{BACKEND_URL}/media/search/test")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert isinstance(data, dict), "Response should be a dictionary"
    print("✓ Search media works")

def test_borrow_media():
    """Test: POST /media/<name>/borrow - should mark media as borrowed"""
    print("Testing: Borrow media...")
    borrow_data = {
        "borrowed_by": "Test Student",
        "days": 7
    }
    response = requests.post(f"{BACKEND_URL}/media/Test Book/borrow", json=borrow_data)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "borrowed", "Status should be 'borrowed'"
    print("✓ Borrow media works")

def test_return_media():
    """Test: POST /media/<name>/return - should mark media as available"""
    print("Testing: Return media...")
    response = requests.post(f"{BACKEND_URL}/media/Test Book/return")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "returned", "Status should be 'returned'"
    print("✓ Return media works")

def test_delete_media():
    """Test: DELETE /media/<name> - should delete the media item"""
    print("Testing: DELETE media...")
    response = requests.delete(f"{BACKEND_URL}/media/Test Book")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "deleted", "Status should be 'deleted'"
    print("✓ DELETE media works")

def test_get_by_category():
    """Test: GET /media/category/<category> - should return media by category"""
    print("Testing: GET by category...")
    response = requests.get(f"{BACKEND_URL}/media/category/Book")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert isinstance(data, dict), "Response should be a dictionary"
    print("✓ GET by category works")

def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("Running Backend API Tests")
    print("=" * 50)
    print()
    
    try:
        test_get_all_media()
        test_add_media()
        test_get_specific_media()
        test_search_media()
        test_borrow_media()
        test_return_media()
        test_delete_media()
        test_get_by_category()
        
        print()
        print("=" * 50)
        print("✓ ALL TESTS PASSED!")
        print("=" * 50)
    except AssertionError as e:
        print()
        print("=" * 50)
        print(f"✗ TEST FAILED: {e}")
        print("=" * 50)
    except Exception as e:
        print()
        print("=" * 50)
        print(f"✗ ERROR: {e}")
        print("=" * 50)

if __name__ == "__main__":
    run_all_tests()
