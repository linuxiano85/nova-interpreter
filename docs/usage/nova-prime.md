# Nova Prime - GUI e Controllo Vocale

Nova Prime offre un'interfaccia desktop moderna con controllo vocale per Open Interpreter.

## Attivazione

### Wake Word: "hey nova"
- Pronuncia "hey nova" seguito dal comando
- Funziona in background anche con l'app minimizzata
- Rilevamento ottimizzato per italiano e inglese

### Hotkey Configurabile
- Default: `Ctrl+Alt+N`
- Personalizzabile nel file di configurazione
- Attiva l'ascolto immediato

### Sistema Tray
- Icona sempre visibile nel sistema tray
- Click destro per menu contestuale:
  - Attiva/Disattiva ascolto
  - Apri finestra Nova Prime
  - Esci dall'applicazione

## Interfaccia Utente

### Finestra Principale
- Design elegante con bordi arrotondati
- Trasparenza e effetti grafici moderni
- Draggabile e sempre in primo piano
- Dimensioni compatte: 520x280px

### Waveform Animata "Aurora"
- Visualizzazione multicolore del livello audio
- Animazione fluida durante l'ascolto
- Gradiente glass-effect con transizioni

### Stati Visivi
- **Pronto**: "Pronto. Di' 'hey nova' o usa la scorciatoia."
- **In ascolto**: "In ascolto..." con waveform attiva
- **Elaborazione**: "Sto pensando..." durante l'AI processing
- **Parlando**: "Sto parlando..." se TTS abilitato

## Esempi di Comandi Vocali

### Apertura Applicazioni
```
"hey nova, apri Safari"
"hey nova, open Visual Studio Code"
"hey nova, avvia le Impostazioni"
```

### Controllo Steam
```
"hey nova, apri steam Baldur's Gate 3"
"hey nova, open steam Half-Life 2"
"hey nova, avvia steam Cyberpunk 2077"
```

### Azioni Complesse
```
"hey nova, scarica il modello locale Llama 3"
"hey nova, crea una presentazione sui gatti"
"hey nova, invia un'email al mio capo"
```

## Configurazione Avanzata

File: `~/.config/nova-prime/config.json`

```json
{
  "language": "it",
  "wake_word": "hey nova",
  "global_hotkey": "ctrl+alt+n",
  "listen_on_start": true,
  "stt_backend": "faster-whisper",
  "tts_backend": null,
  "use_os_mode": true,
  "model_provider": "openai",
  "model_name": "gpt-4o",
  "show_waveform_on_listen": true
}
```

### Opzioni STT Backend
- `"faster-whisper"`: Locale, veloce, buona qualità
- `"openai"`: Whisper API, richiede API key
- `"whisper"`: Whisper locale standard

### Opzioni Model Provider
- `"openai"`: GPT-4o, GPT-3.5-turbo, ecc.
- `"anthropic"`: Claude models
- `"local"`: Modelli locali via Ollama/LM Studio

## Troubleshooting

### PySide6 non installato
```bash
pip install "open-interpreter[nova-prime]"
```

### Audio non funziona
Verifica che sounddevice e openwakeword siano installati:
```bash
pip install sounddevice openwakeword
```

### Hotkey non risponde
- Verifica che non ci siano conflitti con altre app
- Prova a cambiare la combinazione nel config
- Su Linux potrebbe servire X11 per hotkey globali

### Steam games non trovati
- Verifica che Steam sia installato
- I giochi devono essere installati localmente
- Nova Prime legge i file manifest da `steamapps/`