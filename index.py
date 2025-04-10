from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from supabase import create_client
import fitz  # PyMuPDF
import tempfile
import os

app = FastAPI()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
BUCKET = "benchbila"
TABELLA = "tabella"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/get_bilancio")
def get_bilancio(azienda: str = Query(...), categoria: str = Query("Bilancio")):
    query = supabase.table(TABELLA).select("*").ilike("Azienda", azienda).ilike("categoria", categoria).execute()

    if not query.data:
        return JSONResponse(status_code=404, content={"errore": "Documento non trovato"})

    file_info = query.data[0]
    file_path = file_info["path"].replace("benchbila/", "")
    file_data = supabase.storage.from_(BUCKET).download(file_path)

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