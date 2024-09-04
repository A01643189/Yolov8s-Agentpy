# -*- coding: utf-8 -*-
"""SecurityAgents.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1kg3DClcAN8lqbiuPaMNNudUlg3UrmWdH
"""

#!pip install owlready2
#!pip install agentpy
#!pip install matplotlib
#!pip install IPython

import agentpy as ap
from owlready2 import *
#import matplotlib.pyplot as plt
#import IPython

onto = get_ontology("file://ontologia.owl")

"""**ONTOLOGY**"""

with onto:
  class Drone(Thing):
      pass

  class DroneStation(Thing):
      pass

  class Security(Thing):
      pass

  class SecurityList(Thing):
      pass

  class Camera(Thing):
      pass

  class CameraList(Thing):
      pass

  class Suspicious(Thing):
      pass

  class Obstacle(Thing):
      pass

  class Area(Thing):
      pass

  class AreaList(Thing):
      pass

  class Place(Thing):
      pass

  class Mobile(Thing): #Movable object or agent
      pass

  class has_suspicious(ObjectProperty):
      domain = [Mobile]
      range = [Suspicious]

  class has_obstacle(ObjectProperty):
      domain = [Obstacle]
      range = [Suspicious]

  class position_x(DataProperty, FunctionalProperty):
      domain = [Place]
      range = [int]

  class position_y(DataProperty, FunctionalProperty):
      domain = [Place]
      range = [int]




onto.save(file="my_ontology.owl")

"""**DRONE AGENT**"""

class DroneAgent(ap.Agent):
    """
    Attributes:
      agentType:
      position:
      direction:
      owl_instance:
      actions:
      rules:
    """

    def alert_coordinator(self, suspicious):
        coordinator = next(agent for agent in self.model.agents if isinstance(agent, CoordinatorAgent))
        coordinator.receive_alert(self, suspicious.position)

    def setup(self):
        self.agentType = 1
        self.position = [0, 0]
        self.direction = [0, 1]  # Default direction (East)
        self.actions = []  # Initialize the list of actions
        self.rules = []  # Initialize the list of rules
        self.owl_instance = onto.Drone(self.id)


    def move(self):
        self.position[0] += self.direction[0]
        self.position[1] += self.direction[1]
        self.owl_instance.position_x = self.position[0]
        self.owl_instance.position_y = self.position[1]
        print(f"Drone {self.id} moved to {self.position}.")

    def step(self, coordinator):
        self.move()
        self.see(self.model.grid, coordinator)

    def see(self, e, coordinator):
        perceived_objects = e.neighbors(self, 1)
        for obj in perceived_objects:
            if isinstance(obj, SuspiciousAgent):
                coordinator.report_threat(self.position, 'Drone')
                print(f"Drone {self.id} detected a suspicious figure.")

    # RULES

    def rule_1(self, act):
        '''
        Rule for detecting suspicious activity
        '''
        validate = [False, False]

        # First proposition: If there is a suspicious agent in the area
        for suspicious in self.model.suspicious:
            if suspicious.pos == self.position:
                validate[0] = True

        # Second proposition: If the action is check_suspicion
        if act == self.check_suspicion:
            validate[1] = True

        return sum(validate) == 2  # Check if both propositions are True

    def rule_2(self, act):
        # Rule logic to be implemented
        pass

    def next(self):
        for act in self.actions:
            for rule in self.rules:
                if rule(act):
                    act()

    # ACTIONS

    def move_N(self):
        self.direction = (-1, 0)  # North
        self.move()

    def move_S(self):
        self.direction = (1, 0)  # South
        self.move()

    def move_E(self):
        self.direction = (0, 1)  # East
        self.move()

    def move_W(self):
        self.direction = (0, -1)  # West
        self.move()

    def forward(self):
        """
        Forward Movement Function
        """
        self.model.grid.move_by(self, self.direction)

    def backward(self):
        """
        Backward Movement Function
        """
        opposite_direction = [-self.direction[0], -self.direction[1]]
        self.model.grid.move_by(self, opposite_direction)

    def turn(self):
        """
        Rotation Function (Clockwise)
        """
        if self.direction == (-1, 0):  # North
            self.direction = (0, 1)  # East
        elif self.direction == (0, 1):  # East
            self.direction = (1, 0)  # South
        elif self.direction == (1, 0):  # South
            self.direction = (0, -1)  # West
        elif self.direction == (0, -1):  # West
            self.direction = (-1, 0)  # North

"""**SECURITY GUARD AGENT**"""

class SecurityAgent(ap.Agent):

    def validate_threat(self, position):
        # Simplified validation logic
        for agent in self.model.agents:
            if isinstance(agent, SuspiciousAgent) and agent.position == position:
                print(f"Threat confirmed by security agent {self.id} at {position}.")
                return True
        print(f"No threat found by security agent {self.id} at {position}.")
        return False

    def inspect_area(self):
        threat_position = self.model.coordinator.get_threats()[0]['position']
        if self.validate_threat(threat_position):
            self.raise_alarm()

    def setup(self):
        self.agentType = 2
        self.owl_instance = onto.Security(f"Security_{self.id}")
        self.actions = [self.inspect_area, self.raise_alarm]
        self.rules = [self.rule_1]

    def see(self, e, coordinator):
        perceived_objects = e.neighbors(self, 1)
        for obj in perceived_objects:
            if isinstance(obj, SuspiciousAgent):
                coordinator.report_threat(self.position, 'Drone')
                print(f"Drone {self.id} detected a suspicious figure.")

    def step(self, coordinator):
        self.see(self.model.grid, coordinator)
        self.next()

    #RULES

    def rule_1(self, act):
        if self.owl_instance.has_suspicious:
            return act in [self.inspect_area, self.raise_alarm]
        return True

    def next(self):
        for act in self.actions:
            for rule in self.rules:
                if rule(act):
                    act()

    def take_control(self, drone):
        print(f"Security agent {self.id} takes control of drone {drone.id}.")
        drone.see(self.model.grid)
        self.inspect_area()

    def inspect_area(self):
        print(f"Security agent {self.id} inspects the area.")

    def raise_alarm(self):
        print(f"Security agent {self.id} raises the alarm.")

"""**CAMERA AGENT**"""

class CameraAgent(ap.Agent):
    def alert_coordinator(self, suspicious):
        coordinator = next(agent for agent in self.model.agents if isinstance(agent, CoordinatorAgent))
        coordinator.receive_alert(self, suspicious.position)

    def alert_drone(self, suspicious):
        drones = [agent for agent in self.model.agents if isinstance(agent, DroneAgent)]
        for drone in drones:
            drone.owl_instance.has_suspicious.append(suspicious.owl_instance)
            print(f"Drone {drone.id} has been alerted about a suspicious figure.")

        # Assuming alert_coordinator should be called as part of alert_drone
        coordinator = next(agent for agent in self.model.agents if isinstance(agent, CoordinatorAgent))
        coordinator.report_threat(self.position, 'Camera')
        print(f"Camera {self.id} alerted drones and security about a suspicious figure.")

    def setup(self):
        self.agentType = 3
        self.owl_instance = onto.Camera(f"Camera_{self.id}")

    def see(self, e, coordinator):
        perceived_objects = e.neighbors(self, 1)
        for obj in perceived_objects:
            if isinstance(obj, SuspiciousAgent):
                self.alert_drone(obj)
                self.alert_coordinator(obj)
                print(f"Camera {self.id} detected a suspicious figure.")

    def step(self, coordinator):
        self.see(self.model.grid, coordinator)
        self.next()  # This is a placeholder; implement next() as needed

    def next(self):
        pass  # Placeholder; implement next() as needed

"""**OBSTACLE AGENT**"""

class ObstacleAgent(ap.Agent):
    def setup(self):
        self.agentType = 4
        self.name = f"Obstacle_{self.id}"
        # Check if 'onto' and 'Obstacle' are defined correctly.

        print(f'onto: {onto}')
        print(f'onto.Obstacle: {onto.Obstacle}')
        self.owl_instance = onto.Obstacle(self.name)

"""**SUSPICIOUS AGENT**"""

class SuspiciousAgent(ap.Agent):
    def setup(self):
        self.agentType = 5
        self.name = f"Suspicious_{self.id}"
        self.owl_instance = onto.Suspicious(self.name)

"""**SECURITY MODEL**"""

class SecurityModel(ap.Model):

    class CoordinatorAgent:
        def __init__(self):
            self.detected_threats = []

        def report_threat(self, position, agent_type):
            threat_info = {'position': position, 'reported_by': agent_type}
            if threat_info not in self.detected_threats:
                self.detected_threats.append(threat_info)
                print(f"Threat reported by {agent_type} at position {position}.")

        def get_threats(self):
            return self.detected_threats

    def setup(self):
        self.coordinator = self.CoordinatorAgent()

        # Create agents
        self.agents = ap.AgentList(self, 1, DroneAgent)
        self.agents += ap.AgentList(self, 1, SecurityAgent)
        self.agents += ap.AgentList(self, 2, CameraAgent)
        self.agents += ap.AgentList(self, 2, ObstacleAgent)
        self.agents += ap.AgentList(self, 1, SuspiciousAgent)

        # Initialize the grid and add agents
        self.grid = ap.Grid(self, [10, 10], track_empty=True)
        self.grid.add_agents(self.agents, random=True)

    def step(self):
        for agent in self.agents:
            if hasattr(agent, 'step'):
                agent.step(self.coordinator)

parameters = {
    'steps': 20,

}

model = SecurityModel(parameters)
results = model.run()

# Función de animaci