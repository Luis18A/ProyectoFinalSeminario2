import asyncio
from scrappers.mercadoLibre import MercadoLibreScraper
from scrappers.megatone import MegatoneScraper
from scrappers.fravega import FravegaScraper
from scrappers.infopartes import InfoPartesScraper
from scrappers.fullstore import FullstoreScraper
import uuid
import threading

# Caché en memoria para las tareas ejecutadas en hilos locales
_hilos_tasks = {}
_hilos_tasks_lock = threading.Lock()

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
            print(f"[Scraper] Error en {name}: {response}")
            
    # Filtrar resultados para asegurar relevancia con la búsqueda original
    filtered_results = []
    STOP_WORDS = {'con', 'del', 'para', 'por', 'que', 'una', 'uno', 'los', 'las', 'les', 'and', 'the', 'for', 'with', 'de', 'la', 'el', 'en', 'un', 'y', 'a', 'o'}
    # Limpiar y tokenizar la consulta (ej. "Epson L3210" -> ['epson', 'l3210'])
    query_tokens = [
        token.strip(",.()[]{}-_").lower() 
        for token in q.split() 
        if token.strip(",.()[]{}-_").lower() not in STOP_WORDS
    ]
    
    if query_tokens:
        for item in combined_results:
            title_lower = item.get('titulo', '').lower()
            # Contar cuántos tokens significativos coinciden en el título
            matches = sum(1 for token in query_tokens if token in title_lower)
            # Para consultas cortas (1 o 2 tokens), exigimos al menos 1 coincidencia.
            # Para consultas más largas (3+), exigimos al menos el 50% de las palabras clave o al menos 2.
            required_matches = max(1, len(query_tokens) // 2) if len(query_tokens) > 2 else 1
            
            if matches >= required_matches:
                filtered_results.append(item)
    else:
        filtered_results = combined_results

    filtered_results.sort(key=lambda x: x.get('precio', 0))
    return filtered_results


def _run_scraping_thread(task_id, q):
    try:
        # Ejecutar scrapers usando asyncio.
        # En hilos secundarios de Flask, creamos un nuevo event loop.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(_ejecutar_scrapers(q))
        finally:
            loop.close()
            
        with _hilos_tasks_lock:
            _hilos_tasks[task_id] = {
                'status': 'completed',
                'results': results
            }
    except Exception as e:
        print(f"[Thread Task] Error ejecutando scrapers: {e}")
        with _hilos_tasks_lock:
            _hilos_tasks[task_id] = {
                'status': 'failed',
                'error': str(e)
            }

def iniciar_busqueda_hilos(q):
    """Lanza la búsqueda de repuestos en un hilo de fondo y devuelve un task_id local."""
    task_id = f"thread-{uuid.uuid4()}"
    with _hilos_tasks_lock:
        _hilos_tasks[task_id] = {
            'status': 'running'
        }
    
    t = threading.Thread(target=_run_scraping_thread, args=(task_id, q))
    t.daemon = True
    t.start()
    return task_id

def obtener_estado_busqueda_hilos(task_id):
    """Consulta el estado de una búsqueda local en hilos."""
    with _hilos_tasks_lock:
        task_info = _hilos_tasks.get(task_id)
        
    if not task_info:
        return False, "Tarea local no encontrada"
        
    if task_info['status'] == 'completed':
        return True, {'status': 'completed', 'results': task_info['results']}
    elif task_info['status'] == 'failed':
        return False, task_info.get('error', 'Error desconocido en la búsqueda')
    else:
        return True, {'status': 'running'}
