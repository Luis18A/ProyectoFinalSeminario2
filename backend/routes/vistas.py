from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from backend.controller.auth_controller import AuthController
from backend.controller.usuario_controller import UsuarioController
from backend.controller.analytics_controller import AnalyticsController
from backend.utils.decorators import login_required, role_required

# Creamos el Blueprint para las vistas estáticas
vistas_bp = Blueprint('vistas', __name__)

# ─── Auth ────────────────────────────────────────────────────────────────────

@vistas_bp.route('/')
def login():
    if 'usuario_id' in session:
        from backend.utils.decorators import _redirect_por_rol
        return _redirect_por_rol(session.get('rol_descripcion', ''))
    return render_template('login.html')

@vistas_bp.route('/login', methods=['POST'])
def login_post():
    session.clear()
    username = request.form.get('username')
    password = request.form.get('password')

    usuario_valido, mensaje = AuthController.validar_login(username, password)

    if usuario_valido:
        session['usuario_id'] = usuario_valido.id
        session['username']   = usuario_valido.username
        try:
            session['rol_descripcion'] = usuario_valido.rol.descripcion
        except Exception:
            session['rol_descripcion'] = ''
        session['real_rol_descripcion'] = session.get('rol_descripcion', '')
        
        from backend.utils.decorators import _redirect_por_rol
        return _redirect_por_rol(session['rol_descripcion'])
    else:
        return render_template('login.html', error=mensaje)

@vistas_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('vistas.login'))

# ─── Vistas generales ────────────────────────────────────────────────────────

@vistas_bp.route('/dashboard')
@login_required
@role_required('Administrador')
def dashboard():
    datos = AnalyticsController.obtener_datos_analytics()
    return render_template('admin_analytics.html', **datos)

@vistas_bp.route('/api/global-search')
@login_required
def global_search():
    from backend.models.Cliente import Cliente
    from backend.models.Equipo import Equipo
    from backend.models.OrdenServicio import OrdenServicio
    from flask import jsonify

    q = request.args.get('q', '').strip()
    if len(q) < 2 or len(q) > 100:
        return jsonify({'clientes': [], 'equipos': [], 'ordenes': []})

    # 1. Clientes
    clientes_query = Cliente.query.filter(
        (Cliente.nombre.ilike(f"%{q}%")) |
        (Cliente.apellido.ilike(f"%{q}%")) |
        (Cliente.dni_cuil.ilike(f"%{q}%"))
    ).limit(5).all()

    clientes_res = [{
        'id': c.id,
        'nombre': f"{c.nombre} {c.apellido}",
        'dni_cuil': c.dni_cuil,
        'url': url_for('clientes.gestion_cliente', q=c.dni_cuil)
    } for c in clientes_query]

    # 2. Equipos
    equipos_query = Equipo.query.filter(
        (Equipo.marca.ilike(f"%{q}%")) |
        (Equipo.modelo.ilike(f"%{q}%")) |
        (Equipo.numero_serie.ilike(f"%{q}%"))
    ).limit(5).all()

    equipos_res = [{
        'id': e.id,
        'label': f"{e.marca} {e.modelo} (S/N: {e.numero_serie})",
        'cliente_nombre': f"{e.cliente.nombre} {e.cliente.apellido}" if e.cliente else 'Sin cliente',
        'url': url_for('equipo.gestion_equipos', cliente_id=e.cliente_id) if e.cliente_id else '#'
    } for e in equipos_query]

    # 3. Órdenes / Tickets (ID numérico o falla o accesorios)
    ordenes_res = []
    
    # Intenta buscar por ID de Ticket si es numérico o empieza con TK-
    tk_id = q.upper().replace("TK-", "").strip()
    if tk_id.isdigit():
        try:
            orden_id = int(tk_id)
            from database import db
            orden = db.session.get(OrdenServicio, orden_id)
            if orden:
                ordenes_res.append({
                    'id': orden.id,
                    'codigo': f"TK-{orden.id:04d}",
                    'falla': orden.falla_reportada or 'Sin falla',
                    'estado': orden.estado.value if orden.estado else 'Desconocido',
                    'url': url_for('ordenServicio.gestionar_ticket', orden_id=orden.id)
                })
        except Exception:
            pass

    # También buscamos por falla_reportada o accesorios o cliente/equipo
    ordenes_query = OrdenServicio.query.join(Equipo).join(Cliente).filter(
        (OrdenServicio.falla_reportada.ilike(f"%{q}%")) |
        (Cliente.nombre.ilike(f"%{q}%")) |
        (Cliente.apellido.ilike(f"%{q}%")) |
        (Equipo.marca.ilike(f"%{q}%")) |
        (Equipo.modelo.ilike(f"%{q}%"))
    ).limit(5).all()

    for o in ordenes_query:
        # Evitar duplicados si ya se agregó por ID
        if any(item['id'] == o.id for item in ordenes_res):
            continue
        ordenes_res.append({
            'id': o.id,
            'codigo': f"TK-{o.id:04d}",
            'falla': o.falla_reportada or 'Sin falla',
            'estado': o.estado.value if o.estado else 'Desconocido',
            'url': url_for('ordenServicio.gestionar_ticket', orden_id=o.id)
        })

    # Limitar el total de órdenes a 5
    ordenes_res = ordenes_res[:5]

    return jsonify({
        'clientes': clientes_res,
        'equipos': equipos_res,
        'ordenes': ordenes_res
    })
