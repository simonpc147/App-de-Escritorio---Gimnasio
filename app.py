# app.py (archivo principal en la raíz del proyecto)
from flask import Flask, render_template, request, redirect, url_for, flash, session
from app.controllers.controlador import Controlador
import os  
from dotenv import load_dotenv 

load_dotenv()

app = Flask(__name__, 
            template_folder='app/views/templates',
            static_folder='app/views/static')

app.secret_key = os.getenv('SECRET_KEY', 'clave_secreta_por_defecto')

controlador = Controlador()


@app.route('/')
def index():
    """Página principal de la aplicación."""
    return render_template('index.html')

# === RUTAS PARA USUARIOS ===

@app.route('/usuarios')
def usuarios():
    """Lista todos los usuarios registrados."""
    try:
        lista_usuarios = controlador.obtener_usuarios()
        return render_template('usuarios/lista.html', usuarios=lista_usuarios)
    except Exception as e:
        flash(f'Error al obtener usuarios: {e}', 'danger')
        return redirect(url_for('index'))

@app.route('/usuarios/nuevo', methods=['GET', 'POST'])
def nuevo_usuario():
    """Formulario para registrar un nuevo usuario."""
    if request.method == 'POST':
        # Obtener datos del formulario
        id_usuario = request.form.get('id_usuario')
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        
        # Validar datos (implementar según necesidades)
        
        # Procesar el registro
        try:
            from datetime import datetime
            fecha_registro = datetime.now().strftime("%Y-%m-%d")
            resultado = controlador.registrar_usuario(id_usuario, nombre, email, telefono, fecha_registro)
            
            if isinstance(resultado, int) and resultado > 0:
                flash('Usuario registrado exitosamente', 'success')
                return redirect(url_for('usuarios'))
            else:
                flash(f'Error al registrar usuario: {resultado}', 'danger')
        except Exception as e:
            flash(f'Error en el servidor: {e}', 'danger')
    
    # Si es GET o hay error en POST, mostrar formulario
    return render_template('usuarios/nuevo.html')

@app.route('/usuarios/<id>')
def ver_usuario(id):
    """Ver detalles de un usuario específico."""
    try:
        usuario = controlador.buscar_usuario_por_id(id)
        if usuario:
            return render_template('usuarios/detalle.html', usuario=usuario)
        else:
            flash('Usuario no encontrado', 'warning')
            return redirect(url_for('usuarios'))
    except Exception as e:
        flash(f'Error al buscar usuario: {e}', 'danger')
        return redirect(url_for('usuarios'))

# === RUTAS PARA EJERCICIOS ===

@app.route('/ejercicios')
def ejercicios():
    """Lista todos los ejercicios disponibles."""
    try:
        lista_ejercicios = controlador.obtener_ejercicios()
        return render_template('ejercicios/lista.html', ejercicios=lista_ejercicios)
    except Exception as e:
        flash(f'Error al obtener ejercicios: {e}', 'danger')
        return redirect(url_for('index'))

@app.route('/ejercicios/nuevo', methods=['GET', 'POST'])
def nuevo_ejercicio():
    """Formulario para registrar un nuevo ejercicio."""
    if request.method == 'POST':
        # Obtener datos del formulario
        id_ejercicio = request.form.get('id_ejercicio')
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        grupo_muscular = request.form.get('grupo_muscular')
        
        # Procesar el registro
        try:
            resultado = controlador.registrar_ejercicio(id_ejercicio, nombre, descripcion, grupo_muscular)
            
            if isinstance(resultado, int) and resultado > 0:
                flash('Ejercicio registrado exitosamente', 'success')
                return redirect(url_for('ejercicios'))
            else:
                flash(f'Error al registrar ejercicio: {resultado}', 'danger')
        except Exception as e:
            flash(f'Error en el servidor: {e}', 'danger')
    
    # Si es GET o hay error en POST, mostrar formulario
    return render_template('ejercicios/nuevo.html')

# === RUTAS PARA RUTINAS ===

@app.route('/rutinas')
def rutinas():
    """Lista todas las rutinas disponibles."""
    try:
        lista_rutinas = controlador.obtener_rutinas()
        return render_template('rutinas/lista.html', rutinas=lista_rutinas)
    except Exception as e:
        flash(f'Error al obtener rutinas: {e}', 'danger')
        return redirect(url_for('index'))

@app.route('/rutinas/nueva', methods=['GET', 'POST'])
def nueva_rutina():
    """Formulario para crear una nueva rutina."""
    if request.method == 'POST':
        # Obtener datos del formulario
        id_rutina = request.form.get('id_rutina')
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        nivel_dificultad = request.form.get('nivel_dificultad')
        
        # Procesar el registro
        try:
            resultado = controlador.registrar_rutina(id_rutina, nombre, descripcion, nivel_dificultad)
            
            if isinstance(resultado, int) and resultado > 0:
                flash('Rutina creada exitosamente', 'success')
                return redirect(url_for('rutinas'))
            else:
                flash(f'Error al crear rutina: {resultado}', 'danger')
        except Exception as e:
            flash(f'Error en el servidor: {e}', 'danger')
    
    # Si es GET o hay error en POST, mostrar formulario
    return render_template('rutinas/nueva.html')

@app.route('/rutinas/asignar', methods=['GET', 'POST'])
def asignar_rutina():
    """Formulario para asignar una rutina a un usuario."""
    if request.method == 'POST':
        # Obtener datos del formulario
        id_usuario = request.form.get('id_usuario')
        id_rutina = request.form.get('id_rutina')
        fecha_fin = request.form.get('fecha_fin')
        
        # Procesar la asignación
        try:
            from datetime import datetime
            fecha_asignacion = datetime.now().strftime("%Y-%m-%d")
            resultado = controlador.asignar_rutina_a_usuario(id_usuario, id_rutina, fecha_asignacion, fecha_fin)
            
            if isinstance(resultado, int) and resultado > 0:
                flash('Rutina asignada exitosamente', 'success')
                return redirect(url_for('rutinas'))
            else:
                flash(f'Error al asignar rutina: {resultado}', 'danger')
        except Exception as e:
            flash(f'Error en el servidor: {e}', 'danger')
    
    # Si es GET o hay error en POST, mostrar formulario con listas de usuarios y rutinas
    try:
        usuarios = controlador.obtener_usuarios()
        rutinas_list = controlador.obtener_rutinas()
        return render_template('rutinas/asignar.html', usuarios=usuarios, rutinas=rutinas_list)
    except Exception as e:
        flash(f'Error al cargar datos: {e}', 'danger')
        return redirect(url_for('index'))

# === RUTAS PARA ASISTENCIA ===

@app.route('/asistencia')
def asistencia():
    """Página principal de control de asistencia."""
    try:
        from datetime import datetime
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        lista_asistencias = controlador.obtener_asistencias_por_fecha(fecha_actual)
        return render_template('asistencia/lista.html', asistencias=lista_asistencias, fecha=fecha_actual)
    except Exception as e:
        flash(f'Error al obtener asistencias: {e}', 'danger')
        return redirect(url_for('index'))

@app.route('/asistencia/entrada', methods=['GET', 'POST'])
def registrar_entrada():
    """Formulario para registrar entrada de usuario."""
    if request.method == 'POST':
        id_usuario = request.form.get('id_usuario')
        
        try:
            from datetime import datetime
            fecha = datetime.now().strftime("%Y-%m-%d")
            hora_entrada = datetime.now().strftime("%H:%M:%S")
            
            resultado = controlador.registrar_asistencia(id_usuario, fecha, hora_entrada)
            
            if isinstance(resultado, int) and resultado > 0:
                flash(f'Entrada registrada: {hora_entrada}', 'success')
                return redirect(url_for('asistencia'))
            else:
                flash(f'Error al registrar entrada: {resultado}', 'danger')
        except Exception as e:
            flash(f'Error en el servidor: {e}', 'danger')
    
    # Obtener lista de usuarios para el formulario
    try:
        usuarios = controlador.obtener_usuarios()
        return render_template('asistencia/entrada.html', usuarios=usuarios)
    except Exception as e:
        flash(f'Error al cargar usuarios: {e}', 'danger')
        return redirect(url_for('index'))

# Configurar manejo de errores
@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template('errores/404.html'), 404

@app.errorhandler(500)
def error_servidor(e):
    return render_template('errores/500.html'), 500

# Ejecutar la aplicación si este archivo es el principal
if __name__ == '__main__':
    # Obtener configuración del entorno
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    
    # Iniciar la aplicación
    app.run(debug=debug_mode, host=host, port=port)