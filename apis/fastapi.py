import asyncio
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scrappers.mercadoLibre import MercadoLibreScraper
from scrappers.megatone import MegatoneScraper
from scrappers.fravega import FravegaScraper
from scrappers.infopartes import InfoPartesScraper
from scrappers.fullstore import FullstoreScraper

# Reconfigurar salida estándar en Windows para evitar UnicodeEncodeError
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
async def search(q: str):
    scrapers = [
        ("MercadoLibre", MercadoLibreScraper()),
        ("Megatone", MegatoneScraper()),
        ("Fravega", FravegaScraper()),
        ("InfoPartes", InfoPartesScraper()),
        ("Fullstore", FullstoreScraper())
    ]
    
    # Todos los scrapers son síncronos (def), así que los envolvemos en to_thread para no bloquear.
    tasks = [
        asyncio.to_thread(scraper.search, q)
        for _, scraper in scrapers
    ]
    
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    combined_results = []
    
    # Procesamos las respuestas asociándolas con cada scraper
    for (name, _), response in zip(scrapers, responses):
        if not isinstance(response, Exception):
            combined_results.extend(response)
        else:
            print(f"Error en {name}: {response}")
    
    # Ordenamos por precio
    combined_results.sort(key=lambda x: x.get('precio', 0))
    
    return combined_results 