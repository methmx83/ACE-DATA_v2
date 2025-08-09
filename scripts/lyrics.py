#
# Modul: Lyrics-Scraper
# Zweck: Liest Metadaten aus Audiodateien, ruft Songtexte von Genius (2 URL-Varianten
#        plus Such-Fallback) ab und speichert sie als <basename>_lyrics.txt.
# Nutzung: Wird von der Gradio-UI (webui/app.py) im Verarbeitungs-Flow aufgerufen.
#
import os
import re
import time

from shared_logs import LOGS, log_message  # Importiere LOGS und log_message aus shared_logs.py

import requests
from bs4 import BeautifulSoup
from tinytag import TinyTag
from tqdm import tqdm
import unicodedata
from urllib.parse import quote

from include.metadata import clean_rap_metadata, normalize_string

# Konfiguration
# - HEADERS: Browser-ähnlicher User-Agent, erhöht die Erfolgsquote beim Scraping.
# - REQUEST_DELAY: Wartezeit (Sekunden), bevor die Fallback-Suche verwendet wird
#                  (hilft, Rate-Limits/Blockierungen zu vermeiden).
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}
REQUEST_DELAY = 1.5

# Funktion: get_audio_metadata(file_path)
# - Eingabe: Pfad zu einer Audio-Datei (mp3, flac, wav, m4a, ...)
# - Ausgabe: Dict mit 'title', 'artist', 'album' (leere Strings bei Fehlern)
# - Nebenwirkungen: Log-Ausgaben über log_message; Exceptions werden intern abgefangen
def get_audio_metadata(file_path):
    from scripts.helpers.metadata import get_audio_metadata as _meta
    return _meta(file_path)


# Funktion: process_single_file(file_path)
# - Zweck: Holt Lyrics für eine einzelne Datei und speichert sie als <basename>_lyrics.txt
# - Verhalten: Liest Artist/Title via TinyTag → get_lyrics → schreibt UTF-8-Datei mit Header
# - Rückgabe: True bei Erfolg, False bei Fehlern (Exceptions werden unterdrückt)
def process_single_file(file_path):
    """Fetch and save lyrics for one audio file"""
    try:
        meta = get_audio_metadata(file_path)
        artist = meta['artist']
        title = meta['title']

        lyrics = get_lyrics(artist, title)
        base = os.path.splitext(os.path.basename(file_path))[0]
        out_path = os.path.join(os.path.dirname(file_path), f"{base}_lyrics.txt")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(f"Artist: {artist}\nTitle: {title}\n\n")
            f.write(lyrics)
        return True
    except Exception as e:
        return False


# Funktion: scrape_genius_lyrics(artist, title)
# - Zweck: Direkter Versuch über zwei deterministische Genius-URL-Varianten
# - Ablauf: Erst Artist-Title, dann Title-Artist; parst Lyrics-Container und entfernt Referenz-Blöcke
# - Rückgabe: Lyrics-Text oder leerer String bei Nicht-Erfolg
def scrape_genius_lyrics(artist, title):
    """Try two URL patterns to fetch lyrics HTML"""
    clean_artist = clean_rap_metadata(artist)
    clean_title = clean_rap_metadata(title)
    # Two URL variants
    url1 = f"https://genius.com/{normalize_string(clean_artist)}-{normalize_string(clean_title)}-lyrics"
    url2 = f"https://genius.com/{normalize_string(clean_title)}-{normalize_string(clean_artist)}-lyrics"
    
    # Debugging-Ausgaben
    print(f"💡 Generated URL1: {url1}")
    print(f"💡 Generated URL2: {url2}")

    for url in (url1, url2):
        log_message(f"⏳ Trying URL: {url}")  # Kürzere Ausgabe
        resp = requests.get(url, headers=HEADERS)

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            containers = soup.select("div[class*='Lyrics__Container']") or soup.find_all("div", {"data-lyrics-container": "true"})
            if containers:
                text = ''
                for c in containers:
                    for block in c.select(".ReferentFragmentdesktop__ClickTarget, .Label"):
                        block.decompose()
                    text += c.get_text(separator="\n", strip=True) + "\n\n"
                return text.replace("[", "\n[").replace("]", "]\n").strip()
    return ''


# Funktion: genius_search_fallback(artist, title)
# - Zweck: Fallback-Suche über die Genius-Suchseite, wenn direkte URLs scheitern
# - Strategie: Nimmt den ersten '/lyrics'-Treffer, der im Linktext den Artist enthält
# - Rückgabe: Lyrics-Text oder leerer String
def genius_search_fallback(artist, title):
    """Fallback search via Genius search page"""
    query = quote(f"{artist} {title}")
    search_url = f"https://genius.com/search?q={query}"
    print(f"Searching Genius: {search_url}")  # Kürzere Ausgabe
    resp = requests.get(search_url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'html.parser')
    links = soup.select("a[href*='/lyrics']")
    for link in links:
        href = link['href']
        if artist.lower() in link.get_text(strip=True).lower():
            return scrape_genius_lyrics_from_url(href)
    return ''


# Funktion: scrape_genius_lyrics_from_url(url)
# - Zweck: Scraping, wenn die konkrete Lyrics-URL bereits bekannt ist (aus Suche)
# - Rückgabe: Zusammengefügter Lyrics-Text aus allen Lyrics-Containern oder leerer String
def scrape_genius_lyrics_from_url(url):
    """Scrape lyrics from a discovered Genius URL"""
    resp = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(resp.text, 'html.parser')
    containers = soup.select("div[class*='Lyrics__Container']") or soup.find_all("div", {"data-lyrics-container": "true"})
    if containers:
        return "\n\n".join(c.get_text(separator="\n", strip=True) for c in containers)
    return ''


# Funktion: get_lyrics(artist, title)
# - Zweck: Orchestriert den Lyrics-Bezug: Direktversuch → (Pause) → Such-Fallback
# - Rückgabe: Lyrics-Text oder '⚠️ Lyrics not found'
# - Logging: Kurze Statusmeldungen mit log_message
def get_lyrics(artist, title):
    log_message(f"🔄 Search lyrics for: {artist} - {title}")  # Kürzere Ausgabe
    lyrics = scrape_genius_lyrics(artist, title)
    if not lyrics:
        time.sleep(REQUEST_DELAY)
        lyrics = genius_search_fallback(artist, title)
    return lyrics or '⚠️ Lyrics not found'


# Funktion: load_lyrics(file_path)
# - Zweck: Lädt vorhandene <basename>_lyrics.txt, falls diese existiert
# - Rückgabe: Dateiinhalt (UTF-8) oder leerer String
def load_lyrics(file_path):
    """Load existing lyrics file if present"""
    base = os.path.splitext(file_path)[0]
    path = f"{base}_lyrics.txt"
    return open(path, 'r', encoding='utf-8').read() if os.path.exists(path) else ''


# Funktion: fetch_and_save_lyrics(artist, title, output_path)
# - Zweck: Holt Lyrics zu Artist/Title und schreibt sie direkt an den angegebenen Pfad
# - Unterschied zu process_single_file: schreibt nur die Lyrics (ohne Header-Zeilen)
# - Rückgabe: True bei Erfolg, sonst False
def fetch_and_save_lyrics(artist, title, output_path):
    """Orchestrate lyrics fetch + save to output_path"""
    lyrics = get_lyrics(artist, title)
    if not lyrics or lyrics.lower() == 'lyrics not found':
        return False
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(lyrics)
    return True

log_message("... Lyric Scraper loaded ✅")
