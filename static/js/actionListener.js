import { fetcher } from './fetcher.js';

// DOM Elements 
const form = document.getElementById('search-form');
const flightInput = document.getElementById('flightNumber');
const emptyP = document.getElementById('empty-p');

// Spinner & Containers
const spinner = document.getElementById('loading-spinner');
const destinationContainer = document.getElementById('destination-container');

// Result Elements
const titleElement = document.getElementById('location-title');
const imageElement = document.getElementById('city-image');
const spotifyBtn = document.getElementById('spotify-btn');

// Facts & Sights Elements
const factsBtn = document.getElementById('facts-btn');
const sightsBtn = document.getElementById('sights-btn');
const factsPanel = document.getElementById('facts-panel');
const sightsPanel = document.getElementById('sights-panel');

// State (Memory for app)
const state = {
  city: null,
  open: null, // "facts" | "sights" | null
  cache: { facts: null, sights: null }
};

// Helpers
function getSelectedGenres() {
  return Array.from(document.querySelectorAll('input[name="genre"]:checked'))
    .map(el => el.value);
}

function resetPanels() {
  state.open = null;
  state.cache.facts = null;
  state.cache.sights = null;

  if (factsBtn) factsBtn.setAttribute("aria-expanded", "false");
  if (sightsBtn) sightsBtn.setAttribute("aria-expanded", "false");

  if (factsPanel) {
      factsPanel.classList.add("is-hidden");
      factsPanel.innerHTML = "";
  }
  if (sightsPanel) {
      sightsPanel.classList.add("is-hidden");
      sightsPanel.innerHTML = "";
  }
}

function closeAllPanels() {
  state.open = null;
  if (factsBtn) factsBtn.setAttribute("aria-expanded", "false");
  if (sightsBtn) sightsBtn.setAttribute("aria-expanded", "false");
  if (factsPanel) factsPanel.classList.add("is-hidden");
  if (sightsPanel) sightsPanel.classList.add("is-hidden");
}

function togglePanel(which) {
  if (state.open === which) {
    closeAllPanels();
    return;
  }

  closeAllPanels();

  if (which === "facts") {
    state.open = "facts";
    factsBtn.setAttribute("aria-expanded", "true");
    factsPanel.classList.remove("is-hidden");
  } else {
    state.open = "sights";
    sightsBtn.setAttribute("aria-expanded", "true");
    sightsPanel.classList.remove("is-hidden");
  }
}

// Render Functions
function renderFacts(facts) {
  const extract = facts.extract ?? "No facts available.";
  const url = facts.wikipedia_url
    ? `<a class="panel-link" id="wiki-link" href="${facts.wikipedia_url}" target="_blank" rel="noopener">Read more on Wikipedia</a>`
    : "";

  factsPanel.innerHTML = `
    <h3>Facts about ${state.city}</h3>
    <p>${extract}</p>
    ${url}
  `;
}

function renderSights(sights) {
  const items = sights.items ?? [];

  if (items.length === 0) {
    sightsPanel.innerHTML = `
      <h3>Sights</h3>
      <p>No specific sights found.</p>
    `;
    return;
  }

  sightsPanel.innerHTML = `
    <h3>Top Sights in ${state.city}</h3>
    <ul class="panel-list">
      ${items.map(x => `
        <li>
          ${x.url ? `<a class="panel-link" href="${x.url}" target="_blank" rel="noopener">${x.name}</a>` : x.name}
        </li>
      `).join("")}
    </ul>
  `;
}

// API Loaders (Facts/Sights)
async function loadFactsIfNeeded() {
  if (state.cache.facts) {
    renderFacts(state.cache.facts);
    return;
  }

  factsPanel.innerHTML = `<p class="loading">Loading facts...</p>`;

  try {
    const data = await fetcher(`/api/cities/${encodeURIComponent(state.city)}/facts`, { method: 'GET' });
    state.cache.facts = data;
    renderFacts(data);
  } catch (e) {
    factsPanel.innerHTML = `<p>Could not load facts.</p>`;
  }
}

async function loadSightsIfNeeded() {
  if (state.cache.sights) {
    renderSights(state.cache.sights);
    return;
  }

  sightsPanel.innerHTML = `<p class="loading">Loading sights...</p>`;

  try {
    const data = await fetcher(`/api/cities/${encodeURIComponent(state.city)}/sights`, { method: 'GET' });
    state.cache.sights = data;
    renderSights(data);
  } catch (e) {
    sightsPanel.innerHTML = `<p>Could not load sights.</p>`;
  }
}

// MAIN EVENT: SEARCH FORM
if (form) {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        // Clear previous error messages
        if (emptyP) emptyP.textContent = "";

        const flightNumber = (flightInput.value || "").trim();
        if (!flightNumber) {
            if (emptyP) emptyP.textContent = "Please enter a flight number.";
            return;
        }

        const genres = getSelectedGenres();

        // Show spinner and hide result
        if (spinner) {
            spinner.style.display = 'block';
            spinner.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        if (destinationContainer) destinationContainer.style.display = 'none';
        
        // Clear previous panels gamla paneler
        resetPanels();

        try {
            // Get Flight info (RESTful GET)
            const flightData = await fetcher(`/api/flights/${encodeURIComponent(flightNumber)}`, {
                method: 'GET'
            });

            if (!flightData || flightData.error) {
                if (spinner) spinner.style.display = 'none';
                window.alert("Flight not found. Please check the flight number.");
                return;
            }

            // Update UI with flight info directly (we dont await playlist for this)
            const city = flightData.destination_city || "Unknown City";
            const country = flightData.destination_country || "Unknown Country";
            state.city = city;

            if (titleElement) titleElement.innerText = `${city}, ${country}`;

            if (imageElement) {
                if (flightData.city_image) {
                  if (flightData.city_image.includes("https://media1.tenor.com/images/f0e8e9237c710dda55a2a86a7c73b40b/tenor.gif")) {
                      window.alert("Image not found. Enjoy Bibble instead!");
                    }
                  
                    imageElement.src = flightData.city_image;
                    imageElement.style.display = "block";
                } else {
                    imageElement.src = `https://loremflickr.com/600/400/${encodeURIComponent(city)},cityscape`;
                    imageElement.style.display = "block";

                }
            }

            // show containern so that user can see city while playlist it being created
            if (destinationContainer) {
                destinationContainer.style.display = "flex";
                destinationContainer.scrollIntoView({ behavior: 'smooth' });
            }

            // Create playlist (RESTful POST)
            // We send genres and iso_code in body according to REST- best practises.
            const playlistData = await fetcher(`/api/flights/${encodeURIComponent(flightNumber)}/playlists`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    genres: genres,
                    iso_code: flightData.iso_code 
                })
            });

            // hide spinner when everything is done
            if (spinner) spinner.style.display = 'none';

            // update spotify button if we got a link 
            if (spotifyBtn && playlistData && playlistData.playlist_url) {
                spotifyBtn.href = playlistData.playlist_url;
                spotifyBtn.style.display = "inline-flex";
            } else if (spotifyBtn) {
                spotifyBtn.style.display = "none";
            }

        } catch (error) {
            console.error("Frontend error:", error);
            if (spinner) spinner.style.display = 'none';
            if (emptyP) emptyP.textContent = "Something went wrong. Try again.";
        }
    });
}


// BUTTON EVENTS (Facts & Sights)
if (factsBtn) {
    factsBtn.addEventListener("click", async () => {
        if (!state.city) return; // Do nothing if we dont have a city yet
        togglePanel("facts");
        if (state.open === "facts") {
            await loadFactsIfNeeded();
        }
    });
}

if (sightsBtn) {
    sightsBtn.addEventListener("click", async () => {
        if (!state.city) return;
        togglePanel("sights");
        if (state.open === "sights") {
            await loadSightsIfNeeded();
        }
    });
}