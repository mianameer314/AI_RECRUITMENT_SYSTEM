# app/services/resume_service.py
from app.workers.celery_worker import celery_app
from app.db.mongo import db  # synchronous pymongo instance
import PyPDF2
import json
import os
from datetime import datetime

JSON_DIR = "app/uploads/json"

@celery_app.task(name="app.services.resume_service.parse_resume_task")
def parse_resume_task(file_path: str, user_id: str = None):
    """
    Parse PDF, save text to JSON, and store metadata in MongoDB.
    """
    extracted_text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted_text += page.extract_text() or ""
    except Exception as e:
        print(f"❌ Error parsing PDF: {e}")
        return

    # prepare resume id
    resume_id = os.path.splitext(os.path.basename(file_path))[0]

    # store JSON backup
    os.makedirs(JSON_DIR, exist_ok=True)
    json_data = {"text": extracted_text}
    with open(os.path.join(JSON_DIR, f"{resume_id}.json"), "w") as out:
        json.dump(json_data, out)

    # insert into MongoDB (synchronous)
    resume_doc = {
        "_id": resume_id,
        "user_id": user_id,
        "filename": os.path.basename(file_path),
        "text": extracted_text,
        "status": "uploaded",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    try:
        db["resumes"].insert_one(resume_doc)
        print(f"✅ Resume saved in Mongo with id {resume_id}")
    except Exception as e:
        print(f"⚠️ Could not save resume in Mongo: {e}")

    print(f"✅ JSON saved for {resume_id}")
