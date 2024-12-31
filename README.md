# Projet d'Architecture Microservices : Tracking GPS

Ce projet permet de suivre les déplacements de deux utilisateurs fictifs sur une carte au sein de la ville de Pau. 
Ce travail a été réalisé par Clément MOUNIC, Achraf MAZOUARA et Hugo HERSANT dans le cadre de notre formation à CY Tech. 

## Installation et lancement

1. Clonez le dépôt en local :

``` git clone https://github.com/hugooo225/tracking_gps.git ```

2. Lancez les conteneurs :

``` docker compose up --build ```

3. Accédez à l'application dans votre navigateur à l'adresse :

``` localhost:5371 ```

Sur cette page, il est possible de cliquer sur les utilisateurs pour voir leur IP respective. 

4. Pour arrêter les conteneurs et supprimer les volumes associés :

``` docker compose down -v ```

## Fonctionnalités

La base de données est automatiquement initialisée et prête à être utilisée. Elle est petit à petit remplie par des coordonnées GPS fictives. 

Ces coordonnées sont générées aléatoirement mais de manière réaliste puisque l'utilisateur ne peut se déplacer que sur les noeuds consécutifs du graphe routier de la ville de Pau, récupéré en amont.

Pour gérer les consumers et producers, vous pouvez utiliser les commandes suivantes : 

- Eteindre un consumer ou un producer :

``` docker stop {container} ```

- Rallumer un consumer ou un producer :

``` docker start {container} ```

Avec {container} valant "producer", "producer_2" ou "consumer". 

Vous pouvez également installer LazyDocker via la commande : 

``` curl https://raw.githubusercontent.com/jesseduffield/lazydocker/master/scripts/install_update_linux.sh | bash ```

