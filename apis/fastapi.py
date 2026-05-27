import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scrappers.mercadoLibre import MercadoLibreScraper
from scrappers.megatone import MegatoneScraper
from scrappers.fravega import FravegaScraper

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
    ml_scraper = MercadoLibreScraper()
    mega_scraper = MegatoneScraper()
    fravega_scraper = FravegaScraper()
    
    # Todos los scrapers son síncronos (def), así que los envolvemos en to_thread para no bloquear.
    tasks = [
        asyncio.to_thread(ml_scraper.search, q),
        asyncio.to_thread(mega_scraper.search, q),
        asyncio.to_thread(fravega_scraper.search, q)
    ]
    
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    combined_results = []
    
    # Procesamos MercadoLibre
    if not isinstance(responses[0], Exception):
        combined_results.extend(responses[0])
    else:
        print(f"Error en MercadoLibre: {responses[0]}")
    
    # Procesamos Megatone
    if not isinstance(responses[1], Exception):
        combined_results.extend(responses[1])
    else:
        print(f"Error en Megatone: {responses[1]}")

    # Procesamos Fravega
    if not isinstance(responses[2], Exception):
        combined_results.extend(responses[2])
    else:
        print(f"Error en Fravega: {responses[2]}")
    
    # Ordenamos por precio
    combined_results.sort(key=lambda x: x.get('precio', 0))
    
    return combined_results 