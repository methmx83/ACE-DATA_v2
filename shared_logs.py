LOGS = []

def log_message(message: str):
    global LOGS
    LOGS.append(message)
    LOGS.append("")  # Fügt eine Leerzeile hinzu
    print(message)  # Ausgabe im Terminal
    print("")  # Leerzeile im Terminal