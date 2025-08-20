import pytest
import io

@pytest.mark.asyncio
async def test_upload_invalid_file(async_client):
    content = b"This is not a PDF"
    file = {"file": ("resume.txt", io.BytesIO(content), "text/plain")}

    res = await async_client.post("/api/v1/resumes/upload", files=file)
    assert res.status_code == 400
    assert res.json()["detail"] == "Only PDF files are allowed."

@pytest.mark.asyncio
async def test_upload_valid_pdf(async_client):
    # Sample blank PDF bytes
    pdf_bytes = (
        b"%PDF-1.4\n%FakePDF\n1 0 obj\n<<>>\nendobj\nxref\n0 1\n0000000000 65535 f\n"
        b"trailer\n<<>>\nstartxref\n9\n%%EOF"
    )
    file = {"file": ("resume.pdf", io.BytesIO(pdf_bytes), "application/pdf")}

    res = await async_client.post("/api/v1/resumes/upload", files=file)
    assert res.status_code == 200
    json_data = res.json()
    assert "file_name" in json_data
