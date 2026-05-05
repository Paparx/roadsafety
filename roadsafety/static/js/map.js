document.addEventListener("DOMContentLoaded", function () {

    console.log("MAP JS LOADED");

    const map = L.map('map', {
        scrollWheelZoom: false
    }).setView([21.2514, 81.6296], 13);

   
    let tempMarker = null;

    map.on('click', () => map.scrollWheelZoom.enable());
    map.on('mouseout', () => map.scrollWheelZoom.disable());

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);


    fetch('/api/map-data/')
    .then(res => res.json())
    .then(data => {

        const resultsDiv = document.getElementById("results");

        resultsDiv.innerHTML = "";

        data.forEach(acc => {

            if (!acc.lat || !acc.lng) return;

            let status = (acc.status || "").toLowerCase();
            let color = "red";
            let badge = "badge-high";

            if (status === "pending") {
                color = "orange";
                badge = "badge-medium";
            }

            if (status === "resolved") {
                color = "green";
                badge = "badge-low";
            }

            const marker = L.circleMarker([acc.lat, acc.lng], {
                radius: 8,
                color: color,
                fillColor: color,
                fillOpacity: 0.8
            }).addTo(map);

            marker.bindPopup(`<b>${acc.location}</b><br>Status: ${acc.status}`);

            const item = document.createElement("div");
            item.className = "result-item";

            item.innerHTML = `
                <b>${acc.location}</b><br>
                <small class="${badge}">${acc.status}</small>
            `;

            item.onclick = () => {
                map.setView([acc.lat, acc.lng], 15);
                marker.openPopup();
            };

            resultsDiv.appendChild(item);
        });

    });


   
    const locBtn = document.getElementById("locBtn");
    if (locBtn) {
        locBtn.onclick = () => {
            navigator.geolocation.getCurrentPosition(pos => {
                const lat = pos.coords.latitude;
                const lng = pos.coords.longitude;

                map.setView([lat, lng], 14);

               
                if (tempMarker) {
                    map.removeLayer(tempMarker);
                }

               
                tempMarker = L.marker([lat, lng]).addTo(map)
                    .bindPopup("You are here")
                    .openPopup();
            });
        };
    }


    
    const searchBtn = document.getElementById("searchBtn");
    const searchInput = document.getElementById("searchInput");

    if (searchBtn && searchInput) {
        searchBtn.onclick = () => {

            let place = searchInput.value.trim();

            if (!place) {
                alert("Enter a location");
                return;
            }

            fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${place}`)
            .then(res => res.json())
            .then(data => {

                if (data.length > 0) {

                    let lat = data[0].lat;
                    let lon = data[0].lon;

                    map.setView([lat, lon], 13);

                   
                    if (tempMarker) {
                        map.removeLayer(tempMarker);
                    }

                    
                    tempMarker = L.marker([lat, lon]).addTo(map)
                        .bindPopup(place)
                        .openPopup();

                } else {
                    alert("Location not found");
                }
            });
        };
    }


    setTimeout(() => {
        map.invalidateSize();
    }, 300);

});