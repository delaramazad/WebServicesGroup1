async function fetchFlightData(flightNumber) {
  const url = `/api/flight?flightNumber=${encodeURIComponent(flightNumber)}`;
  const res = await fetch(url, { headers: { "Accept": "application/json" } });
  const payload = await res.json().catch(() => ({}));

  if (!res.ok) {
    const msg = payload?.error || `Request failed (${res.status})`;
    throw new Error(msg);
  }
  return payload;
}

window.fetchFlightData = fetchFlightData;
