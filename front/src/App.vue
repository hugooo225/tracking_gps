<script setup>
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
</script>

<template><div id="map"></div></template>

<script>

export default {
    name: 'Map',
    mounted() {

        // observer 
        function observer(url, circlesMap) {
            const ws = new WebSocket(url);
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                console.log(data);

                // new IP : creation of a new circle
                if (!circlesMap.has(data.IP)) {
                    const i = circlesMap.size % 3;
                    let color;
                    if (i === 0) {
                        color = 'rgb(255, 0, 0)';
                    } else if (i === 1) {
                        color = 'rgb(0, 0, 255)';
                    } else {
                        color = 'rgb(255, 150, 0)';
                    }
                    var circle = L.circle([data.latitude, data.longitude], {
                        color: color,
                        fillColor: color,
                        fillOpacity: 0.4,
                        radius: 20
                    }).addTo(map);
                    circle.bindPopup(`L'utilisateur ${data.IP} a été détecté dans cette zone`);
                    circlesMap.set(data.IP, circle);
                }

                // updating the circle
                circlesMap.get(data.IP).setLatLng([data.latitude, data.longitude]);

            };
        }

        // map (object) containing all circles
        const circlesMap = new Map();

        // leaflet map
        var map = L.map('map').setView([43.30856651983747, -0.36764327846338196], 14);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 20,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        // observe
        observer("ws://localhost:8000/ws/coordonnees", circlesMap); 

    }
};

</script>
