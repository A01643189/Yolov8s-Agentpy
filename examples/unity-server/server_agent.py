from flask import Flask, request, jsonify
import logging
from securityagents import SecurityModel  # Assuming the simulation code is named security_simulation.py

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    try:
        # Extract JSON data from the POST request
        input_data = request.get_json()

        # Extract parameters from the input data
        steps = input_data['steps']
        drone_positions = input_data['drone_positions']
        security_positions = input_data['security_positions']
        camera_positions = input_data['camera_positions']
        obstacle_positions = input_data['obstacle_positions']
        suspicious_positions = input_data['suspicious_positions']
        drone_station_positions = input_data['drone_station_positions']

        # Initialize simulation parameters
        parameters = {
            'steps': steps,
            'drone_positions': drone_positions,
            'security_positions': security_positions,
            'camera_positions': camera_positions,
            'obstacle_positions': obstacle_positions,
            'suspicious_positions': suspicious_positions,
            'drone_station_positions': drone_station_positions,
        }

        # Initialize and run the security model
        model = SecurityModel(parameters)
        model.run()  # Replace `run_model()` with `run()`

        # Gather results
        results = {
            "final_state": model.agent_data,  # Assuming this collects final states or other data
            "messages": ["Simulation completed successfully"]
        }

        # Return JSON response
        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_agent_data', methods=['GET'])
def get_agent_data():
    global model
    try:
        if model is None:
            return jsonify({"error": "Simulation has not been run yet"}), 400

        # Return the agent data from the SecurityModel
        results = {
            "agent_data": model.agent_data
        }

        return jsonify(results), 200

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return jsonify({"error": str(e)}), 500


# Simple GET request to test the server
@app.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({"message": "Server is running"}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
