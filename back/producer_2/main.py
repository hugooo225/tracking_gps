from confluent_kafka import Producer
import time
import json
from function import *

# main function
def main():

    # get IP address
    IP = get_local_ip()

    # get informations from config.json
    with open('./config.json','r') as config_file:
        conf = json.load(config_file)
    producer = Producer(conf[0])
    topic = conf[1]['topic']
    partition = int(conf[1]['partition'])

    # create the graph and get the origin node
    graph = get_city_graph(conf[1]['CITY'])
    origin_node = get_random_node(graph)

    # initialisation
    previous_node = origin_node
    visited_points = [previous_node]
    while True:

        # generate visited points
        next_point = get_random_neighbor(graph, previous_node, visited_points)
        coordinates = get_coordinates(graph, next_point)
        previous_node = next_point

        # send message to Kafka
        try : 
            producer.produce(topic, key=IP, value=json.dumps(coordinates).encode('utf-8'), partition=partition)
            producer.flush()
            print(f"Message envoyé : {coordinates} (Partition: {partition})")
            time.sleep(1)
        except Exception as e :
            print(f"Erreur : {e}")


# execution 
if __name__ == "__main__" :
    main()