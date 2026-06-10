from flask import Flask, jsonify

app = Flask(__name__)

# Mock data simulating a flight manifest
MOCK_MANIFEST = [
    {
        "package_id": "PKG-001",
        "flight_number": "AA123",
        "destination": "NEW YORK",
        "status": "pending"
    },
    {
        "package_id": "PKG-002",
        "flight_number": "BA456",
        "destination": "LONDON",
        "status": "pending"
    },
    {
        "package_id": "PKG-003",
        "flight_number": "DL789",
        "destination": "TOKYO",
        "status": "pending"
    }
]

@app.route('/manifest', methods=['GET'])
def get_manifest():
    return jsonify(MOCK_MANIFEST)

if __name__ == '__main__':
    # Run on a different port than the FastAPI backend to avoid conflicts
    print("Starting Mock Manifest API on port 5000...")
    app.run(port=5000)
