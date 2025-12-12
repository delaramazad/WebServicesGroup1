import { fetcher } from './fetcher.js';

async function fetchFlightNumber() {
    const button = document.querySelector('button');
    button.addEventListener("click", async (event) => {
        event.preventDefault();

        const flightInput = document.getElementById('flightNumber');
        const flightNumber = flightInput.value;

        console.log(flightNumber);

        const data = await fetcher('/get_flight_info', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ flightNumber: flightNumber })
        });

        console.log(data);

    })
  
}

fetchFlightNumber();