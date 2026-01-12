# Espotifly
EspotiFly is a mashup web service that combines real-time flight data with personalized music recommendations. By entering a flight number users can retrieve information about their destination and automatically generate a Spotify playlist. The playlist features artists from that country and preffered music genre.


# Features
* Flight Tracking: Fetches detailed information about flight departures and arrivals via flight number.

* Geographic Data: Connects airports with countries and cities using Wikidata and local databases.

* Music Recommendations: Identifies popular artists from the destination country via MusicBrainz.

* Automated Playlists: Creates a unique playlist on the user's Spotify account featuring top tracks from the recommended artists.


# APIs Used
The project integrates the following services:

* Aviationstack API: For flight status and airport information.

* MusicBrainz API: To fetch artists based on country codes.

* Spotify Web API: For searching tracks and managing playlists.

* Wikimedia API (Wikidata): To cross-reference IATA codes with countries.


# Tech Stack

* Backend: Python with the Flask framework.

* Frontend: HTML5, CSS3 och JavaScript.

* Libraries: spotipy (Spotify SDK), requests (API calls), python-dotenv (environment variables), airportsdata.


# Installation and Setup
1. Clone the project:
    https://github.com/delaramazad/WebServicesGroup1

2. Install dependencies:
    pip install -r requirements.txt

3. Configure environment variables: 
    Create a .env file in the root directory and add your API keys:

AVIATION_API_KEY=your_key
SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8081

*These credentials are to be obtained separately from the group to maintain the security of the credentials. They must be manually switched out by the user to the correct credentials in order for the program to function. Please see the attached document titled "ENV INFO".*

4. Run the application:
    Type python app.py in the terminal. The app starts at http://127.0.0.1:8081 (hold Ctrl and click the link).

Alternatively: 
    Type py app.py in the terminal.

Alternatively: 
    Run the program by navigating to the app.py file in Visual Studio Code and pressing "Run Python file". Then, observe the command box at the bottom of the screen and open the link: http://localhost:8081/