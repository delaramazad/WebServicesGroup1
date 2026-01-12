import re
import requests
import random
import hashlib

class MusicBrainzService:
    MUSIC_BACKUPS = {
        "SE": ["ABBA", "Avicii", "Zara Larsson", "Roxette", "Swedish House Mafia"],
        "TR": ["Tarkan", "Sezen Aksu", "Müslüm Gürses", "Sertab Erener", "Hadise"],
        "US": ["Michael Jackson", "Taylor Swift", "Eminem", "Beyoncé", "Elvis Presley"],
        "GB": ["The Beatles", "Adele", "Queen", "Ed Sheeran", "Coldplay"],
        "DK": ["Lukas Graham", "MØ", "Volbeat", "Aqua"],
        "NO": ["Kygo", "A-ha", "Alan Walker", "Aurora"],
        "ES": ["Enrique Iglesias", "Rosalía", "Julio Iglesias"],
        "FR": ["Daft Punk", "David Guetta", "Édith Piaf"],
        "DE": ["Rammstein", "Scorpions", "Kraftwerk"],
        "IT": ["Måneskin", "Andrea Bocelli", "Eros Ramazzotti"]
    }

    DEFAULT_TAGS = ["pop", "rock", "dance", "electronic", "hip-hop"]

    SPOTIFY_TO_MB = {
        "hip hop": "hip-hop",
        "hip-hop": "hip-hop",
        "edm": "electronic",
        "r&b": "rnb",
        "rnb": "rnb",
    }

    def _sanitize(self, s: str) -> str:
        s = (s or "").strip().lower()
        s = s.replace('"', "")
        s = re.sub(r"[^a-z0-9 \-\_\+\&]", "", s)
        s = re.sub(r"\s+", " ", s)
        return s

    def _normalize_genres(self, genres):
        out = []
        if not isinstance(genres, list):
            return out
        for g in genres:
            if not isinstance(g, str):
                continue
            g2 = self._sanitize(g)
            if not g2:
                continue
            g2 = self.SPOTIFY_TO_MB.get(g2, g2)
            if g2 not in out:
                out.append(g2)
        return out

    def _mb_search(self, iso_code, tags, limit=120):
        url = "https://musicbrainz.org/ws/2/artist/"
        tags_query = " OR ".join([f'tag:"{t}"' for t in tags])
        query = f"country:{iso_code} AND ({tags_query})"

        params = {"query": query, "fmt": "json", "limit": limit}
        headers = {'User-Agent': 'WebServiceGroup1/1.0 (delaram.azad99@gmail.com)'}

        print(f"MB query: {query}")
        r = requests.get(url, params=params, headers=headers, timeout=8)
        if r.status_code != 200:
            print(f"MusicBrainz API error: {r.status_code}")
            return []

        data = r.json()
        artists_raw = data.get("artists", [])
        names = []
        for a in artists_raw:
            name = a.get("name")
            if name and name not in names:
                names.append(name)
        return names

    def _stable_shuffle(self, items, seed_str):
        seed = int(hashlib.sha256(seed_str.encode("utf-8")).hexdigest()[:8], 16)
        rnd = random.Random(seed)
        items = list(items)
        rnd.shuffle(items)
        return items

    def get_artists_by_country(self, iso_code, genres=None):
        iso_code = (iso_code or "").upper().strip()
        user_tags = self._normalize_genres(genres)

        # if user_tags exist run try to make sure genre actually makes a difference
        if user_tags:
            try:
                artists = self._mb_search(iso_code, user_tags, limit=120)
                if artists:
                    # genre-controlled order -> Spotify includes different artists early -> different songs
                    artists = self._stable_shuffle(artists, f"{iso_code}|{','.join(sorted(user_tags))}")
                    return artists[:40]
                else:
                    print("0 träffar på valda genrer – fallback till default.")
            except Exception as e:
                print(f"Kunde inte nå MusicBrainz API (user tags): {e}")

        # Fallback: default tags
        try:
            artists = self._mb_search(iso_code, self.DEFAULT_TAGS, limit=120)
            if artists:
                artists = self._stable_shuffle(artists, f"{iso_code}|default")
                return artists[:40]
        except Exception as e:
            print(f"Kunde inte nå MusicBrainz API (default): {e}")

        print("Går över till reservlistan (Backup)...")
        return self.MUSIC_BACKUPS.get(iso_code, ["Inga artister hittades"])
