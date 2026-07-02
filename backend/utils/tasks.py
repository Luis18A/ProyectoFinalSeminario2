import os
import asyncio
from celery import Celery
from scrappers.mercadoLibre import MercadoLibreScraper
from scrappers.megatone import MegatoneScraper
from scrappers.fravega import FravegaScraper
from scrappers.infopartes import InfoPartesScraper
from scrappers.fullstore import FullstoreScraper

# Obtener URL de Redis de las variables de entorno, o usar SQLite local si no está disponible
redis_url = os.environ.get('REDIS_URL')
if redis_url:
    broker_url = redis_url
    result_backend = redis_url
else:
    # Usar SQLite local para desarrollo sin necesidad de instalar o correr Redis/Docker
    os.makedirs('instance', exist_ok=True)
    broker_url = 'sqla+sqlite:///instance/celery_broker.db'
    result_backend = 'db+sqlite:///instance/celery_results.db'

celery = Celery(
    'tasks',
    broker=broker_url,
    backend=result_backend
)

# Configuración de Celery
celery.conf.update(
    task_track_started=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Argentina/Buenos_Aires',
    enable_utc=True,
)

async def _ejecutar_scrapers(q):
    scrapers = [
        ("MercadoLibre", MercadoLibreScraper()),
        ("Megatone", MegatoneScraper()),
        ("Fravega", FravegaScraper()),
        ("InfoPartes", InfoPartesScraper()),
        ("Fullstore", FullstoreScraper())
    ]
    
    # Envolver los scrapers síncronos en hilos para que corran en paralelo
    tasks = [
        asyncio.to_thread(scraper.search, q)
        for _, scraper in scrapers
    ]
    
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    combined_results = []
    for (name, _), response in zip(scrapers, responses):
        if not isinstance(response, Exception):
            combined_results.extend(response)
        else:
            print(f"[Celery Scraper] Error en {name}: {response}")
            
    combined_results.sort(key=lambda x: x.get('precio', 0))
    return combined_results

@celery.task(name='tasks.buscar_repuestos_async')
def buscar_repuestos_async(q):
    """Tarea asíncrona de Celery para buscar ofertas de repuestos."""
    try:
        # Ejecutar el event loop asíncrono
        results = asyncio.run(_ejecutar_scrapers(q))
        return results
    except Exception as e:
        print(f"[Celery Task] Error ejecutando scrapers: {e}")
        return []
