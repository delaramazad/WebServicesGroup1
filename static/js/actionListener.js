import { fetcher } from './fetcher.js';

// ---------- DOM Elements ----------
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

// ---------- State (Minne för appen) ----------
const state = {
  city: null,
  open: null, // "facts" | "sights" | null
  cache: { facts: null, sights: null }
};

// ---------- Helpers ----------
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

// ---------- Render Functions ----------
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

// ---------- API Loaders (Facts/Sights) ----------
async function loadFactsIfNeeded() {
  if (state.cache.facts) {
    renderFacts(state.cache.facts);
    return;
  }

  factsPanel.innerHTML = `<p class="loading">Loading facts...</p>`;

  try {
    const data = await fetcher(`/api/city/facts?city=${encodeURIComponent(state.city ?? "")}`, { method: 'GET' });
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
    const data = await fetcher(`/api/city/sights?city=${encodeURIComponent(state.city ?? "")}`, { method: 'GET' });
    state.cache.sights = data;
    renderSights(data);
  } catch (e) {
    sightsPanel.innerHTML = `<p>Could not load sights.</p>`;
  }
}

// ---------- MAIN EVENT: SEARCH FORM ----------
if (form) {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        // Rensa gamla felmeddelanden
        if (emptyP) emptyP.textContent = "";

        const flightNumber = (flightInput.value || "").trim();
        if (!flightNumber) {
            if (emptyP) emptyP.textContent = "Please enter a flight number.";
            return;
        }

        const genres = getSelectedGenres();

        // 1. VISA SPINNER & DÖLJ RESULTAT
        if (spinner) {
            spinner.style.display = 'block';
            spinner.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
        if (destinationContainer) destinationContainer.style.display = 'none';
        
        // Rensa gamla paneler (viktigt om man söker igen)
        resetPanels();

        try {
            // API ANROP
            const data = await fetcher('/get_flight_info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ flightNumber, genres })
            });

            // 2. DÖLJ SPINNER
            if (spinner) spinner.style.display = 'none';

            if (!data || data.error) {
                if (emptyP) emptyP.textContent = data?.error ?? "Could not find flight.";
                return;
            }

            // 3. UPPDATERA UI
            const city = data.destination_city || "Unknown City";
            const country = data.destination_country || "Unknown Country";
            state.city = city;

            if (titleElement) titleElement.innerText = `${city}, ${country}`;

            // Bild
            if (imageElement) {
                if (data.city_image) {
                    imageElement.src = data.city_image;
                    imageElement.style.display = "block";
                } else if (city && city !== "Unknown City") {
                    imageElement.src = `https://loremflickr.com/600/400/${encodeURIComponent(city)},cityscape`;
                    imageElement.style.display = "block";
                } else {
                    imageElement.style.display = "none";
                }
            }

            // Spotify
            if (spotifyBtn) {
                if (data.playlist_url) {
                    spotifyBtn.href = data.playlist_url;
                    spotifyBtn.style.display = "inline-flex";
                } else {
                    spotifyBtn.style.display = "none";
                }
            }

            // 4. VISA RESULTAT
            if (destinationContainer) {
                destinationContainer.style.display = "flex"; // Använder flexbox för styling
                destinationContainer.scrollIntoView({ behavior: 'smooth' });
            }

        } catch (error) {
            console.error("Frontend error:", error);
            if (spinner) spinner.style.display = 'none';
            if (emptyP) emptyP.textContent = "Something went wrong. Try again.";
        }
    });
}

// ---------- BUTTON EVENTS (Facts & Sights) ----------
if (factsBtn) {
    factsBtn.addEventListener("click", async () => {
        if (!state.city) return; // Gör inget om vi inte har en stad än
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