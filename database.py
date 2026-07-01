import os
import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse, unquote
import socket

try:
    import psycopg
except ImportError:
    psycopg = None

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError('DATABASE_URL non configurato')
        self.init_db()

    def _postgres_conninfo(self) -> str:
        """Estrae le informazioni di connessione da DATABASE_URL"""
        parsed = urlparse(self.database_url)
        host = parsed.hostname or ""
        try:
            port = parsed.port or 5432
        except ValueError as exc:
            raise ValueError(
                "DATABASE_URL non valida: sembra mancare l'host o la porta. "
                "Incolla la connection string completa di Supabase, ad esempio "
                "'postgresql://user:password@host:5432/dbname'."
            ) from exc
        dbname = parsed.path.lstrip("/")
        user = unquote(parsed.username or "")
        password = unquote(parsed.password or "")

        if not host or not dbname or not user:
            raise ValueError(
                "DATABASE_URL non valida: servono user, host e nome database. "
                "Controlla di aver copiato la connection string completa, non solo la password."
            )

        # Risolvi IPv4 per evitare problemi con IPv6 su Render
        hostaddr = None
        try:
            infos = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)
            if infos:
                hostaddr = infos[0][4][0]
        except socket.gaierror:
            hostaddr = None

        parts = [
            f"host={host}",
            f"port={port}",
            f"dbname={dbname}",
            f"user={user}",
            f"password={password}",
            "sslmode=require",
        ]
        if hostaddr:
            parts.append(f"hostaddr={hostaddr}")
        return " ".join(parts)

    def _connect(self):
        """Connessione al database"""
        if not psycopg:
            raise RuntimeError(
                "psycopg non installato. Esegui: pip install -r requirements.txt"
            )
        return psycopg.connect(self._postgres_conninfo())

    def init_db(self):
        """Inizializza il database creando le tabelle necessarie"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS tasks (
                        id SERIAL PRIMARY KEY,
                        description TEXT NOT NULL,
                        date TEXT NOT NULL,
                        time TEXT NOT NULL,
                        completed BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                    """
                )
                conn.commit()
                logger.info("Database inizializzato")
        except Exception as e:
            logger.error(f"Errore nell'inizializzazione del database: {e}")
            raise

    def add_task(self, description: str, date: str, time: str) -> int:
        """Aggiunge una nuova attività"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO tasks (description, date, time, completed)
                    VALUES (%s, %s, %s, FALSE)
                    RETURNING id
                    """,
                    (description, date, time),
                )
                task_id = cursor.fetchone()[0]
                conn.commit()
                return int(task_id)
        except Exception as e:
            logger.error(f"Errore nell'aggiunta attività: {e}")
            raise

    def _rows_to_tasks(self, rows) -> List[Dict]:
        """Converte le righe dal database in dizionari di attività"""
        return [
            {
                "id": row[0],
                "description": row[1],
                "date": row[2],
                "time": row[3],
                "completed": bool(row[4]),
            }
            for row in rows
        ]

    def get_tasks_by_date(self, date: str) -> List[Dict]:
        """Ottiene tutte le attività per una specifica data"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, description, date, time, completed
                    FROM tasks
                    WHERE date = %s
                    ORDER BY time ASC
                    """,
                    (date,),
                )
                return self._rows_to_tasks(cursor.fetchall())
        except Exception as e:
            logger.error(f"Errore nel caricamento attività per data: {e}")
            raise

    def get_all_tasks(self) -> List[Dict]:
        """Ottiene tutte le attività"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, description, date, time, completed
                    FROM tasks
                    ORDER BY date DESC, time ASC
                    """
                )
                return self._rows_to_tasks(cursor.fetchall())
        except Exception as e:
            logger.error(f"Errore nel caricamento tutte le attività: {e}")
            raise

    def mark_completed(self, task_id: int) -> bool:
        """Marca un'attività come completata"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE tasks SET completed = TRUE WHERE id = %s",
                    (task_id,),
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Errore nel completamento attività: {e}")
            raise

    def delete_task(self, task_id: int) -> bool:
        """Elimina un'attività"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Errore nell'eliminazione attività: {e}")
            raise

    def get_task_by_id(self, task_id: int) -> Optional[Dict]:
        """Ottiene un'attività specifica per ID"""
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, description, date, time, completed
                    FROM tasks
                    WHERE id = %s
                    """,
                    (task_id,),
                )
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "description": row[1],
                        "date": row[2],
                        "time": row[3],
                        "completed": bool(row[4]),
                    }
                return None
        except Exception as e:
            logger.error(f"Errore nel caricamento attività per ID: {e}")
            raise
