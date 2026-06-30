from database import db
from datetime import datetime

class TareaBusqueda(db.Model):
    __tablename__ = 'tarea_busqueda'

    id              = db.Column(db.String(50), primary_key=True)
    status          = db.Column(db.String(20), nullable=False, default='running')
    resultados_json = db.Column(db.JSON, nullable=True)
    error           = db.Column(db.String(500), nullable=True)
    fecha_creacion  = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, id, status='running', resultados_json=None, error=None):
        self.id              = id
        self.status          = status
        self.resultados_json = resultados_json or []
        self.error           = error

    def __repr__(self):
        return f"<TareaBusqueda id='{self.id}' status='{self.status}'>"
