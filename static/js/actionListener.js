import { fetcher } from './fetcher.js';

async function fetchFlightNumber() {
    const button = document.querySelector('button');
    button.addEventListener("click", async (event) => {
        event.preventDefault();

        const flightInput = document.getElementById('flightNumber');
        const flightNumber = flightInput.value;

        try {
            const data = await fetcher('/get_flight_info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ flightNumber: flightNumber })
            });

            // --- HÄR BÖRJAR ÄNDRINGEN ---
            
            // Kolla om vi fick giltig data (ingen error)
            if (data && !data.error) {
                console.log("Flyg hittat, skickar vidare till destination...");
                
                // Gamla kod för att se loggarna i konsolen först
                if(data.destination_country) {
                    console.log(`Destination Country: ${data.destination_country}`);
                }

                // Den sista delen som gör att sidan faktiskt byts:
                window.location.href = `/destination?flightNumber=${flightNumber}`;
                
            } else {
                // Om något gick fel (t.ex. fel flygnummer)
                console.warn("Felmeddelande:", data ? data.error : "Okänt fel");
                alert("Kunde inte hitta flyget. Kontrollera flygnumret och försök igen.");
            }
            
            // --- HÄR SLUTAR ÄNDRINGEN ---

        } catch (error) {
            console.error('Error fetching flight info:', error);
        }
    })
}

fetchFlightNumber();