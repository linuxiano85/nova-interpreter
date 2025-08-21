# Estensioni Computer API (Nova Prime)

Oltre alle funzioni documentate in Open Interpreter, Nova Prime aggiunge nuove capacità di controllo del sistema operativo.

## OS - Open App

Apre un'applicazione di sistema per nome, con supporto cross-platform.

### Sintassi
```python
interpreter.computer.os.open_app(app_name: str) -> str
```

### Esempi
```python
# macOS
interpreter.computer.os.open_app("Safari")
interpreter.computer.os.open_app("Visual Studio Code")
interpreter.computer.os.open_app("System Preferences")

# Windows
interpreter.computer.os.open_app("notepad")
interpreter.computer.os.open_app("Calculator")
interpreter.computer.os.open_app("Microsoft Word")

# Linux
interpreter.computer.os.open_app("firefox")
interpreter.computer.os.open_app("gedit")
interpreter.computer.os.open_app("gnome-terminal")
```

### Implementazione per OS

#### macOS
- Usa `open -a "App Name"`
- Supporta nomi completi delle applicazioni
- Cerca automaticamente in `/Applications/`

#### Windows
- Usa PowerShell `Start-Process` o `cmd start`
- Supporta nomi eseguibili e percorsi completi
- Fallback multipli per compatibilità

#### Linux
- Prova `gtk-launch` con file .desktop
- Fallback a `xdg-open` per percorsi
- Cerca eseguibili in PATH

## OS - Open Steam Game

Avvia un gioco di Steam per nome (se installato) o per AppID.

### Sintassi
```python
interpreter.computer.os.open_steam_game(name_or_appid: str) -> str
```

### Esempi per Nome
```python
# Ricerca per nome (case-insensitive, supporta matching parziale)
interpreter.computer.os.open_steam_game("Baldur's Gate 3")
interpreter.computer.os.open_steam_game("Half-Life 2")
interpreter.computer.os.open_steam_game("Cyberpunk 2077")

# Matching parziale
interpreter.computer.os.open_steam_game("baldur")  # trova "Baldur's Gate 3"
interpreter.computer.os.open_steam_game("half life")  # trova "Half-Life 2"
```

### Esempi per AppID
```python
# AppID diretto (sempre funziona se Steam è installato)
interpreter.computer.os.open_steam_game("1086940")  # Baldur's Gate 3
interpreter.computer.os.open_steam_game("220")     # Half-Life 2
interpreter.computer.os.open_steam_game("1091500") # Cyberpunk 2077
```

### Come Funziona

#### Risoluzione Nome → AppID
1. Legge i file manifest da `steamapps/appmanifest_*.acf`
2. Estrae nome e AppID di ogni gioco installato
3. Crea mapping nome→AppID (case-insensitive)
4. Supporta matching parziale se nome esatto non trovato

#### Percorsi Steam per OS
- **Linux**: `~/.local/share/Steam/steamapps/`
- **macOS**: `~/Library/Application Support/Steam/steamapps/`
- **Windows**: `%PROGRAMFILES(x86)%\Steam\steamapps\` o `%PROGRAMFILES%\Steam\steamapps\`

#### Lancio tramite Steam Protocol
- Usa protocollo `steam://rungameid/{appid}`
- Cross-platform: funziona su tutti gli OS con Steam installato
- Non richiede che Steam sia già aperto

### Valori di Ritorno

#### Successo
```python
"Launched Steam game 'Baldur's Gate 3'"
"Launched Steam game (AppID: 1086940)"
```

#### Errori
```python
"Steam game 'Nome Gioco' not found"
"Could not launch Steam game with AppID 123456"
"Error launching Steam game 'Nome': [dettagli errore]"
```

## Integrazione con Nova Prime

### Enhanced Steam Services
Quando il pacchetto `nova_prime` è installato, l'API Computer usa i servizi avanzati:

```python
from nova_prime.services.steam import installed_games, launch_game_by_name

# Lista tutti i giochi installati
games = installed_games()
print(f"Trovati {len(games)} giochi Steam")

# Lancio diretto
success = launch_game_by_name("Baldur's Gate 3")
```

### Fallback Graceful
Se `nova_prime` non è disponibile:
- `open_app()` funziona normalmente
- `open_steam_game()` supporta solo AppID numerici
- Messaggio informativo per installare `[nova-prime]` extras

## Esempi di Uso in Conversazioni

### Comando Diretto
```python
result = interpreter.computer.os.open_app("Safari")
print(result)  # "Launched Safari"
```

### In Chat Interattiva
```python
interpreter.chat("Apri Safari e vai su YouTube")
```

L'AI userà automaticamente le nuove API per aprire Safari, poi controllerà il browser per navigare.

### Steam Gaming Session
```python
interpreter.chat("Avvia Baldur's Gate 3 e dimmi i controlli")
```

L'AI aprirà il gioco e potrà fornire informazioni sui controlli.

## Note Tecniche

### Sicurezza
- Le API verificano che le app esistano prima del lancio
- Nessuna esecuzione di comandi arbitrari
- Logging degli errori per debugging

### Performance
- Cache del mapping Steam per sessioni multiple
- Lazy loading dei servizi nova_prime
- Timeout appropriati per operazioni di rete

### Compatibilità
- Funziona con tutte le versioni di Steam supportate
- Compatibile con installazioni Steam multiple
- Supporta Steam Deck (Linux)