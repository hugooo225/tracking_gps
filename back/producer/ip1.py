from confluent_kafka import Producer
import time
import json
import generate_coordinates as g
import constants



# execution 
if __name__ == "__main__" :

    with open('../config.json','r') as config_file:
        conf = json.load(config_file)

    producer = Producer(conf)

    topic = 'coordinates'
    partition = 0  # Partition cible

    # Génération des points
    # create the graph and get the origin node
    graph = g.get_city_graph(constants.CITY)
    origin_node = g.get_random_node(graph)
    previous_node = origin_node
    visited_points = [previous_node]
    try : 
        while True:
            # generate visited points
            next_point = g.generate_point(graph, previous_node,visited_points)
            visited_points.append(next_point)
            # Envoie du message au Kafka
            producer.produce(topic, key="IP1", value=json.dumps(next_point).encode('utf-8'), partition=partition)
            producer.flush()
            print(f"Message envoyer : {next_point} (Partition: {partition})")
            time.sleep(1)
    except KeyboardInterrupt:
        print('Arrêt Producteur')