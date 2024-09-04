from flask import Flask, request, jsonify
from your_script import SecurityModel  # Import your script's classes/functions here

app = Flask(__name__)

# Initialize your model here
model = SecurityModel({'steps': 20})

@app.route('/update_agents', methods=['POST'])
def update_agents():
    # Get the data from the request
    data = request.json
   
    for agent_data in data['agents']: #definir que hacer en update de agentes
        agent_id = agent_data['id']
        new_position = agent_data['position']
 
    
    # se puede hacer un step
    model.step()
    
    # se genera el response
    response_data = {
        'status': 'success',
        'message': 'Agents updated successfully.'
    }
    
    return jsonify(response_data)

@app.route('/get_agent_status', methods=['GET'])
def get_agent_status():
    #se inicializa un array vacío para poner los estados de los agentes
    agent_status = []
    for agent in model.agents:
        status = {
            'id': agent.id,
            'position': agent.position,
            #agregar la info de los agentes
        }
        agent_status.append(status)
    
    return jsonify({'agents': agent_status})

if __name__ == '__main__':
    app.run(debug=True)  
