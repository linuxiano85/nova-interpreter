# Nova Prime Doctor

Esegue un controllo rapido dell'ambiente (Python, dipendenze, Qt offscreen, Steam).

## Uso
```
nova-prime-doctor
```

Codice di uscita:
- 0: tutto ok
- 1: qualche requisito mancante
- 2: errore interno del doctor

Su Linux in CI, usare `QT_QPA_PLATFORM=offscreen` o `xvfb-run`.