# 🖥️ Bot Telegram Web GUI

Web interface per gestire le attività del Bot Telegram Daily Tasks.

Accedi da browser e gestisci i tuoi impegni con supporto completo al fuso orario **UTC+2** (Europe/Rome).

## ✨ Funzionalità

- 📋 **Interfaccia web responsive** - Funziona su desktop, tablet e smartphone
- ➕ **Aggiungi attività** - Con descrizione, data e ora
- 📅 **Filtri** - Visualizza tutte le attività o solo quelle di oggi
- ✅ **Segna come completate** - Traccia il progresso
- 🗑️ **Elimina attività** - Rimuovi impegni
- 🕐 **Fuso orario UTC+2** - Tutte le date e ore nel tuo fuso
- 🔄 **Aggiornamento in tempo reale** - L'ora si aggiorna automaticamente
- 🗄️ **Connessione a Supabase** - Database PostgreSQL condiviso con il bot

## 🚀 Deploy su Render

### 1. Preparazione

1. Vai su [Render.com](https://render.com)
2. Collega il tuo account GitHub
3. Crea un nuovo **Web Service**
4. Seleziona questo repository

### 2. Configurazione Render

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
python web_gui.py
```

### 3. Variabili d'Ambiente

Aggiungi in Render → Settings → Environment:

```
DATABASE_URL=postgresql://user:password@host:5432/dbname
TIMEZONE=Europe/Rome
PORT=5000
FLASK_ENV=production
```

**Per il DATABASE_URL:**
- Vai su [Supabase.com](https://supabase.com)
- Apri il tuo progetto
- Settings → Database → Connection string (PostgreSQL)
- Copia la stringa completa

### 4. Avvia il Deploy

Clicca **Deploy** e Render farà il resto.

La tua app sarà disponibile all'URL: `https://your-app-name.onrender.com`

## 💻 Esecuzione Locale

### Prerequisiti

- Python 3.7+
- PostgreSQL (o Supabase)
- pip

### Installazione

1. Clona il repository:
   ```bash
   git clone https://github.com/lucabelometti0709-alt/bot-gui.git
   cd bot-gui
   ```

2. Crea l'ambiente virtuale:
   ```bash
   python -m venv venv
   source venv/bin/activate  # su Windows: venv\Scripts\activate
   ```

3. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura il `.env`:
   ```bash
   cp .env.example .env
   ```
   
   Modifica `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   TIMEZONE=Europe/Rome
   PORT=5000
   FLASK_ENV=development
   ```

5. Avvia il server:
   ```bash
   python web_gui.py
   ```

   La GUI sarà disponibile a: `http://localhost:5000`

## 📱 Utilizzo

### Aggiungere un'Attività

1. Inserisci la **descrizione** dell'attività
2. Seleziona la **data** (precompilata con oggi)
3. Inserisci l'**ora** (formato HH:MM)
4. Clicca **Aggiungi**

### Visualizzare Attività

- **Tutte le attività** - Mostra tutti gli impegni
- **Attività di oggi** - Mostra solo gli impegni di oggi
- **Aggiorna ora** - Sincronizza l'ora corrente

### Gestire Attività

- **✅ Completa** - Segna come completata (strikethrough)
- **🗑️ Elimina** - Rimuovi l'attività

## 🔗 Integrazione con Bot Telegram

Questa GUI condivide lo **stesso database** del bot Telegram principale.

Puoi:
- Aggiungere attività dalla GUI e gestirle dal bot
- Aggiungere attività dal bot e visualizzarle qui
- Ricevere promemoria via Telegram alle ore indicate nel fuso UTC+2

## 📊 API REST

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/tasks?filter=all\|today` | Ottiene attività |
| POST | `/api/tasks` | Aggiunge attività |
| PUT | `/api/tasks/<id>/complete` | Completa attività |
| DELETE | `/api/tasks/<id>` | Elimina attività |
| GET | `/api/time` | Ora corrente nel fuso |
| GET | `/health` | Health check |

### Esempi

**Aggiungere un'attività:**
```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Riunione",
    "date": "2026-07-01",
    "time": "14:30"
  }'
```

**Completare un'attività:**
```bash
curl -X PUT http://localhost:5000/api/tasks/1/complete
```

## 🐛 Troubleshooting

### Errore: DATABASE_URL non configurato

- Assicurati di aver impostato `DATABASE_URL` nel file `.env` o in Render
- Verifica che la connection string sia corretta

### Errore: Fuso orario non valido

- Usa un fuso orario valido dal [database IANA](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
- Esempi: `Europe/Rome`, `Europe/London`, `America/New_York`

### La GUI non si carica

- Controlla che il server sia in esecuzione: `python web_gui.py`
- Verifica l'URL: `http://localhost:5000`
- Controlla i log per errori

### Le attività non si sincronizzano

- Assicurati che DATABASE_URL punti allo stesso database del bot
- Verifica la connessione a Supabase

## 📄 Licenza

Open source per uso personale.

## 🤝 Supporto

Per problemi o suggerimenti, apri un [Issue](https://github.com/lucabelometti0709-alt/bot-gui/issues).
