from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from supabase import create_client
import fitz  # PyMuPDF
import tempfile

app = FastAPI()

SUPABASE_URL = "https://yamgofgwqbytmriukcnv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlhbWdvZmd3cWJ5dG1yaXVrY252Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQxODc1NDksImV4cCI6MjA1OTc2MzU0OX0._ppBZ2rBIE80NGeVR-MtG1HVBVHNzBdu0925-j52rxg"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET = "benchbila"
TABELLA = "tabella"

@app.get("/get_bilancio")
async def get_bilancio(azienda: str, categoria: str = "Bilancio"):
    try:
        query = supabase.table(TABELLA).select("*").ilike("Azienda", azienda).ilike("categoria", categoria).execute()
        if not query.data:
            return JSONResponse(status_code=404, content={"errore": "Documento non trovato"})

        file_info = query.data[0]
        original_path = file_info["path"]
        clean_path = original_path.replace("benchbila/", "")
        file_data = supabase.storage.from_(BUCKET).download(clean_path)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
            temp.write(file_data)
            temp_path = temp.name

        doc = fitz.open(temp_path)
        testo = "".join([page.get_text() for page in doc])
        doc.close()

        return {
            "azienda": azienda,
            "categoria": categoria,
            "contenuto": testo[:4000]
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"errore": str(e)})
