import { fetcher } from './fetcher.js';

async function fetchFlightNumber() {
    const button = document.querySelector('button');
    
    // Säkerhetskoll om knappen inte finns
    if (!button) return;

    button.addEventListener("click", async (event) => {
        event.preventDefault(); // Stoppa sidan från att laddas om!

        const flightInput = document.getElementById('flightNumber');
        const flightNumber = flightInput.value;
        console.log(`Söker efter: ${flightNumber}`);

        try {
            // 1. Hämta data från backend
            const data = await fetcher('/get_flight_info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ flightNumber: flightNumber })
            });

            console.log("Data mottagen:", data);

            // 2. Felhantering
            if (!data || data.error) {
                console.warn("Fel:", data ? data.error : "Okänt fel");
                alert("Kunde inte hitta flyget. Kontrollera numret och försök igen.");
                return; // Avbryt här om det blev fel
            }

            // 3. Hämta HTML-elementen
            const container = document.getElementById('destination-container');
            const titleElement = document.getElementById('location-title');
            const imageElement = document.getElementById('city-image');
            const spotifyBtn = document.getElementById('spotify-btn');

            // 4. Uppdatera Titeln
            const city = data.destination_city || "Unknown City";
            const country = data.destination_country || "Unknown Country";
            
            if (titleElement) {
                titleElement.innerText = `${city}, ${country}`;
            }

            // 5. Uppdatera Bilden
            if (imageElement) {
                if (data.city_image) {
                    imageElement.src = data.city_image;
                    imageElement.style.display = "block";
                } else if (data.destination_city) {
                    // Fallback-bild
                    imageElement.src = `https://loremflickr.com/600/400/${data.destination_city},cityscape`;
                    imageElement.style.display = "block";
                } else {
                    imageElement.style.display = "none";
                }
            }

            // 6. Uppdatera Spotify-knappen
            if (spotifyBtn) {
                if (data.playlist_url) {
                    spotifyBtn.href = data.playlist_url;
                    spotifyBtn.style.display = "inline-flex"; // Visa knappen
                } else {
                    spotifyBtn.style.display = "none"; // Dölj knappen
                }
            }

            // 7. VISA RESULTATET (Viktigast!)
            if (container) {
                container.style.display = "block";
                container.scrollIntoView({ behavior: 'smooth' });
            }

        } catch (error) {
            console.error('Något gick fel i frontend:', error);
        }
    })
}

fetchFlightNumber();