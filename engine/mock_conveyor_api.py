from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "Mock Conveyor API is running. Trigger /halt to test."}), 200

@app.route('/halt', methods=['POST'])
def halt_conveyor():
    data = request.json or {}
    package_id = data.get("package_id", "UNKNOWN")
    print(f"*** MOCK HARDWARE TRIGGERED: Conveyor HALTED for package {package_id} ***")
    return jsonify({"status": "halted", "package": package_id}), 200

if __name__ == '__main__':
    print("Starting Mock Conveyor Hardware API on port 5001...")
    app.run(port=5001)
