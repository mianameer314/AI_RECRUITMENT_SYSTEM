# Resume text extraction logic
from app.workers.celery_worker import celery_app
import PyPDF2
import json
import os

JSON_DIR = "app/uploads/json"

@celery_app.task(name="app.services.resume_service.parse_resume_task")
def parse_resume_task(file_path: str):
    extracted_text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                extracted_text += page.extract_text()
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return

    # store to JSON
    resume_id = os.path.splitext(os.path.basename(file_path))[0]
    json_data = {"text": extracted_text}
    with open(os.path.join(JSON_DIR, f"{resume_id}.json"), "w") as out:
        json.dump(json_data, out)

    print(f"✅ JSON saved for {resume_id}")
