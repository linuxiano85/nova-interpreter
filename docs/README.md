# Nova Prime (fork di Open Interpreter)

Nova Prime è un'interfaccia desktop leggera per controllare il tuo computer con la voce ("hey nova") e con il linguaggio naturale, basata su Open Interpreter.

## Caratteristiche Principali

- **Attivazione vocale "hey nova"** - ascolto continuo in background
- **Sistema tray + hotkey globale** - sempre accessibile
- **GUI elegante con waveform animata** - interfaccia moderna in Qt/QML
- **Apertura app e controllo OS** - integrazione diretta con API Computer/OS Mode
- **Integrazione Steam completa** - avvia giochi per nome o appid
- **Multilingua** - supporto italiano e inglese

## Installazione

### Installazione Rapida
```bash
pip install "open-interpreter[nova-prime] @ git+https://github.com/linuxiano85/nova-interpreter.git"
nova-prime
```

### Installazione da Sorgenti
```bash
git clone https://github.com/linuxiano85/nova-interpreter.git
cd nova-interpreter
pip install -e ".[nova-prime]"
nova-prime
```

### Solo Dipendenze Base (senza GUI)
```bash
pip install open-interpreter
# Nova Prime funziona in modalità CLI anche senza PySide6
python -m nova_prime.main
```

## API Estese

Nova Prime aggiunge nuove funzioni alla Computer API di Open Interpreter:

```python
from interpreter import interpreter

# Apri un'app di sistema
interpreter.computer.os.open_app("Safari")
interpreter.computer.os.open_app("Visual Studio Code")
interpreter.computer.os.open_app("notepad")

# Avvia un gioco Steam
interpreter.computer.os.open_steam_game("Baldur's Gate 3")
interpreter.computer.os.open_steam_game("1086940")  # per appid
```

## Configurazione

Nova Prime salva la configurazione in:
- **Linux**: `~/.config/nova-prime/config.json`
- **macOS**: `~/Library/Application Support/nova-prime/config.json`
- **Windows**: `%APPDATA%/nova-prime/config.json`

Opzioni configurabili:
- Lingua interfaccia (it/en)
- Wake word personalizzata
- Hotkey globale
- Backend STT (faster-whisper, openai, whisper)
- Modello AI (openai, anthropic, local)

## Compatibilità

Per tutte le altre funzioni (vision, mouse, tastiera, browser, mail/SMS su macOS, ecc.), vedi la documentazione originale di Open Interpreter.

Nova Prime estende Open Interpreter mantenendo piena compatibilità con l'API esistente.