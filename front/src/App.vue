<script setup>
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
</script>

<template><div id="map"></div></template>

<script>

export default {
    name: 'Map',
    mounted() {

        function updateCircle(circle, lat, lng) {
            circle.setLatLng([lat, lng]);
        }

        function observer(url, circle_ip1, circle_ip2) {
            const ws = new WebSocket(url);
            ws.onopen = () => {
                console.log(`WebSocket connecté à l'url : ${url}`);
            };
            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.ip === "192.0.0.1") {
                    updateCircle(circle_ip1, data.lat, data.lng);
                } else if (data.ip === "192.0.0.2") {
                    updateCircle(circle_ip2, data.lat, data.lng);
                }
            };
        }

        var map = L.map('map').setView([43.30856651983747, -0.36764327846338196], 14);

        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 20,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        var circle_1 = L.circle([43.31674716329061, -0.35925523954980837], {
            color: 'red',
            fillColor: 'red',
            fillOpacity: 0.4,
            radius: 20
        }).addTo(map);
        circle_1.bindPopup("L'utilisateur IP1 a été détecté dans cette zone.");

        var circle_2 = L.circle([43.32674716329061, -0.36925523954980837], {
            color: 'blue',
            fillColor: 'blue',
            fillOpacity: 0.4,
            radius: 20
        }).addTo(map);
        circle_2.bindPopup("L'utilisateur IP2 a été détecté dans cette zone.");

        observer("ws://consumer:8000/ws/coordonnees", circle_1, circle_2);
    }
};

</script>
