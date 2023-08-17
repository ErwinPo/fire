import random

from mesa import Agent, Model
from mesa.space import SingleGrid
from mesa.time import RandomActivation

from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

from mesa.visualization.UserParam import Slider

from mesa.datacollection import DataCollector
from mesa.visualization.modules import ChartModule


class Tree(Agent):
    FINE = 0
    BURNING = 1
    BURNED_OUT = 2
    
    def __init__(self, model: Model, slide_tree_pos):
        super().__init__(model.next_id(), model)
        self.condition = self.FINE
        self.slide_tree_pos = slide_tree_pos
        
    def step(self):
        if self.condition == self.BURNING:
            for neighbor in self.model.grid.iter_neighbors(self.pos, moore=False): 
                if neighbor.condition == self.FINE and self.random.random()*100 <= self.slide_tree_pos:
                    neighbor.condition = self.BURNING
            self.condition = self.BURNED_OUT

class Forest(Model):
    def __init__(self, height=50, width=50, density=0.80, slide_tree_pos=0):
        super().__init__()
        self.schedule = RandomActivation(self)
        self.grid = SingleGrid(height, width, torus=False)
        for _,(x,y) in self.grid.coord_iter():
            if self.random.random() < density: #Se construten los arboles random tomando en cuenta una densidad
                tree = Tree(self,slide_tree_pos)
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
                           "slide_tree_pos": Slider("Probabilidad", 0, 0, 100, 1), "width":50, "height":50
                        })

server.port = 8522 # The default
server.launch()