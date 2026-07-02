import queue

class SSEService:
    def __init__(self):
        self.listeners = []

    def listen(self):
        """Crea una cola y la registra como receptor de mensajes (suscriptor)."""
        q = queue.Queue(maxsize=100)
        self.listeners.append(q)
        return q

    def announce(self, message):
        """Envía un mensaje a todos los suscriptores activos."""
        for q in list(self.listeners):
            try:
                q.put_nowait(message)
            except queue.Full:
                # Quitar cola si está saturada
                self.listeners.remove(q)
            except Exception:
                # Quitar cola ante fallos inesperados de conexión
                if q in self.listeners:
                    self.listeners.remove(q)

sse_service = SSEService()
