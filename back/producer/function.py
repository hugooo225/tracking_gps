import random as rd
import osmnx as ox
import socket

# get the coordinates of a node
def get_coordinates(graph, node) :
    node = graph.nodes[node]
    return {'latitude' : node["y"], 'longitude' : node["x"]}

# get the graph of the considered city
def get_city_graph(city) :
    city_name = city.split(",")[0].lower().strip()
    try :
        graph = ox.load_graphml(f"{city_name}.graphml")
    except FileNotFoundError :
        graph = ox.graph_from_place(city, network_type='drive', simplify=True).to_undirected()
    return graph

# get a random node from the graph
def get_random_node(graph) :
    return rd.choice(list(graph.nodes()))

# get the neighbors of a given node
def get_neighbors(graph, node) :
    return list(graph.neighbors(node))

# get a random neighbor of a given node
def get_random_neighbor(graph, node, visited_points) :

    # creation of neighbors lists
    neighbors_list = get_neighbors(graph, node)
    filtered_neighbors_list = [neighbor for neighbor in neighbors_list if neighbor not in visited_points]

    # selection of the next node
    if filtered_neighbors_list != [] :
        next_node = rd.choice(filtered_neighbors_list)
    else :
        next_node = rd.choice(neighbors_list)

    # adding the next point to visited nodes
    if next_node not in visited_points :
        visited_points.append(next_node)

    return next_node

# get a local IP address
def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80)) 
            ip_address = s.getsockname()[0]
        return ip_address
    except Exception as e:
        return f"Erreur : {e}"  