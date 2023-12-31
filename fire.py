import random

from mesa import Agent, Model
from mesa.space import SingleGrid
from mesa.time import RandomActivation

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

from mesa.visualization.UserParam import Slider
from mesa.visualization.UserParam import Checkbox
from mesa.datacollection import DataCollector
from mesa.visualization.modules import ChartModule


class Tree(Agent):
    FINE = 0
    BURNING = 1
    BURNED_OUT = 2
            
    
    #Inicializamos los agentes con una probabilidad de propagación
    def __init__(self, model: Model, probability_of_spread, south_wind_speed, west_wind_speed, big_jumps):
        super().__init__(model.next_id(), model)
        self.condition = self.FINE
        self.south_wind_speed = south_wind_speed
        self.west_wind_speed = west_wind_speed
        self.probability_of_spread = probability_of_spread
        self.big_jumps = big_jumps
    def wind(self):
        (x,y) = self.pos
        if self.south_wind_speed > 0: 
            if self.west_wind_speed == 0:
                y = y + 1 
            elif self.west_wind_speed > 0:
                y = y + 1
                x = x + 1
            else:
                y = y + 1
                x = x - 1
        
        elif self.south_wind_speed < 0: 
            if self.west_wind_speed == 0:
                y = y - 1
            elif self.west_wind_speed < 0:
                y = y - 1
                x = x - 1
            else:
                y = y - 1
                x = x + 1
        
        elif self.south_wind_speed == 0: 
            if self.west_wind_speed > 0:
                x = x + 1
            elif self.west_wind_speed < 0:
                x = x - 1
                
        if self.model.grid.out_of_bounds((x,y)):
            return ([self.pos])
        else:
            return([(x,y)]) 
                
    def chispa(self):
        (x,y) = self.pos

        x = x + int(self.west_wind_speed/8)
        y = y + int(self.south_wind_speed/8)
                
        if self.model.grid.out_of_bounds((x,y)):
            return ([self.pos])
        else:
            return([(x,y)]) 
        


    def step(self):
        if self.condition == self.BURNING:
            for neighbor in self.model.grid.get_cell_list_contents(self.wind()):
                if neighbor.condition == self.FINE and self.random.random()*100 <= self.probability_of_spread: # Se mide la probabilidad de propagación por cada step y se compara con un valor porcentual
                    neighbor.condition = self.BURNING
            if self.big_jumps == True:
                for jumpneighbor in self.model.grid.get_cell_list_contents(self.chispa()):
                    if jumpneighbor.condition == self.FINE and self.random.random()*100 <= self.probability_of_spread: # Se mide la probabilidad de propagación por cada step y se compara con un valor porcentual
                        jumpneighbor.condition = self.BURNING
            self.condition = self.BURNED_OUT

class Forest(Model):
    def __init__(self, height=50, width=50, density=0.80, probability_of_spread=0, south_wind_speed = 0, west_wind_speed = 0, big_jumps = True):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.grid = SingleGrid(height, width, torus=False)
        for _,(x,y) in self.grid.coord_iter():
            if self.random.random() < density: #Se construten los arboles random tomando en cuenta una densidad
                tree = Tree(self,probability_of_spread, south_wind_speed, west_wind_speed, big_jumps)#Se agrega el valor del probability_of_spread
                if x == 0:
                    tree.condition = Tree.BURNING
                self.grid.place_agent(tree, (x,y))
                self.schedule.add(tree)
                self.datacollector = DataCollector({"Percent burned": lambda m: self.count_type(m, Tree.BURNED_OUT) / len(self.schedule.agents)})

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)
        
    @staticmethod   
    def count_type(model, condition):
        count = 0
        for tree in model.schedule.agents:
            if tree.condition == condition:
                count += 1
        return count
        

def agent_portrayal(agent):
    if agent.condition == Tree.FINE:
        portrayal = {"Shape": "circle", "Filled": "true", "Color": "Green", "r": 0.75, "Layer": 0}
    elif agent.condition == Tree.BURNING:
        portrayal = {"Shape": "circle", "Filled": "true", "Color": "Red", "r": 0.75, "Layer": 0}
    elif agent.condition == Tree.BURNED_OUT:
        portrayal = {"Shape": "circle", "Filled": "true", "Color": "Gray", "r": 0.75, "Layer": 0}
    else:
        portrayal = {}

    return portrayal

grid = CanvasGrid(agent_portrayal, 50, 50, 450, 450)

chart = ChartModule([{"Label": "Percent burned", "Color": "Black"}], data_collector_name='datacollector')

server = ModularServer(Forest,[grid, chart],"Forest",
                       {
                           "density": Slider("Tree density", 0.45, 0.01, 1.0, 0.01), "width":50, "height":50,
                           "probability_of_spread": Slider("Probabilidad", 0, 0, 100, 1), "width":50, "height":50,#Agregamos slider de la probabilidad de propagación
                            "south_wind_speed": Slider("Velocidad Sur-Norte", 0, -25, 25, 1), "width":50, "height":50,
                           "west_wind_speed": Slider("velocidad Oeste-Este", 0, -25, 25, 1), "width":50, "height":50,
                           "big_jumps": Checkbox("Big Jumps", True)
                        })

server.port = 8522 # The default
server.launch()
#Try