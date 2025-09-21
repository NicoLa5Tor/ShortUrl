from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import string, random
from datetime import datetime
from .config import settings
from .database import DatabaseManager

# Simple FastAPI configuration (same as your working service)
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# Initialize database
db = DatabaseManager(settings.DATABASE_PATH)

class URLRequest(BaseModel):
    url: str
    alias: str = None

class URLResponse(BaseModel):
    short_url: str
    original_url: str

class URLDetails(BaseModel):
    id: int
    code: str
    original_url: str
    short_url: str
    created_at: str

class URLList(BaseModel):
    urls: List[URLDetails]
    total: int

class DeleteResponse(BaseModel):
    message: str
    deleted_count: int

class StatsResponse(BaseModel):
    total_urls: int
    last_created: Optional[str]

# Función para generar códigos aleatorios
def generar_codigo(longitud: int = None):
    if longitud is None:
        longitud = settings.CODE_LENGTH
    return ''.join(random.choices(string.ascii_letters + string.digits, k=longitud))

# Ruta para acortar una URL
@app.post('/shorten', response_model=URLResponse)
def acortar_url(request: URLRequest):
    if not request.url:
        raise HTTPException(status_code=400, detail='Se requiere una URL')

    if request.alias:
        if db.code_exists(request.alias):
            raise HTTPException(status_code=409, detail='Alias ya en uso')
        codigo = request.alias
    else:
        codigo = generar_codigo()
        while db.code_exists(codigo):
            codigo = generar_codigo()

    if not db.save_url(codigo, request.url):
        raise HTTPException(status_code=500, detail='Error al guardar URL')

    return URLResponse(
        short_url=f'http://{settings.BASE_URL}/{codigo}',
        original_url=request.url
    )

# CRUD Endpoints (deben ir ANTES del endpoint /{codigo} para evitar conflictos)

@app.get('/urls', response_model=URLList)
def get_all_urls(limit: Optional[int] = Query(None, ge=1, description="Limit number of results")):
    """Get all shortened URLs"""
    urls_data = db.get_all_urls(limit)
    urls_details = []

    for url_data in urls_data:
        urls_details.append(URLDetails(
            id=url_data['id'],
            code=url_data['code'],
            original_url=url_data['original_url'],
            short_url=f'http://{settings.BASE_URL}/{url_data["code"]}',
            created_at=url_data['created_at']
        ))

    return URLList(urls=urls_details, total=len(urls_details))

@app.get('/urls/{code}', response_model=URLDetails)
def get_url_details(code: str):
    """Get details of a specific shortened URL"""
    url_data = db.get_url_details(code)
    if not url_data:
        raise HTTPException(status_code=404, detail='URL no encontrada')

    return URLDetails(
        id=url_data['id'],
        code=url_data['code'],
        original_url=url_data['original_url'],
        short_url=f'http://{settings.BASE_URL}/{url_data["code"]}',
        created_at=url_data['created_at']
    )

@app.delete('/urls/{code}', response_model=DeleteResponse)
def delete_url(code: str):
    """Delete a specific shortened URL"""
    if not db.code_exists(code):
        raise HTTPException(status_code=404, detail='URL no encontrada')

    success = db.delete_url(code)
    if success:
        return DeleteResponse(message=f'URL con código {code} eliminada', deleted_count=1)
    else:
        raise HTTPException(status_code=500, detail='Error al eliminar URL')

@app.delete('/urls', response_model=DeleteResponse)
def delete_all_urls():
    """Delete all shortened URLs from the database"""
    deleted_count = db.delete_all_urls()
    return DeleteResponse(
        message=f'Todas las URLs han sido eliminadas',
        deleted_count=deleted_count
    )

@app.get('/stats', response_model=StatsResponse)
def get_stats():
    """Get database statistics"""
    stats = db.get_stats()
    return StatsResponse(
        total_urls=stats['total_urls'],
        last_created=stats['last_created']
    )

# Ruta para redirigir desde el alias (DEBE IR AL FINAL para no interferir con otros endpoints)
@app.get('/{codigo}')
def redirigir(codigo: str):
    original_url = db.get_url(codigo)
    if original_url:
        return RedirectResponse(url=original_url, status_code=301)
    raise HTTPException(status_code=404, detail='Alias no encontrado')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
