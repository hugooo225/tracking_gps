from confluent_kafka import Producer
import time
import json
from function import *


def main():

    # get IP address
    IP = get_local_ip()

    with open('./config.json','r') as config_file:
        conf = json.load(config_file)

    producer = Producer(conf[0])
    
    topic = conf[1]['topic']
    partition = int(conf[1]['partition'])  # Partition cible

    # Génération des points
    # create the graph and get the origin node
    graph = get_city_graph(conf[1]['CITY'])

    origin_node = get_random_node(graph)

    previous_node = origin_node
    visited_points = [previous_node]
    try : 
        while True:
            # generate visited points
            next_point = generate_point(graph, previous_node,visited_points)
            visited_points.append(next_point)
            # Envoie du message au Kafka
            try : 
                producer.produce(topic, key=IP, value=json.dumps(next_point).encode('utf-8'), partition=partition)
                producer.flush()
                print(f"Message envoyer : {next_point} (Partition: {partition})")
                time.sleep(1)
            except Exception as e :
                print(f"Erreur : {e}")

    except KeyboardInterrupt:
        # with open('./config.json','w') as config_file:
        #     conf[1]['last_position'] = next_point
        #     json.dump(conf,config_file)
        print('\nArrêt Producteur')


# execution 
if __name__ == "__main__" :
    main()