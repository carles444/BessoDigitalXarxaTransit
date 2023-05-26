from typing import Union
from fastapi import FastAPI
from src.simulator.SUMOSimulator import SUMOSimulator
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Response
import threading
import src.graph.algorithms.Dijkstra as Dijkstra

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

simulation_thread = None

@app.get('/getDijkstraPath')
def get_dijkstra_path(starting_v: str, ending_v: str):
    graph = SUMOSimulator.get_instance().get_graph()
    path = Dijkstra.get_shortest_path(graph, starting_v, ending_v)
    return path

@app.get('/startSimulation')
def start_simulation():
    simulator = SUMOSimulator.get_instance()
    simulation_thread = threading.Thread(simulator.simulate)
    simulation_thread.start()

@app.get('/')
def index(response: Response):
    # response.headers["Access-Control-Allow-Origin"] = origins[0]
    simulator = SUMOSimulator.get_instance()
    graph = simulator.get_graph()
    return graph.__json__()