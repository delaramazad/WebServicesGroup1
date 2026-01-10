import { fetcher } from './fetcher.js';

async function fetchFlightNumber() {
    const button = document.querySelector('button');
    button.addEventListener("click", async (event) => {
        event.preventDefault();

        const flightInput = document.getElementById('flightNumber');
        const flightNumber = flightInput.value;

        console.log(flightNumber);

        const getSelectedGenres = () => {
            return Array.from(document.querySelectorAll('input[name="genre"]:checked'))
            .map(el => el.value);
        };

        const genres = getSelectedGenres();
        console.log('Selected genres:', genres); // för debugging

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

        console.log(data);

        if (!data || data.error) {
        console.warn("Flyget hittades inte eller något gick fel.");
        // Visa meddelande till användaren (t.ex. i en div på skärmen)
        console.log("Felmeddelande:", data ? data.error : "Okänt fel");
        return; // AVBRYT HÄR så att vi inte kraschar längre ner
    }

        if(data.destination_country) {
            console.log(`Destination Country: ${data.destination_country}`);
        } else {
            console.log('No destination country found.');
        }

        if(data.music_recommendations && data.music_recommendations.length > 0) {
            console.log(`Music Recommendations: ${data.music_recommendations.length}` + ' artists found.');
        } 

        // --- NYTT: VISA LÄNKEN ---
        if (data.playlist_url) {
            console.log("Spellista skapad:", data.playlist_url);
            
            // Exempel på hur du kan öppna den direkt eller visa en länk
            // window.open(data.playlist_url, '_blank'); 
            
            // Eller logga den tydligt:
            console.log("Klicka här för att lyssna: " + data.playlist_url);
        } else {
            console.log("Ingen spellista kunde skapas.");
        }
        } catch (error) {
            console.error('Error fetching flight info:', error);
        }
    })
  
}

fetchFlightNumber();