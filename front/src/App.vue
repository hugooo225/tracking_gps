<script setup>
import 'leaflet/dist/leaflet.css';
</script>

<template>
  <div id="map"></div>
</template>

<script>
import L from 'leaflet';

export default {
    name: 'MapComponent',
    mounted() {

        var map = L.map('map').setView([43.30856651983747, -0.36764327846338196], 14);
      
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 20,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);
        var circle1 = L.circle([43.31674716329061, -0.35925523954980837], {
            color: 'red',
            fillColor: 'red',
            fillOpacity: 0.5,
            radius: 20
        }).addTo(map);
        circle1.bindPopup("L'utilisateur IP1 a été détecté dans cette zone.");

        var circle2 = L.circle([43.29157162677075, -0.36958337105246714], {
            color: 'blue',
            fillColor: 'blue',
            fillOpacity: 0.5,
            radius: 20
        }).addTo(map);
        circle2.bindPopup("L'utilisateur IP2 a été détecté dans cette zone.");
    }
};

</script>
