(function () {
  const form = document.querySelector("form.search");
  const input = document.getElementById("flightNumber");
  const results = document.querySelector(".results");
  const hint = results?.querySelector(".hint");
  const pre = results?.querySelector("pre.results-box");

  if (!form || !input || !results) return;

  // Om du vill köra "utan page reload": använd fetch mot /api/flight
  form.addEventListener("submit", async (e) => {
    // Låt server-side POST vara fallback om fetchFlightData saknas
    if (typeof window.fetchFlightData !== "function") return;

    e.preventDefault();
    const flightNumber = (input.value || "").trim();
    if (!flightNumber) return;

    try {
      const data = await window.fetchFlightData(flightNumber);

      // Bygg/uppdatera resultbox
      if (!pre) {
        const title = results.querySelector(".results-title") || document.createElement("h2");
        title.className = "results-title";
        title.textContent = "Flight data";
        results.prepend(title);

        const box = document.createElement("pre");
        box.className = "results-box";
        results.appendChild(box);
        box.textContent = JSON.stringify(data.data, null, 2);
      } else {
        pre.textContent = JSON.stringify(data.data, null, 2);
      }

      if (hint) hint.remove();
    } catch (err) {
      console.error(err);
      alert(err?.message || "Kunde inte hämta flight-data.");
    }
  });
})();
