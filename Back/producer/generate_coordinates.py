import os
import random as rd
import numpy as np #type: ignore
import matplotlib.pyplot as plt #type: ignore
import constants
import osmnx as ox #type: ignore
import folium #type: ignore


# get the coordinates of a node
def get_coordinates(graph, node) :
    node = graph.nodes[node]
    return {'latitude' : node["y"], 'longitude' : node["x"]}


# get the graph of the considered city
def get_city_graph(city) :
    return ox.graph_from_place(city, network_type='walk', simplify=True).to_undirected()


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
    
    return next_node


def generate_point(graph, previous_node,visited_points):
    # visiting the nodes
    neighbor = get_random_neighbor(graph, previous_node,visited_points)

    # convert the nodes into classic coordinates (latitude and longitude)
    neighbor = get_coordinates(graph, neighbor) 

    return neighbor


# generate visited points 
def generate_points(graph, origin_node, n_points) :

    # initialization
    nodes_list = [origin_node]

    # visiting the nodes
    for _ in range(n_points) :
        neighbor = get_random_neighbor(graph, nodes_list[-1], nodes_list)
        nodes_list.append(neighbor)

    # convert the nodes into classic coordinates (latitude and longitude)
    nodes_list = [get_coordinates(graph, node) for node in nodes_list]

    return nodes_list


# create the map to visualize the points (centered on the first node)
def create_map(graph, first_node) :
    latitude, longitude = get_coordinates(graph, first_node)
    return folium.Map(location=[latitude, longitude], zoom_start=14)


# add a list of points (latitude, longitude) to the map
def add_points_map(map, points_list) :

    # iterating through the points
    for point in points_list :

        # add the points on the map
        folium.CircleMarker(
            location = (point[0], point[1]),
            radius = 3,
            color = "blue",
            fill = True,
            fill_color = "blue"
        ).add_to(map)

    # add the lines on the map
    folium.PolyLine(points_list, color='red').add_to(map)

    return map


# save the map in HTML format
def save_map(map, path) :
    map.save(path)


# execution 
if __name__ == "__main__" :

    # create the graph and get the origin node
    graph = get_city_graph(constants.CITY)
    origin_node = get_random_node(graph)

    # generate visited points
    visited_points = generate_points(graph, origin_node, constants.N_POINTS)

    # create the map to display the points
    map = create_map(graph, origin_node)

    # add the points and the lines on the map
    map = add_points_map(map, visited_points)

    # save the map
    save_map(map, constants.MAP_PATH)
