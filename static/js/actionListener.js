import { fetcher } from './fetcher.js';

// ---------- DOM ----------
const form = document.getElementById('search-form');
const flightInput = document.getElementById('flightNumber');
const emptyP = document.getElementById('empty-p');

const destinationContainer = document.getElementById('destination-container');
const titleElement = document.getElementById('location-title');
const imageElement = document.getElementById('city-image');
const spotifyBtn = document.getElementById('spotify-btn');

const factsBtn = document.getElementById('facts-btn');
const sightsBtn = document.getElementById('sights-btn');
const factsPanel = document.getElementById('facts-panel');
const sightsPanel = document.getElementById('sights-panel');

// ---------- State ----------
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

  factsBtn.setAttribute("aria-expanded", "false");
  sightsBtn.setAttribute("aria-expanded", "false");

  factsPanel.classList.add("is-hidden");
  sightsPanel.classList.add("is-hidden");

  factsPanel.innerHTML = "";
  sightsPanel.innerHTML = "";
}

function closeAllPanels() {
  state.open = null;
  factsBtn.setAttribute("aria-expanded", "false");
  sightsBtn.setAttribute("aria-expanded", "false");
  factsPanel.classList.add("is-hidden");
  sightsPanel.classList.add("is-hidden");
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

// ---------- Render ----------
function renderFacts(facts) {
  const extract = facts.extract ?? "No facts available.";
  const url = facts.wikipedia_url
    ? `<a class="panel-link" id="wiki-link" href="${facts.wikipedia_url}" target="_blank" rel="noopener">Read more on Wikipedia</a>`
    : "";

  factsPanel.innerHTML = `
    <div class="panel-title">Facts</div>
    <p style="margin-top:0;">${extract}</p>
    ${url}
  `;
}

function renderSights(sights) {
  const items = sights.items ?? [];

  if (items.length === 0) {
    sightsPanel.innerHTML = `
      <div class="panel-title">Sights</div>
      <p style="margin-top:0;">No sights found.</p>
    `;
    return;
  }

  sightsPanel.innerHTML = `
    <div class="panel-title">Sights</div>
    <ul class="panel-list">
      ${items.map(x => `
        <li>
          ${x.url ? `<a class="panel-link" href="${x.url}" target="_blank" rel="noopener">${x.name}</a>` : x.name}
        </li>
      `).join("")}
    </ul>
  `;
}

// ---------- Loaders ----------
async function loadFactsIfNeeded() {
  if (state.cache.facts) {
    renderFacts(state.cache.facts);
    return;
  }

  factsPanel.innerHTML = `<p class="loading">Loading facts...</p>`;

  try {
    const data = await fetcher(`/api/city/facts?city=${encodeURIComponent(state.city ?? "")}`, {
      method: 'GET'
    });

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
    const data = await fetcher(`/api/city/sights?city=${encodeURIComponent(state.city ?? "")}`, {
      method: 'GET'
    });

    state.cache.sights = data;
    renderSights(data);
  } catch (e) {
    sightsPanel.innerHTML = `<p>Could not load sights.</p>`;
  }
}

// ---------- Events ----------
form.addEventListener("submit", async (event) => {
  event.preventDefault();

  emptyP.textContent = "";

  const flightNumber = (flightInput.value || "").trim();
  if (!flightNumber) {
    emptyP.textContent = "Please enter a flight number.";
    return;
  }

  const genres = getSelectedGenres();

  try {
    const data = await fetcher('/get_flight_info', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ flightNumber, genres })
    });

    if (!data || data.error) {
      emptyP.textContent = data?.error ?? "Could not find flight.";
      return;
    }

    // Update title
    const city = data.destination_city || "Unknown City";
    const country = data.destination_country || "Unknown Country";
    state.city = city;

    titleElement.innerText = `${city}, ${country}`;

    // Update image
    if (data.city_image) {
      imageElement.src = data.city_image;
      imageElement.style.display = "block";
    } else if (city && city !== "Unknown City") {
      imageElement.src = `https://loremflickr.com/600/400/${encodeURIComponent(city)},cityscape`;
      imageElement.style.display = "block";
    } else {
      imageElement.style.display = "none";
    }

    // Update spotify button
    if (data.playlist_url) {
      spotifyBtn.href = data.playlist_url;
      spotifyBtn.style.display = "inline-flex";
    } else {
      spotifyBtn.style.display = "none";
    }

    // Show destination area
    destinationContainer.style.display = "block";
    destinationContainer.scrollIntoView({ behavior: 'smooth' });

    // Reset panels/cache for new city
    resetPanels();

  } catch (error) {
    console.error("Frontend error:", error);
    emptyP.textContent = "Something went wrong. Try again.";
  }
});

factsBtn.addEventListener("click", async () => {
  togglePanel("facts");
  if (state.open === "facts") {
    await loadFactsIfNeeded();
  }
});

sightsBtn.addEventListener("click", async () => {
  togglePanel("sights");
  if (state.open === "sights") {
    await loadSightsIfNeeded();
  }
});
