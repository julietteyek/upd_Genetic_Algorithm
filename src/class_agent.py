"""
Genetic Algorithm - agent.py

This module contains the agent class, where all necessary\n
attributes for the agent object are initialized.


External Dependencies
---------------------
random
    random operations
numpy
    numerical operations
    data management

Authors
-------
    - [@julietteyek] (https://github.com/julietteyek)
    - [@Jxshyz] (https://github.com/Jxshyz)
    - [@Markomrnkvc] (https://github.com/Markomrnkvc)
    - [@SophZoe] (https://github.com/SophZoe)
    - [@Salt-is-leaving] (https://github.com/Salt-is-leaving)
"""
import random
import numpy as np
#from main import *
from main import VISUALIZE_POISON, ENERGYCOSTS_MOVEMENT, ENERGYCOSTS_REPRODUCTION, START_ENERGY
from main import WIDTH, HEIGHT, NUMBER_AGENTS, ROUNDS, FOOD_PERCENTAGE_BEGINNING,ADDITIONAL_FOOD_PERCENTAGE, SICKNESS_DURATION, VIGILANT_RADIUS
import main



#from CLASS_Board import Board
#from CLASS_Game import Game

# Global counter for the numbering of living beings
AGENTS_COUNTER = NUMBER_AGENTS

class Agent:
    """
     Class to represent an Agent in this simulated environment\n
     with various genetic traits and behaviours.

    Attributes
    ----------
    number : int
        unique identifier for agent
    \n
    energy : int
        current energy of agent
    \n
    genetic : dict
        genetic traits of agent
    \n
    position : touple
        current position of agent on board
    \n
    covered_distance : int
        distance covered by agent, starts at 0
    \n
    expelled : int
        number of times agent has been expelled, starts at 0
    \n
    flight_mode : int
        checks if agent is in flight mode, is set to 5
    \n
    consume_counter : int
        number of times agent has consumed food, starts at 0
    \n
    consumption_time : int
        time needed for agent to consume different food
    \n
    sick : bool
        initial health of agent, default set to false
    \n
    sickness_counter : int
        number of times agent has been sick, starts at 0
    \n
    sickness_duration : int
        duration of agents sickness
    \n
    previous_condition : int
        previous condition of agent, default set to none
    \n
    reproduction_counter : int
        number of times agent has reproduced with a partner, starts at 0
    \n
    parent_a : int
        unique identifier for agents parent A, default set to None
    \n
    parent_b : int
        unique identifier for agents parent B, default set to None

    Methods
    -------
    genedistribution():
        randomly sets the genedistribution of each agent based on predetermined genes
        in the global dictionary GENPOOL
    \n
    consuming_food(food_dict):
        adjusting health and status values of an agent based on food properties,
        which are predetermined through the food_dict and the agents unique genedistribution
    \n
    move(board):
        defines how the agent moves on the board considering the state it is in
        (linking the movement with it's energy, sickness and fleeing behaviour)
    \n
    move_towards(food_position):
        agent moves towards food_position to consume it
    \n
    random_move():
        agent moves randomly
    \n
    search_food(board):
        finding food is defined through the agents gene 'visibility_range', if food is found it
        will be consumed, considering the agents unique genedistributions and intelligence
        (disease risk) and the presence of aggressive agents
    \n
    check_for_aggressive_agents(board, x, y):
        ability of an agent to check for agressive agents within a specified search radius
        from its given location; is called in the search_food method
    \n
    check_for_sickness():
        checks if and how long the agent is sick, if False agents go back to previous condition
    \n
    move_away_from_aggressive(board, aggressive_agents):
        agent will move away from aggressive agents, if any were found
        (if any were found with the check_for_aggressive_agents method), its food consumption
        is being interrupted
    \n
    reproduce(board, partner):
        agents that occupy the same position and have suficcient energy have a chance to reproduce,
        success is dependant on tribal affiliation, with a guarantee if they are frome the same
        tribe. succesful reproduction results in a new agent inheriting genetic treits
        from both parents (calling the genedistribution_through_heredity method)
    \n
    genedistribution_through_heredity(parent1, parent2):
        determines the genetic traits of an agent created through reproduction, combining traits
        from both parents, some selected at random (tribe, intelligence), others calculated
    """

    def __init__(self, number, board):
        """
        Initializes all necessary attributes for the agent object

        Parameters
        ----------
        number : int
            unique identifier for agent

        Returns
        -------
        None
        """
        global AGENTS_COUNTER
        self.board = board
        self.sickness_counter = 0
        self.number = number
        self.energy = START_ENERGY
        self.genetic = {}
        self.genedistribution()
        self.position = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
        self.reproduction_counter = 0
        self.consume_counter = 0
        self.sick = False
        self.sickness_duration = 0
        self.flight_mode = 0
        self.previous_condition = None
        self.parent_a = None
        self.parent_b = None
        self.consumption_time = 0
        self.covered_distance = 0
        self.expelled = 0
        self.last_consumed_food_energy = 0
        self.gained_energy = 0

    def genedistribution(self):
        """
        randomly sets the genedistribution of each agent based on predetermined genes
        in the global dictionary GENPOOL

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        for gen, area in main.GENPOOL["Genes"].items():
            if isinstance(area[0], bool):
                self.genetic[gen] = random.choice(area)
                if self.genetic["Intelligent"] == True:
                    self.genetic["Aggressive"] = False
                else:
                    self.genetic["Aggressive"] = True
            else:
                self.genetic[gen] = random.randint(*area)

    def consuming_food(self, food_key):
        """
        adjusting health and status values of an agent based on food properties, \n
        which are predetermined through the food_dict and the agents unique genedistribution

        Parameters
        ----------
        food_key : key
            a key used as reference for food

        Returns
        -------
        None
        """
        self.consumption_time = main.FOOD[food_key]["consumption_time"] // max(1, self.genetic['Metabolism'])
        self.last_consumed_food_energy = main.FOOD[food_key]["Energy"]
        risk = main.FOOD[food_key]["disease_risk"]
        if self.genetic["Intelligent"] is False:
            if random.random() < risk * (1 - self.genetic["Resistance"] / 3):
                self.sick = True
                self.sickness_duration = SICKNESS_DURATION
                self.sickness_counter += 1

    def check_for_sickness(self):
        """
        checks if and how long the agent is sick, if False agents go back to previous condition

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        if self.sick:
            self.sickness_duration -= 1
            self.random_move()
            print("#####Krankes Lebewesen regeneriert!")
            if self.sickness_duration <= 0:
                self.sick = False
                self.random_move()
                print("Krankes Lebewesen ist nun wieder Gesund #####")

    def move(self, board):
        """
        defines how the agent moves on the board considering the state it is in

        Parameters
        ----------
        board : Any
            (right now board is not accessed in method)

        Returns
        -------
        Literal ["deceased"] if Agent died | None
        """
        if self.genetic["Intelligent"] is True and self.check_for_aggressive_agents():
            self.consumption_time = 0
            self.expelled += 1
            self.random_move()
        elif self.consumption_time > 0:
            # agent is consuming food
            self.consumption_time -= 1
            if self.consumption_time == 0:
                self.energy += self.last_consumed_food_energy
                self.gained_energy += self.last_consumed_food_energy
                self.consume_counter += 1
                self.last_consumed_food_energy = 0
        elif self.sick is True:
            self.check_for_sickness()
        else:
            # agent is looking for food, if its not fleeing or consuming
            closest_food, food_key = self.search_food(board)
            if closest_food is not None and main.FOOD[food_key]["disease_risk"] == 0 and self.genetic["Intelligent"] is True:
                # move agent towards closest_food
                self.move_towards(closest_food, food_key)
            elif closest_food is not None and self.genetic["Aggressive"] is True:
                self.move_towards(closest_food, food_key)
            else:
                # random move if there was no food to be found
                self.random_move()

            # reduces energy after next move
            if self.energy <= 0:
                return "deceased"

    def move_towards(self, food_position, food_key):
        """
        agent moves towards food_position to consume it

        Parameters
        ----------
        food_position : int

        Returns
        -------
        None
        """
        condition = self.genetic['Condition']
        food_x, food_y = food_position

        step_x = min(abs(food_x - self.position[0]), condition) * (1 if food_x > self.position[0] else -1)
        step_y = min(abs(food_y - self.position[1]), condition) * (1 if food_y > self.position[1] else -1)

        new_x = self.position[0] + step_x
        new_y = self.position[1] + step_y

        # Stellt sicher, dass die neue Position innerhalb der Grenzen des Spielfelds liegt
        new_x = max(0, min(WIDTH - 1, new_x))
        new_y = max(0, min(HEIGHT - 1, new_y))

        # Überprüft, ob das Zielnahrungsmittel an der neuen Position vorhanden ist
        if self.board.food[new_x, new_y] == food_key:
            self.consuming_food(food_key)
            self.board.food[new_x, new_y] = 0  # Entfernt das konsumierte Nahrungsmittel vom Board
        else:
            # Korrigiert die Position, falls das Nahrungsmittel nicht mehr vorhanden ist
            closest_food, _ = self.search_food(self.board)
            if closest_food:
                self.position = closest_food
            else:
                self.random_move()  # Führt eine zufällige Bewegung durch, wenn keine Nahrung gefunden wurde

        self.covered_distance += abs(step_x + step_y)
        self.position = (new_x, new_y)  # Aktualisiert die Position des Agenten

    def random_move(self):
        """
        agent moves randomly

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # agent makes a random move
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        new_x = max(0, min(WIDTH - 1, self.position[0] + dx))
        new_y = max(0, min(HEIGHT - 1, self.position[1] + dy))
        self.position = (new_x, new_y)
        self.covered_distance += abs(1 * self.genetic["Condition"])
        StepsTimesEnergycost = ENERGYCOSTS_MOVEMENT * abs(self.genetic["Condition"])
        self.energy -= StepsTimesEnergycost if not self.sick else StepsTimesEnergycost * 2



    def search_food(self, board):
        """
        finding food is defined through the agents gene 'visibility_range', if food is found it \n
        will be consumed, considering the agents unique genedistributions and intelligence \n
        (disease risk) and the presence of aggressive agents

        Parameters
        ----------
        board : Any

        Returns
        -------
        tuple [int, int] coordinates of the (consumed) food | None
        """
        closest_food = 0
        food_key = 0
        visibilityrange = self.genetic["Visibilityrange"]
        for dx in range(-visibilityrange, visibilityrange + 1):
            for dy in range(-visibilityrange, visibilityrange + 1):
                x, y = self.position[0] + dx, self.position[1] + dy
                if 0 <= x < WIDTH and 0 <= y < HEIGHT and board.food[x][y]:
                    closest_food = x, y
                    food_key = board.food[x][y]
                    board.food[x][y] = 0
                    self.energy += FOOD[food_key]["Energy"]
                    print(f"key is {food_key}")
                    print(f"closest food coordinates are {closest_food}")

                    return closest_food, food_key
                
        return None, None


    def check_for_aggressive_agents(self):
        """
        ability of an agent to check for agressive agents within a specified search radius \n
        any agent recognized as aggressive is appended to a list \n
        is called in the search_food method
        Parameters
        ----------
        board : Any
        Returns
        -------
        list() of aggressive agents
        """
        search_radius = VIGILANT_RADIUS
        min_x = max(0, self.position[0] - search_radius)
        max_x = min(self.board.width - 1, self.position[0] + search_radius)
        min_y = max(0, self.position[1] - search_radius)
        max_y = min(self.board.height - 1, self.position[1] + search_radius)

        for agent in self.board.agents_list:
            if agent != self and agent.genetic["Aggressive"]:
                if min_x <= agent.position[0] <= max_x and min_y <= agent.position[1] <= max_y:
                    return True  

        return False 

    def reproduce(self, partner, board):
        """
        agents in the same position on the board have a chance to reproduce,\n
        given certain circumstances (position, energy, tribe affiliation)\n
        every reproduction is tracked within the agent\n
        the child is added onto the board as an agent

        Parameters
        ----------
        board : Any
        partner : Any

        Returns
        -------
        None
        """
        global AGENTS_COUNTER
        if self.energy > ENERGYCOSTS_REPRODUCTION and self.position == partner.position:
            success_rate = 1 if self.genetic["Tribe"] == partner.genetic["Tribe"] else 0.3
            if random.random() < success_rate:
                AGENTS_COUNTER += 1
                child = Agent(AGENTS_COUNTER, self.board)
                child.genedistribution_through_heredity(self, partner)
                self.energy -= ENERGYCOSTS_REPRODUCTION
                self.reproduction_counter += 1
                partner.reproduction_counter += 1
                board.add_agent(child)

    def genedistribution_through_heredity(self, parent1, parent2):
        """
        determines the genetic traits of an agent created through reproduction,\n
        combining traits from both parents, some selected at random (tribe, intelligence),\n
        others calculated

        Parameters
        ----------
        parent1 : Any
        parent2 : Any

        Returns
        -------
        None
        """
        for gen in GENPOOL["Genes"]:
            if gen == "Tribe":
                self.genetic[gen] = random.choice([parent1.genetic[gen], parent2.genetic[gen]])
                self.parent_a = parent1.number
                self.parent_b = parent2.number
            elif gen == "Intelligent":
                self.genetic[gen] == random.choice([parent1.genetic[gen], parent2.genetic[gen]])
            else:
                weight = random.uniform(0, 1)
                gen_value = (weight * parent1.genetic[gen] + (1 - weight) * parent2.genetic[gen]) / 2
                self.genetic[gen] = int(round(gen_value, 3))
                if self.genetic["Intelligent"] == True:
                    self.genetic["Aggressive"] = False
                else:
                    self.genetic["Aggressive"] = True
