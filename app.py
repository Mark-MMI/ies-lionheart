from flask import Flask, render_template, request, redirect, url_for, flash, session
from utils import obtener_datos as datas
from utils import obtener_graficas_plt as graphs_plt
from app_service import data_loader as loader

app = Flask(__name__)
app.secret_key = "corazón_de_leon_2026"

#=============================================================================================#

# Usuarios hardcodeados
USUARIOS = {
    "admin": {"password": "Admin$1234", "rol": "admin"},
    "usuario": {"password": "User$1234", "rol": "usuario"}
}

def requiere_login():
    """Devuelve redirect si no hay sesión activa, None si está ok."""
    if "usuario" not in session:
        return redirect(url_for("login"))
    return None

def es_admin():
    return session.get("rol") == "admin"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre = request.form.get("usuario")
        password = request.form.get("password")
        user = USUARIOS.get(nombre)
        if user and user["password"] == password:
            session["usuario"] = nombre
            session["rol"] = user["rol"]
            return redirect(url_for("index"))
        flash("Usuario o contraseña incorrectos.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

#=============================================================================================#

# Protección para las rutas antes de los request
@app.before_request
def proteger_rutas():
    rutas_publicas = ["login", "static"]
    if request.endpoint not in rutas_publicas and "usuario" not in session:
        return redirect(url_for("login"))

#=============================================================================================#

@app.route("/")
def index():    
    datos = datas.obtener_resumen_general()
    
    # Gráfica de evolución de evaluaaciones
    df_evolucion_global = datas.obtener_evolucion_global()
    grafica_evolucion = graphs_plt.generar_grafica_evolucion(df_evolucion_global)


    return render_template("index.html",
        es_admin=es_admin(),
        total_matriculas=datos["total_matriculas"],
        total_grupos=datos["total_grupos"],
        total_materias=datos["total_materias"],
        nota_media_global=datos["nota_media"],
        porcentaje_aprobados=datos["porcentaje_aprobados"],
        porcentaje_repetidores=datos["porcentaje_repetidores"],
        total_evaluados_final=datos["total_evaluados_final"],
        pct_aprobados_final=datos["pct_aprobados_final"],
        grafica_evolucion=grafica_evolucion
    )

#=============================================================================================#

@app.route("/materias")
def materias():
    # Obtención de filtros si procede
    evaluacion = request.args.get("evaluacion") # Por defecto todas
    curso = request.args.get("curso") # Por defecto todas
    grupo = request.args.get("grupo")
    orden_col = request.args.get("ordenar_por", "MATERIA") # Por defecto materia
    orden_dir = request.args.get("orden_dir", "asc") # Por defecto ascendente
    descarte_sin_datos = request.args.get("descarte_sin_datos", "no") == "si" # Por defecto False (no)
    
    tabla, tabla_html, evaluaciones, cursos, grupos, grafica_aprobados, grafica_medias = loader.cargar_datos_materias(
        evaluacion, curso, grupo, descarte_sin_datos, orden_col, orden_dir)
    
    # Seleccionar materia para evolución — por defecto la primera disponible
    materia_evolucion = request.args.get("materia_evolucion")
    grafica_evolucion_mat = loader.obtener_evolucion_materias(materia_evolucion)
    
    return render_template("materias.html",
        es_admin=es_admin(),
        total_registros=len(tabla),
        evaluaciones=evaluaciones,
        cursos=cursos,
        grupos=grupos,
        filtro_evaluacion=evaluacion,
        filtro_curso=curso,
        filtro_grupo=grupo,
        filtro_orden=orden_col,
        filtro_dir=orden_dir,
        filtro_descarte_sin_datos="no" if not descarte_sin_datos else "si",
        grafica_aprobados=grafica_aprobados,
        grafica_medias=grafica_medias,
        tabla_html=tabla_html,
        grafica_evolucion=grafica_evolucion_mat,
        materias_lista=sorted(datas.lectura_df_notas()["MATERIA"].dropna().unique()),
        filtro_materia_evolucion=materia_evolucion
    )

@app.route("/descargar/materias")
def descargar_materias():
    evaluacion = request.args.get("evaluacion")
    curso = request.args.get("curso")
    grupo = request.args.get("grupo")
    descarte = request.args.get("descarte_sin_datos", "no") == "si"
    orden_col = request.args.get("ordenar_por", "MATERIA")
    orden_dir = request.args.get("orden_dir", "asc")
    formato = request.args.get("formato", "csv")

    tabla, nombre = loader.arreglo_tabla_materias(evaluacion, curso, descarte, grupo, orden_col, orden_dir)

    return loader.exportar_tabla(tabla, nombre, formato)

@app.route("/guardar/materias", methods=["POST"]) # Guardar en workbench
def guardar_mysql_materias():
    if not es_admin():
        flash("Necesitas permisos de administrador.", "error")
        return redirect(url_for("materias"))

    evaluacion = request.form.get("evaluacion")
    curso = request.form.get("curso")
    grupo = request.form.get("grupo")
    descarte = request.form.get("descarte_sin_datos", "no") == "si"
    orden_col = request.form.get("ordenar_por", "MATERIA")
    orden_dir = request.form.get("orden_dir", "asc")

    tabla, nombre = loader.arreglo_tabla_materias(evaluacion, curso, descarte, grupo, orden_col, orden_dir)
    ok, mensaje = loader.guardar_en_mysql(tabla, nombre)

    flash(mensaje, "success" if ok else "error")
    qs = request.form.get("query_string", "")
    return redirect(url_for("materias") + ("?" + qs if qs else ""))

#=============================================================================================#

@app.route("/grupos")
def grupos():
    # Obtención de filtros si procede
    evaluacion = request.args.get("evaluacion")
    evaluacion_peores = request.args.get("evaluacion_peores") # Independencia para la segunda tabla
    estudios = request.args.get("estudios")
    materia = request.args.get("materia")
    orden_col = request.args.get("ordenar_por", "GRUPO") # Por defecto "GRUPO"
    orden_dir = request.args.get("orden_dir", "asc") # Por defecto ascendente
    grupo_detalle = request.args.get("grupo_detalle")
    # Por defecto se mostrarán 10 grupos
    # Si no hay un valor convertible a entero, será 10 por defecto
    top_n = int(request.args.get("top_n", 10) or 10)
    descarte_sin_datos = request.args.get("descarte_sin_datos", "no") == "si" # Por defecto False (no)

    # Carga de todas las variables que se usan para la visualización de datos en el render_template
    (tabla, tabla_html, grafica_aprobados, grafica_medias, tabla_peores_html, evaluaciones, 
    lista_estudios, materias, grupos_lista) = loader.cargar_datos_grupos(
        evaluacion, evaluacion_peores, estudios, materia, orden_col, orden_dir, descarte_sin_datos, grupo_detalle, top_n
    )
    
    # Obtención de gráfica para evolución por evaluación
    grupo_evolucion = request.args.get("grupo_evolucion")
    grafica_evolucion_grp = loader.obtener_evolucion_grupos(grupo_evolucion)

    return render_template("grupos.html",
        es_admin=es_admin(),
        total_registros=len(tabla),
        evaluaciones=evaluaciones,
        estudios=lista_estudios,
        materias=materias,
        grupos=grupos_lista,
        filtro_evaluacion=evaluacion,
        filtro_evaluacion_peores=evaluacion_peores,
        filtro_estudios=estudios,
        filtro_materia=materia,
        filtro_orden=orden_col,
        filtro_dir=orden_dir,
        filtro_descarte_sin_datos="no" if descarte_sin_datos == False else "si",
        filtro_grupo_detalle=grupo_detalle,
        filtro_top_n=top_n,
        tabla_html=tabla_html,
        grafica_aprobados=grafica_aprobados,
        grafica_medias=grafica_medias,
        tabla_peores_html=tabla_peores_html,
        grafica_evolucion=grafica_evolucion_grp,
        filtro_grupo_evolucion=grupo_evolucion
    )

@app.route("/descargar/grupos")
def descargar_grupos():
    evaluacion = request.args.get("evaluacion")
    estudio = request.args.get("estudio")
    materia = request.args.get("materia")
    orden_col = request.args.get("ordenar_por", "GRUPO")
    orden_dir = request.args.get("orden_dir", "asc")
    descarte = request.args.get("descarte_sin_datos", "no") == "si"
    formato = request.args.get("formato", "csv")

    tabla, nombre = loader.arreglo_tabla_grupos(evaluacion, estudio, descarte, materia, orden_col, orden_dir)

    return loader.exportar_tabla(tabla, nombre, formato)

@app.route("/guardar/grupos", methods=["POST"])
def guardar_mysql_grupos():
    if not es_admin():
        flash("Necesitas permisos de administrador.", "error")
        return redirect(url_for("grupos"))

    evaluacion = request.form.get("evaluacion")
    estudio = request.form.get("estudio")
    materia = request.form.get("materia")
    descarte = request.form.get("descarte_sin_datos", "no") == "si"
    orden_col = request.form.get("ordenar_por", "GRUPO")
    orden_dir = request.form.get("orden_dir", "asc")

    tabla, nombre = loader.arreglo_tabla_grupos(
        evaluacion, estudio, descarte, materia, orden_col, orden_dir)
    ok, mensaje = loader.guardar_en_mysql(tabla, nombre)

    flash(mensaje, "success" if ok else "error")
    qs = request.form.get("query_string", "")
    return redirect(url_for("grupos") + ("?" + qs if qs else ""))

@app.route("/descargar/peores_materias")
def descargar_peores_materias():
    evaluacion = request.args.get("evaluacion")
    grupo_detalle = request.args.get("grupo_detalle")
    top_n = int(request.args.get("top_n", 10))
    formato = request.args.get("formato", "csv")

    tabla = datas.obtener_peores_materias_por_grupo(grupo_detalle, evaluacion, top_n)
    tabla = tabla.replace("Sin datos", "")

    return loader.exportar_tabla(tabla, f"peores_materias_{grupo_detalle}", formato)

@app.route("/guardar/peores_materias", methods=["POST"])
def guardar_mysql_peores_materias():
    if not es_admin():
        flash("Necesitas permisos de administrador.", "error")
        return redirect(url_for("grupos"))

    evaluacion = request.form.get("evaluacion")
    grupo_detalle = request.form.get("grupo_detalle")
    top_n = int(request.form.get("top_n", 10))

    if not grupo_detalle:
        flash("Selecciona un grupo antes de guardar.", "error")
        return redirect(url_for("grupos"))

    tabla = datas.obtener_peores_materias_por_grupo(grupo_detalle, evaluacion, top_n)
    tabla = tabla.replace("Sin datos", "")
    nombre = loader.generar_nombre_archivo(
        "peores_materias", grupo=grupo_detalle, evaluacion=evaluacion)
    ok, mensaje = loader.guardar_en_mysql(tabla, nombre)

    flash(mensaje, "success" if ok else "error")
    qs = request.form.get("query_string", "")
    return redirect(url_for("grupos") + ("?" + qs if qs else ""))

#=============================================================================================#

@app.route("/absentismo")
def absentismo():
    fecha_inicio = request.args.get("fecha_inicio")
    fecha_fin = request.args.get("fecha_fin")
    grupo = request.args.get("grupo")
    materia = request.args.get("materia")
    estudios = request.args.get("estudios")
    orden_col = request.args.get("ordenar_por", "AUSENCIAS")
    orden_dir = request.args.get("orden_dir", "desc")

    (totales, por_grupo, por_materia, tabla_grupo_html, tabla_materia_html,
    grafica_grupo, grafica_materia, grafica_mes, grupos, materias, estudios_lista) = loader.cargar_datos_absentismo(
        fecha_inicio, fecha_fin, grupo, materia, estudios, orden_col, orden_dir)

    return render_template("absentismo.html",
        es_admin=es_admin(),
        totales=totales,
        total_registros_grupo=len(por_grupo),
        total_registros_materia=len(por_materia),
        tabla_grupo_html=tabla_grupo_html,
        tabla_materia_html=tabla_materia_html,
        grafica_grupo=grafica_grupo,
        grafica_materia=grafica_materia,
        grafica_mes=grafica_mes,
        grupos=grupos,
        materias=materias,
        estudios=estudios_lista,
        filtro_fecha_inicio=fecha_inicio or "",
        filtro_fecha_fin=fecha_fin or "",
        filtro_grupo=grupo,
        filtro_materia=materia,
        filtro_estudios=estudios,
        filtro_orden=orden_col,
        filtro_dir=orden_dir,
    )

@app.route("/descargar/absentismo")
def descargar_absentismo():
    fecha_inicio = request.args.get("fecha_inicio")
    fecha_fin = request.args.get("fecha_fin")
    grupo = request.args.get("grupo")
    materia = request.args.get("materia")
    estudios = request.args.get("estudios")
    tipo = request.args.get("tipo", "grupo")
    orden_col = request.args.get("ordenar_por", "GRUPO" if tipo == "grupo" else "MATERIA")
    orden_dir = request.args.get("orden_dir", "asc")
    formato = request.args.get("formato", "csv")

    tabla, nombre = loader.arreglo_tabla_absentismo(fecha_inicio, fecha_fin, grupo, materia, estudios, tipo, orden_col, orden_dir)

    return loader.exportar_tabla(tabla, nombre, formato)

@app.route("/guardar/absentismo", methods=["POST"])
def guardar_mysql_absentismo():
    if not es_admin():
        flash("Necesitas permisos de administrador.", "error")
        return redirect(url_for("absentismo"))

    fecha_inicio = request.form.get("fecha_inicio")
    fecha_fin = request.form.get("fecha_fin")
    grupo = request.form.get("grupo")
    materia = request.form.get("materia")
    estudios = request.form.get("estudios")
    tipo = request.form.get("tipo", "grupo")
    orden_col = request.form.get("ordenar_por", "GRUPO" if tipo == "grupo" else "MATERIA")
    orden_dir = request.form.get("orden_dir", "asc")

    tabla, nombre = loader.arreglo_tabla_absentismo(
        fecha_inicio, fecha_fin, grupo, materia, estudios, tipo, orden_col, orden_dir)
    ok, mensaje = loader.guardar_en_mysql(tabla, nombre)

    flash(mensaje, "success" if ok else "error")
    qs = request.form.get("query_string", "")
    return redirect(url_for("absentismo") + ("?" + qs if qs else ""))

#=============================================================================================#

@app.route("/riesgo")
def riesgo():
    evaluacion = request.args.get("evaluacion")
    estudios = request.args.get("estudios")
    grupo = request.args.get("grupo")
    min_suspensas = int(request.args.get("min_suspensas", 4))
    max_media = float(request.args.get("max_media", 4))
    min_ausencias = int(request.args.get("min_ausencias", 50))
    orden_col = request.args.get("ordenar_por", "NIVEL_RIESGO")
    orden_dir = request.args.get("orden_dir", "asc")
    tipo_riesgo = request.args.get("tipo_riesgo")

    df_riesgo, tabla_html, grafica, totales, evaluaciones, estudios_list, grupos_list = loader.cargar_datos_riesgo(
        evaluacion, estudios, grupo, min_suspensas, max_media, min_ausencias, tipo_riesgo, orden_col, orden_dir)

    return render_template("riesgo.html",
        es_admin=es_admin(),
        totales=totales,
        tabla_html=tabla_html,
        grafica=grafica,
        total_registros=len(df_riesgo),
        evaluaciones=evaluaciones,
        estudios=estudios_list,
        grupos=grupos_list,
        filtro_evaluacion=evaluacion,
        filtro_estudios=estudios,
        filtro_grupo=grupo,
        filtro_min_suspensas=min_suspensas,
        filtro_max_media=max_media,
        filtro_min_ausencias=min_ausencias,
        filtro_orden=orden_col,
        filtro_dir=orden_dir,
        filtro_riesgo=tipo_riesgo
    )

@app.route("/descargar/riesgo")
def descargar_riesgo():
    evaluacion    = request.args.get("evaluacion")
    estudios      = request.args.get("estudios")
    grupo         = request.args.get("grupo")
    min_suspensas = int(request.args.get("min_suspensas", 4))
    max_media     = float(request.args.get("max_media", 3.5))
    min_ausencias = int(request.args.get("min_ausencias", 100))
    orden_col     = request.args.get("ordenar_por", "NIVEL_RIESGO")
    orden_dir     = request.args.get("orden_dir", "asc")
    formato       = request.args.get("formato", "csv")

    df_riesgo = datas.obtener_alumnado_en_riesgo(
        evaluacion, estudios, grupo, min_suspensas, max_media, min_ausencias)
    
    if not df_riesgo.empty and orden_col in df_riesgo.columns:
        df_riesgo = df_riesgo.sort_values(
            orden_col, ascending=(orden_dir == "asc"))

    nombre = loader.generar_nombre_archivo("riesgo",
        evaluacion=evaluacion, 
        estudios=estudios, 
        grupo=grupo
    )
    return loader.exportar_tabla(df_riesgo, nombre, formato)

@app.route("/guardar/riesgo", methods=["POST"])
def guardar_mysql_riesgo():
    if not es_admin():
        flash("Necesitas permisos de administrador.", "error")
        return redirect(url_for("riesgo"))

    evaluacion    = request.form.get("evaluacion")
    estudios      = request.form.get("estudios")
    grupo         = request.form.get("grupo")
    min_suspensas = int(request.form.get("min_suspensas", 4))
    max_media     = float(request.form.get("max_media", 3.5))
    min_ausencias = int(request.form.get("min_ausencias", 100))
    orden_col     = request.form.get("ordenar_por", "NIVEL_RIESGO")
    orden_dir     = request.form.get("orden_dir", "asc")

    df_riesgo = datas.obtener_alumnado_en_riesgo(
        evaluacion, estudios, grupo,
        min_suspensas, max_media, min_ausencias)
    
    if not df_riesgo.empty and orden_col in df_riesgo.columns:
        df_riesgo = df_riesgo.sort_values(
            orden_col, ascending=(orden_dir == "asc"))

    nombre = loader.generar_nombre_archivo("riesgo",
        evaluacion=evaluacion, estudios=estudios, grupo=grupo)
    ok, mensaje = loader.guardar_en_mysql(df_riesgo, nombre)

    flash(mensaje, "success" if ok else "error")
    qs = request.form.get("query_string", "")
    return redirect(url_for("riesgo") + ("?" + qs if qs else ""))

#=============================================================================================#

@app.route("/acerca")
def acerca():
    redir = requiere_login()
    if redir: return redir
    return render_template("acerca.html")

#=============================================================================================#

if __name__ == "__main__":
    app.run(debug=True)