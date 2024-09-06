from flask import Flask, request, jsonify
from flask_cors import CORS
from securityagents import SecurityModel  # Import your script's classes/functions here

app = Flask(__name__)
CORS(app,origins=["*"])

# Initialize your model here
model = SecurityModel({'steps': 20})

#@app.route('/initialize', methods=['POST'])
# def initialize_simulation():
 #   model.setup()  # Initialize the model with agents and grid
  #  return jsonify({'status': 'success', 'message': 'Simulation initialized.'})


@app.route('/update_agents', methods=['POST'])
def update_agents():
    model.setup()  # Ensure setup is called before accessing attributes
    model.step()
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data received'}), 400

    for agent_data in data.get('AgentList', []):
        agent_id = agent_data.get('agentType')
        new_position = agent_data.get('position', {})
        x = new_position.get('x')
        y = new_position.get('y')

        for agent in model.agents:
            if agent.id == agent_id:
                agent.position = [x, y]
                break
        else:
            return jsonify({'status': 'error', 'message': f'Agent with id {agent_id} not found'}), 404

    model.step()  # Proceed with simulation step

    return jsonify({'status': 'success', 'message': 'Agents updated successfully.'})

@app.route('/update_position', methods=['PUT'])
def update_position():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data received'}), 400

    agent_id = data.get('id')
    new_position = data.get('position', {})
    x = new_position.get('x')
    y = new_position.get('y')

    agent = next((a for a in model.agents if a.id == agent_id), None)
    if agent:
        agent.position = [x, y]
        return jsonify({'status': 'success', 'message': 'Position updated successfully.'})
    else:
        return jsonify({'status': 'error', 'message': f'Agent with id {agent_id} not found'}), 404


@app.route('/get_agent_status', methods=['GET'])
def get_agent_status():
    agent_status = []
    for agent in model.agents:
        status = {
            'id': agent.id,
            'position': agent.position,
            # Add additional agent information here if needed
        }
        agent_status.append(status)
    
    return jsonify({'agents': agent_status})

if __name__ == '__main__':
    app.run(debug=True)
