import random as rd
import numpy as np #type: ignore
import matplotlib.pyplot as plt #type: ignore
import constants

# generate new coordinates given the previous ones
def get_next_coordinates(prev_coords, dist) :

    # if we consider the previous point as the origin of an euclidean plane and (x1, y1) the new coordinates, we have :
    # y1 = y0 + sqrt(d² - (x0 - x1)²) => x1 > x0 - d
    # (with d the distance between the two points)
    # so we just have to generate a random number for x1
    x0, y0 = prev_coords
    x1 = rd.uniform(x0 - dist, x0 + dist)
    y1 = y0 + rd.choice([-1, 1])*np.sqrt(dist**2 - (x0 - x1)**2)

    return (x1, y1)
    

# generate a set of coordinates
def generate_coordinates(n, dist) :

    # initiation
    coord_list = [constants.BASE_COORDINATES]

    # build the list
    for _ in range(n) :
        new_coord = get_next_coordinates(coord_list[-1], dist)
        coord_list.append(new_coord)
    
    return coord_list


# display the coordinates list
def display_coordinates(coord_list) :

    # list of latitudes and longitudes
    latitudes_list = [coord[0] for coord in coord_list]
    longitudes_list = [coord[1] for coord in coord_list]

    # creation of the figure
    plt.figure(figsize=(10, 6))
    plt.plot(longitudes_list, latitudes_list, marker='o', label="Trajet")
    plt.scatter(longitudes_list, latitudes_list, color='red', zorder=5, label="Points")
    plt.grid(True)
    plt.axis("equal")

    # display the figure
    plt.show()


# execution 
if __name__ == "__main__" :

    # generate the list of coordinates
    coord_list = generate_coordinates(50, constants.DIST_COORDS)

    # display the generated points
    display_coordinates(coord_list)