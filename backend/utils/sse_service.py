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
            except Exception:
                # Quitar cola de forma segura ante saturación o desconexión
                self.remove_listener(q)

    def remove_listener(self, q):
        """Remueve de forma segura un suscriptor de la lista."""
        if q in self.listeners:
            self.listeners.remove(q)

sse_service = SSEService()
