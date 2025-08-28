import os
from celery import Celery
from dotenv import load_dotenv
load_dotenv()

CELERY_BROKER = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')

celery_app = Celery('tasks', broker=CELERY_BROKER, backend=CELERY_BACKEND)
celery_app.conf.task_routes = {'app.tasks.process_document': {'queue': 'default'}}

from app.parser import parse_text
from app.database import SessionLocal, init_db
from app.models import Document

init_db()

@celery_app.task(bind=True)
def process_document(self, document_id: int, file_path: str):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return {'error': 'document not found'}
        if not os.path.exists(file_path):
            doc.status = 'FAILED'
            db.commit()
            return {'error': 'file not found'}
        with open(file_path, 'rb') as f:
            raw = f.read()
        try:
            text = raw.decode('utf-8')
        except Exception:
            text = raw.decode('utf-8', errors='replace')
        parsed = parse_text(text)
        doc.parsed_vendor = parsed.get('vendor')
        doc.parsed_invoice_no = parsed.get('invoice_no')
        doc.parsed_date = parsed.get('date')
        doc.parsed_total = parsed.get('total')
        doc.raw_text = text
        doc.status = 'SUCCESS'
        db.commit()
        return parsed
    except Exception:
        if 'doc' in locals():
            doc.status = 'FAILED'
            db.commit()
        raise
    finally:
        db.close()
