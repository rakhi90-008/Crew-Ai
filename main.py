import os, uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.orm import Session
from app import models, schemas
from app.database import SessionLocal, init_db
from app.models import Document
from app.tasks import process_document, celery_app

init_db()
app = FastAPI(title='Financial Document Analyzer (Async)')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

FILE_STORAGE = os.getenv('FILE_STORAGE_PATH', './data/uploads')
os.makedirs(FILE_STORAGE, exist_ok=True)

@app.post('/upload')
async def upload(file: UploadFile = File(...), metadata: str = Form(default='')):
    file_id = str(uuid.uuid4())
    filename = file.filename or f'upload-{file_id}'
    saved_path = os.path.join(FILE_STORAGE, f'{file_id}-{filename}')
    try:
        content = await file.read()
        with open(saved_path, 'wb') as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to save uploaded file: {e}')
    db = next(get_db())
    doc = Document(filename=filename, raw_text='', status='PENDING')
    db.add(doc)
    db.commit()
    db.refresh(doc)
    task = process_document.delay(doc.id, saved_path)
    doc.task_id = task.id
    db.commit()
    return {'task_id': task.id, 'document_id': doc.id}

@app.get('/status/{task_id}')
def get_status(task_id: str):
    res = celery_app.AsyncResult(task_id)
    status = res.status
    result = None
    if res.successful():
        result = res.result
    return {'task_id': task_id, 'status': status, 'result': result}

@app.get('/documents/{doc_id}')
def get_document(doc_id: int):
    db = next(get_db())
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail='Document not found')
    parsed = {'vendor': doc.parsed_vendor, 'invoice_no': doc.parsed_invoice_no, 'date': doc.parsed_date, 'total': doc.parsed_total}
    return schemas.DocumentResponse(id=doc.id, filename=doc.filename, raw_text=doc.raw_text, parsed=schemas.ParsedResult(**parsed), task_id=doc.task_id, status=doc.status, created_at=doc.created_at)

@app.get('/documents')
def list_documents(skip: int = 0, limit: int = 50):
    db = next(get_db())
    docs = db.query(Document).offset(skip).limit(limit).all()
    out = []
    for d in docs:
        parsed = {'vendor': d.parsed_vendor, 'invoice_no': d.parsed_invoice_no, 'date': d.parsed_date, 'total': d.parsed_total}
        out.append(schemas.DocumentResponse(id=d.id, filename=d.filename, raw_text=d.raw_text, parsed=schemas.ParsedResult(**parsed), task_id=d.task_id, status=d.status, created_at=d.created_at))
    return out
