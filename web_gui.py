import os
import logging
from flask import Flask, render_template, request, jsonify
from datetime import datetime
from pytz import timezone
from dotenv import load_dotenv
from database import Database

load_dotenv()

app = Flask(__name__)

# Configurazione logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configurazione timezone
TIMEZONE_STR = os.getenv('TIMEZONE', 'Europe/Rome')
try:
    USER_TIMEZONE = timezone(TIMEZONE_STR)
    logger.info(f"Fuso orario configurato: {TIMEZONE_STR}")
except Exception as e:
    logger.warning(f"Fuso orario non valido: {TIMEZONE_STR}, uso il sistema. Errore: {e}")
    USER_TIMEZONE = timezone('UTC')

# Database
db = Database()


def get_now():
    """Ritorna l'ora corrente nel fuso orario dell'utente"""
    return datetime.now(USER_TIMEZONE)


def get_today():
    """Ritorna la data odierna nel fuso orario dell'utente (formato YYYY-MM-DD)"""
    return get_now().strftime('%Y-%m-%d')


@app.route('/')
def index():
    """Pagina principale"""
    today = get_today()
    current_time = get_now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template(
        'index.html',
        timezone=TIMEZONE_STR,
        today=today,
        current_time=current_time
    )


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Ottiene le attività filtrate"""
    try:
        filter_type = request.args.get('filter', 'all')
        
        if filter_type == 'today':
            tasks = db.get_tasks_by_date(get_today())
        else:
            tasks = db.get_all_tasks()
        
        return jsonify(tasks), 200
    except Exception as e:
        logger.error(f"Errore nel caricamento attività: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Aggiunge una nuova attività"""
    try:
        data = request.json
        description = data.get('description', '').strip()
        date = data.get('date', '').strip()
        time = data.get('time', '').strip()
        
        if not description or not date or not time:
            return jsonify({'error': 'Compila tutti i campi'}), 400
        
        # Valida il formato
        try:
            datetime.strptime(date, '%Y-%m-%d')
            datetime.strptime(time, '%H:%M')
        except ValueError as e:
            return jsonify({'error': f'Formato non valido: {str(e)}'}), 400
        
        task_id = db.add_task(description, date, time)
        logger.info(f"Attività aggiunta: ID {task_id}")
        
        return jsonify(
            {
                'id': task_id,
                'description': description,
                'date': date,
                'time': time,
                'completed': False,
                'message': 'Attività aggiunta'
            }
        ), 201
    except Exception as e:
        logger.error(f"Errore nell'aggiunta attività: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    """Segna un'attività come completata"""
    try:
        if db.mark_completed(task_id):
            logger.info(f"Attività {task_id} completata")
            return jsonify({'message': 'Attività completata'}), 200
        return jsonify({'error': 'Attività non trovata'}), 404
    except Exception as e:
        logger.error(f"Errore nel completamento attività: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Elimina un'attività"""
    try:
        if db.delete_task(task_id):
            logger.info(f"Attività {task_id} eliminata")
            return jsonify({'message': 'Attività eliminata'}), 200
        return jsonify({'error': 'Attività non trovata'}), 404
    except Exception as e:
        logger.error(f"Errore nell'eliminazione attività: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/time', methods=['GET'])
def get_time():
    """Ritorna l'ora corrente nel fuso orario"""
    return jsonify({
        'time': get_now().strftime('%Y-%m-%d %H:%M:%S'),
        'timezone': TIMEZONE_STR
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check per Render"""
    return 'ok', 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
