from typing import Union
from fastapi import FastAPI
from src.simulator.SUMOSimulator import SUMOSimulator
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Response
import threading
import src.graph.algorithms.Dijkstra as Dijkstra
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from src.graph.algorithms.Greedy import get_greedy_track
from src.graph.algorithms.AStar import get_optimal_path, Strategy
from src.graph.obj.Graph import Graph


app = FastAPI()

app.mount("/ux", StaticFiles(directory="ux"), name="ux")


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

simulation_thread = None

def get_visits_from_query(graph: Graph, starting_v: str, ending_v: str, visits: str) -> list:
    visit_ids = visits.split(',')
    if len(visits) == 0:
        visit_ids = []
    if starting_v not in graph.vertices.keys():
        return []
    v_i = graph.vertices[starting_v]
    if ending_v not in graph.vertices.keys():
        return []
    
    v_f = graph.vertices[ending_v]
    
    for v in visit_ids:
        if v not in graph.vertices.keys():
            return []

    v_visits = [v_i]
    for v in visit_ids:
        v_visits.append(graph.vertices[v])
    v_visits.append(v_f)

    return v_visits

@app.get('/getDijkstraPath')
def get_dijkstra_path(starting_v: str, ending_v: str):
    graph = SUMOSimulator.get_instance().get_graph()
    if starting_v not in graph.vertices.keys():
        return []
    v_i = graph.vertices[starting_v]
    if ending_v not in graph.vertices.keys():
        return []
    v_f = graph.vertices[ending_v]
    path = Dijkstra.get_shortest_path(graph, v_i, v_f)
    print(path)
    return path

@app.get('/greedyPath')
def greedy_path(starting_v: str, ending_v: str, visits: str):
    graph = SUMOSimulator.get_instance().get_graph()
    v_visits = get_visits_from_query(graph, starting_v, ending_v, visits)
    path = get_greedy_track(graph, v_visits)
    return path

@app.get('/AStarShortest')
def astar_shortest(starting_v: str, ending_v: str, visits: str):
    graph = SUMOSimulator.get_instance().get_graph()
    v_visits = get_visits_from_query(graph, starting_v, ending_v, visits)
    path = get_optimal_path(graph, v_visits, Strategy.SHORTEST_PATH)
    return path

@app.get('/AStarWaitingTime')
def astar_waiting_time(starting_v: str, ending_v: str, visits: str):
    global simulating
    if not SUMOSimulator.get_instance().traci_running:
        return []
    graph = SUMOSimulator.get_instance().get_graph()
    v_visits = get_visits_from_query(graph, starting_v, ending_v, visits)
    path = get_optimal_path(graph, v_visits, Strategy.TRAFFIC)
    return path

@app.get('/AStarAvgSpeed')
def astar_avg_speed(starting_v: str, ending_v: str, visits: str):
    global simulating
    if not SUMOSimulator.get_instance().traci_running:
        return []
    graph = SUMOSimulator.get_instance().get_graph()
    v_visits = get_visits_from_query(graph, starting_v, ending_v, visits)
    path = get_optimal_path(graph, v_visits, Strategy.SHORTEST_PATH)
    return path

@app.get('/startSimulation')
def start_simulation():
    global simulation_thread  # Agregar esta línea para referenciar a la variable global
    global simulating
    simulator = SUMOSimulator.get_instance()
    simulating = simulator.traci_running
    if simulating:
        return
    simulation_thread = threading.Thread(target=simulator.simulate)  # Corregir el argumento `target`
    simulation_thread.start()
    simulating = True

@app.get('/closeSimulation')
def close_simulation():
    global simulation_thread  # Agregar esta línea para referenciar a la variable global
    simulator = SUMOSimulator.get_instance()
    simulating = simulator.traci_running
    if not simulating:
        return
    simulator.close_traci()

@app.get('/graph')
def get_graph():
    simulator = SUMOSimulator.get_instance()
    graph = simulator.get_graph()
    return graph.__json__()

@app.get("/")
def root():
    with open("ux/index.html", "r") as file:  # Corregir la ruta del archivo
        content = file.read()
    return HTMLResponse(content=content)
