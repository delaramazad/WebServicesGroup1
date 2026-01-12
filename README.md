# Espotifly
EspotiFly är en mashup-webbtjänst som kombinerar flygdata i realtid med personliga musikrekommendationer. Genom att ange ett flygnummer kan användaren få information om sin destination och automatiskt generera en Spotify-spellista baserad på artister från det aktuella landet, anpassad efter flygresans längd.


# Funktioner
* Flygspårning: Hämtar detaljerad information om flygavgångar och ankomster via flygnummer.

* Geografisk data: Kopplar samman flygplatser med länder och städer med hjälp av Wikidata och lokala databaser.

* Musikrekommendationer: Identifierar populära artister från destinationslandet via MusicBrainz.

* Automatiserade Spellistor: Skapar en unik spellista på användarens Spotify-konto med topplåtar från de rekommenderade artisterna.


# APIs som används
Projektet integrerar följande tjänster:

* Aviationstack API: För flygstatus och flygplatsinformation.

* MusicBrainz API: För att hämta artister baserat på landskod.

* Spotify Web API: För sökning av låtar och hantering av spellistor.

* Wikimedia API (Wikidata): För att korsreferera IATA-koder med länder.


# Teknikstack

* Backend: Python med Flask-ramverket.

* Frontend: HTML5, CSS3 och JavaScript.

* Bibliotek: spotipy (Spotify SDK), requests (API-anrop), python-dotenv (miljövariabler), airportsdata.

# Installation och Setup
1. Klona projektet:
    https://github.com/delaramazad/WebServicesGroup1

2. Installera beroenden:
    pip install -r requirements.txt

3. Konfigurera miljövariabler: Skapa en .env-fil i rotkatalogen och lägg till dina API-nycklar:

AVIATION_API_KEY=din_nyckel
SPOTIFY_CLIENT_ID=ditt_id
SPOTIFY_CLIENT_SECRET=din_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8081

*These credentials are to be obtained separately from the group to maintain the security of the credentials. They must be manually switched out by the user to the correct credentials in order for the program to function. Please see the attached document titled "ENV INFO".*

4. Kör aplikationen:
python app.py i terminalen 
Appen startar på http://127.0.0.1:8081 by holding the Ctrl button and clicking on it with your mouse.

alternativt 

py app.py i terminalen
Appen startar på http://127.0.0.1:8081 by holding the Ctrl button and clicking on it with your mouse.

alternativt

Run the program by navigating to the "app.py" file in Visual Studio Code and pressing "Run Python file", thereafter observe the command-box at the bottom of the screen in the same program, and open the link: "http://localhost:8090/"  

Appen startar på http://127.0.0.1:8081 by holding the Ctrl button and clicking on it with your mouse.
