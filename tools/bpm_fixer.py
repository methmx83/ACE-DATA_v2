import os
import re
import sys

def halbiere_bpm_in_datei(dateipfad):
    with open(dateipfad, 'r', encoding='utf-8') as datei:
        inhalt = datei.read()

    # Finde alle BPM-Werte mit Regex
    bpm_muster = re.compile(r'\bbpm-(\d+)\b')
    bpm_werte = [int(match) for match in bpm_muster.findall(inhalt)]
    
    # Filtere Werte >140 und halbiere sie (gerundet)
    geaenderte_werte = {
        str(orig): str(round(orig / 2)) 
        for orig in bpm_werte 
        if orig > 140
    }

    # Ersetze Originalwerte wenn Änderungen vorhanden
    if geaenderte_werte:
        neuer_inhalt = inhalt
        for orig, neu in geaenderte_werte.items():
            neuer_inhalt = re.sub(
                r'\bbpm-' + re.escape(orig) + r'\b',
                f'bpm-{neu}',
                neuer_inhalt
            )
        return neuer_inhalt
    return None

def main():
    # Pfad zum Skriptverzeichnis
    skript_verzeichnis = os.path.dirname(os.path.abspath(__file__))
    
    # Zielverzeichnis (data im übergeordneten Ordner)
    ziel_verzeichnis = os.path.join(skript_verzeichnis, '..', 'data')
    ziel_verzeichnis = os.path.normpath(ziel_verzeichnis)
    
    if not os.path.exists(ziel_verzeichnis):
        print(f"Fehler: Datenverzeichnis nicht gefunden: {ziel_verzeichnis}")
        print("Stellen Sie sicher, dass ein Ordner 'data' neben dem 'tools'-Ordner existiert")
        sys.exit(1)
    
    print(f"Starte Verarbeitung in: {ziel_verzeichnis}")
    
    for ordnerpfad, _, dateien in os.walk(ziel_verzeichnis):
        for dateiname in dateien:
            if dateiname.endswith('_prompt.txt'):
                dateipfad = os.path.join(ordnerpfad, dateiname)
                neuer_inhalt = halbiere_bpm_in_datei(dateipfad)
                
                if neuer_inhalt is not None:
                    with open(dateipfad, 'w', encoding='utf-8') as datei:
                        datei.write(neuer_inhalt)
                    print(f'Bearbeitet: {dateipfad}')
                else:
                    print(f'Keine Änderung: {dateipfad}')

if __name__ == "__main__":
    main()