#!pip install owlready2
#!pip install agentpy
#!pip install matplotlib
#!pip install IPython

import agentpy as ap
from owlready2 import *
import matplotlib.pyplot as plt
import IPython
import heapq
import random

onto = get_ontology("file://ontologia.owl")

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

  class is_thread(ObjectProperty):
      domain = [Suspicious]
      range = [bool]





onto.save(file="my_ontology.owl")

class DroneAgent(ap.Agent):
    def setup(self):
        super().setup()
        self.agentType = 1
        self.position = [0, 0]
        self.direction = [0, -1]  # Default direction (East)
        self.owl_instance = onto.Drone(self.id)
        self.target = None
        self.path_to_target = []

    def set_target(self, position):
        self.target = position
        self.path_to_target = self.find_path(position)
        if not self.path_to_target:
            print(f"No path found from {self.position} to {position}")
        else:
            print(f"Path set from {self.position} to {position}")

    def move(self):
        print(f"Attempting to move from {self.position}. Path: {self.path_to_target}")  # Debug print
        if self.path_to_target and len(self.path_to_target) > 0:
            next_pos = self.path_to_target.pop(0)
            if next_pos == tuple(self.position):
                print("Next position is the same as current position, skipping...")
                if self.path_to_target:
                    next_pos = self.path_to_target.pop(0)
            print(f"Moving to next position: {next_pos}")  # Debug print
            self.model.grid.move_to(self, next_pos)
            self.position = list(next_pos)
            print(f"Moved to {self.position}.")  # Debug print
            if self.position == self.target:
                print(f"Reached the target at {self.position}. Stopping.")
                self.path_to_target = []  # Clear the path to stop the drone


    def step(self, coordinator):
        if self.position == self.target:
            print(f"Drone {self.id} has reached its target at {self.position}.")
            self.detect_suspicious(coordinator)  # Perform regular checks for suspicious activity
        if self.path_to_target:
            self.move()  # Continue moving towards the target
        if not self.path_to_target:
            print(f"Drone {self.id} has no path to the target. Setting a new target.")
            self.set_target([0, 2])
            self.move()  # Continue moving towards the target

    def detect_suspicious(self, coordinator):
        neighbors = self.model.grid.neighbors(self, distance=1)
        for agent in neighbors:
            if isinstance(agent, SuspiciousAgent) and agent.owl_instance.is_threat:
                print(f"Drone {self.id} detected suspicious activity at {agent.position}.")
                self.set_target(agent.position)
                self.alert_coordinator(coordinator, agent)
            else:
                self.set_target([0, 2])
                self.move()
                print(f"Drone {self.id} did not detect suspicious activity.")

    def alert_coordinator(self, coordinator, suspicious_agent):
        if suspicious_agent.owl_instance.is_threat:
            coordinator.receive_alert(self, suspicious_agent.position)
            print(f"Drone {self.id} has reported a suspicious threat at {suspicious_agent.position}")
        else:
            print(f"Drone {self.id} did not report a suspicious threat.")


    def find_path(self, target):
        start = tuple(self.position)
        goal = tuple(target)
        obstacles = {tuple(agent.position) for agent in self.model.agents if isinstance(agent, ObstacleAgent)}
        return self.a_star_search(start, goal, obstacles)

    def a_star_search(self, start, goal, obstacles):
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}
        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == goal:
                return self.reconstruct_path(came_from, current)
            for neighbor in self.get_neighbors(current):
                if tuple(neighbor) in obstacles:
                    continue
                tentative_g_score = g_score[current] + 1
                if tuple(neighbor) not in g_score or tentative_g_score < g_score[tuple(neighbor)]:
                    came_from[tuple(neighbor)] = current
                    g_score[tuple(neighbor)] = tentative_g_score
                    f_score[tuple(neighbor)] = tentative_g_score + heuristic(tuple(neighbor), goal)
                    heapq.heappush(open_set, (f_score[tuple(neighbor)], tuple(neighbor)))
        return []

    def get_neighbors(self, position):
        neighbors = [
            (position[0] + 1, position[1]),  # South
            (position[0] - 1, position[1]),  # North
            (position[0], position[1] + 1),  # East
            (position[0], position[1] - 1)   # West
        ]
        return [n for n in neighbors if 0 <= n[0] < self.model.grid.shape[0] and 0 <= n[1] < self.model.grid.shape[1]]

    def reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.insert(0, current)
        # Remove the starting position if it is the first in the path and not the only element
        if len(total_path) > 1 and total_path[0] == tuple(self.position):
            total_path.pop(0)
        return total_path


class SecurityAgent(ap.Agent):
    def setup(self):
        self.agentType = 2
        self.owl_instance = onto.Security(f"Security_{self.id}")
        self.is_suspicious_active = False

    def step(self, coordinator):
        if self.is_suspicious_active:
            self.move_drone(self, coordinator)
            self.evaluate_threats(coordinator)  # Check for threats and command drones
        else:
            self.move_drone(self, coordinator)
        

    def move_drone(self, coordinator):
        if self.is_suspicious_active:
            print(f"Drone is moving to a suspicious thread")
        else:
            print(f"Security Agent {self.id} is moving to a drone station.")


    def validate_threat(self, position):
        # Example validation logic, can be more complex
        for agent in self.model.agents:
            if isinstance(agent, SuspiciousAgent) and tuple(agent.position) == tuple(position):
                return True
        return False


class CameraAgent(ap.Agent):
    def setup(self):
        self.agentType = 3
        self.owl_instance = onto.Camera(f"Camera_{self.id}")

    def see(self, coordinator):  # Now accepts 'coordinator' parameter
        # Use 'coordinator' here if needed, for now, it will be passed but not used
        perceived_objects = self.model.grid.neighbors(self, distance=2)
        for obj in perceived_objects:
            if isinstance(obj, SuspiciousAgent):
              if obj.is_suspicious_active:
                  print(f"Camera {self.id} detected a suspicious figure at {obj.position}.")
                  self.alert_drone(obj)
                  self.alert_coordinator(obj, coordinator)  # Assuming alert_coordinator now also needs the coordinator

    def alert_drone(self, suspicious_agent):
        drones = [agent for agent in self.model.agents if isinstance(agent, DroneAgent)]
        for drone in drones:
            drone.set_target(suspicious_agent.position)  # Assuming set_target function exists in DroneAgent
            print(f"Camera {self.id} is alerting Drone {drone.id} about a threat at {suspicious_agent.position}")

    def alert_coordinator(self, suspicious_agent, coordinator):
        if suspicious_agent.owl_instance.is_threat:
            coordinator.receive_alert(self, suspicious_agent.position)
            print(f"Camera {self.id} has reported a suspicious threat at {suspicious_agent.position}")

    def step(self, coordinator):
        self.see(coordinator)  # Ensure coordinator is passed
        self.next()

    def next(self):
        pass  # Placeholder for future implementation


class ObstacleAgent(ap.Agent):
    def setup(self):
        self.agentType = 4
        self.name = f"Obstacle_{self.id}"

        print(f'onto: {onto}')
        print(f'onto.Obstacle: {onto.Obstacle}')
        self.owl_instance = onto.Obstacle(self.name)

    def step(self, *args, **kwargs):
        # Accepts any number of positional and keyword arguments without using them
        pass

class SuspiciousAgent(ap.Agent):
    def setup(self):
        self.agentType = 5
        self.name = f"Suspicious_{self.id}"
        self.owl_instance = onto.Suspicious(self.name)
        # self.owl_instance.is_threat = random.choice([True, False])
        self.owl_instance.is_threat = False
        self.is_suspicious_active = True

    def step(self, *args, **kwargs):
        # Accepts any number of positional and keyword arguments without using them
        pass

class DroneStationAgent(ap.Agent):
    def setup(self):
        self.agentType = 6
        self.name = f"DroneStation_{self.id}"
        self.owl_instance = onto.DroneStation(self.name)

    def step(self, *args, **kwargs):
        # Accepts any number of positional and keyword arguments without using them
        pass

class CentralCoordinator:
    def __init__(self):
        self.detected_threats = []

    def receive_alert(self, agent, position):
        print(f"Alert received from {type(agent).__name__} {agent.id} at position {position}")
        
        self.detected_threats.append({'agent_id': agent.id, 'position': position, 'agent_type': type(agent).__name__})


class SecurityModel(ap.Model):

    def setup(self):
        self.coordinator = CentralCoordinator()

        # Initialize the grid and add agents
        self.grid = ap.Grid(self, [10, 10], track_empty=True)

        # Create agents
        self.agents = ap.AgentList(self, 1, DroneAgent)
        self.agents += ap.AgentList(self, 1, SecurityAgent)
        self.agents += ap.AgentList(self, 3, CameraAgent)
        self.agents += ap.AgentList(self, 30, ObstacleAgent)
        self.agents += ap.AgentList(self, 1, SuspiciousAgent)
        self.agents += ap.AgentList(self, 1, DroneStationAgent)

        # Define positions for agents
        drone_positions = [(9, 7)]
        security_positions = [(1, 7)]
        camera_positions = [(4, 7), (6, 2), (5, 1)]
        obstacle_positions = [(9, 5), (8, 5), (7, 5), (9, 9), (8, 9), (7, 9), (6, 9), (5, 9), (4, 9), (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (0, 4), (1, 4), (2, 4),
                              (7, 4), (7, 3), (7, 2), (7, 1), (7, 0), (3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 4), (6, 0)]
        suspicious_positions = [(5, 4)]
        drone_station_positions = [(0, 2)]

        positions = drone_positions + security_positions + camera_positions + obstacle_positions + suspicious_positions + drone_station_positions

        self.grid.add_agents(self.agents, positions=positions, random=False)

        # Manually assign positions to agents that require it
        for agent, pos in zip(self.agents, positions):
            agent.position = pos

        self.drone_agent = self.agents[0]  # Assuming the first agent is the DroneAgent
        self.drone_station = self.agents[-1]  # Assuming the last agent is the DroneStationAgent

    def step(self):
        for agent in self.agents:
            agent.step(self.coordinator)  # Pass the coordinator to each agent’s step function

        # Optionally, add checks to determine if the simulation should stop
        if self.all_drones_at_targets():
            print("All drones have reached their targets. Simulation ending.")
            self.stop()

    def all_drones_at_targets(self):
        return all(drone.position == drone.target for drone in self.agents if isinstance(drone, DroneAgent))

    def get_neighbors(self, agent, radius=1, moore=True):
        x, y = agent.position
        neighbors = []
        width, height = self.grid.shape  # Correct way to get grid dimensions

        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if moore or abs(dx) + abs(dy) <= radius:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:  # Check boundaries
                        # Directly accessing the list of agents in the cell
                        for neighbor in self.grid[nx, ny]:
                            neighbors.append(neighbor)
        return neighbors


parameters = {
    'steps': 50,

}


def animation_plot(model, ax):
    agent_type_grid = model.grid.attr_grid('agentType')
    ap.gridplot(agent_type_grid, cmap='Accent', ax=ax)
    ax.set_title(f"Security Model\nTime-step: {model.t}")

# Configuración de la visualización
fig, ax = plt.subplots()
model = SecurityModel(parameters)
animation = ap.animate(model, fig, ax, animation_plot)
IPython.display.HTML(animation.to_jshtml())