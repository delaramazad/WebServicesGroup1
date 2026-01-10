import { fetcher } from './fetcher.js';

async function fetchFlightNumber() {
    const button = document.querySelector('button');
    
    // Hämta referenser till containrarna
    const spinner = document.getElementById('loading-spinner');
    const destinationContainer = document.getElementById('destination-container');

    if (!button) return;

    button.addEventListener("click", async (event) => {
        event.preventDefault(); 

        const flightInput = document.getElementById('flightNumber');
        const flightNumber = flightInput.value;
        
        // Hämta genres
        const getSelectedGenres = () => {
            return Array.from(document.querySelectorAll('input[name="genre"]:checked'))
            .map(el => el.value);
        };
        const genres = getSelectedGenres();

        // --- STEG 1: VISA SPINNER & RENSA GAMLA RESULTAT ---
        if (spinner) spinner.style.display = 'block';       // Visa snurran
        if (destinationContainer) destinationContainer.style.display = 'none'; // Dölj gamla resultat
        // ----------------------------------------------------

        try {
            const data = await fetcher('/get_flight_info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    flightNumber: flightNumber,
                    genres: genres
                })
            });

            // --- STEG 2: DÖLJ SPINNER NÄR SVARET KOMMIT ---
            if (spinner) spinner.style.display = 'none';
            // ----------------------------------------------

            console.log("Data mottagen:", data);

            // Felhantering
            if (!data || data.error) {
                console.warn("Fel:", data ? data.error : "Okänt fel");
                alert("Kunde inte hitta flyget. Kontrollera numret och försök igen.");
                return; 
            }

            // Hämta HTML-elementen för resultat
            const titleElement = document.getElementById('location-title');
            const imageElement = document.getElementById('city-image');
            const spotifyBtn = document.getElementById('spotify-btn');

            // Uppdatera Titeln
            const city = data.destination_city || "Unknown City";
            const country = data.destination_country || "Unknown Country";
            
            if (titleElement) {
                titleElement.innerText = `${city}, ${country}`;
            }

            // Uppdatera Bilden
            if (imageElement) {
                if (data.city_image) {
                    imageElement.src = data.city_image;
                    imageElement.style.display = "block";
                } else if (data.destination_city) {
                    imageElement.src = `https://loremflickr.com/600/400/${data.destination_city},cityscape`;
                    imageElement.style.display = "block";
                } else {
                    imageElement.style.display = "none";
                }
            }

            // Uppdatera Spotify-knappen
            if (spotifyBtn) {
                if (data.playlist_url) {
                    spotifyBtn.href = data.playlist_url;
                    spotifyBtn.style.display = "inline-flex"; 
                } else {
                    spotifyBtn.style.display = "none"; 
                }
            }

            // --- STEG 3: VISA RESULTATET ---
            if (destinationContainer) {
                destinationContainer.style.display = 'flex'; // Eller 'block', beroende på din CSS
                destinationContainer.scrollIntoView({ behavior: 'smooth' });
            }

        } catch (error) {
            console.error('Något gick fel i frontend:', error);
            // Om det kraschar helt måste vi ändå ta bort spinnern
            if (spinner) spinner.style.display = 'none';
            alert("Ett oväntat fel inträffade.");
        }
    })
}

fetchFlightNumber();