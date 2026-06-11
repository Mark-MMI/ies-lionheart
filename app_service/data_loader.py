from utils import obtener_datos as datas
from utils import obtener_graficas_plt as graphs_plt
from utils import obtener_tablas as tables
import pandas as pd
import io, sqlite3
from sqlalchemy import create_engine, text
from flask import send_file

###############################
# IMPORTAR TABLAS A WORKBENCH #
###############################
DATABASE_URL = "mysql+pymysql://root:Datos$1002@localhost/lionheart"

def guardar_en_mysql(df, nombre_tabla):
    """Guarda un DataFrame en MySQL, reemplazando si ya existe."""
    try:
        conexion = create_engine(DATABASE_URL)
        df.to_sql(nombre_tabla, con=conexion, if_exists="replace", index=False)
        return True, f"Tabla '{nombre_tabla}' guardada correctamente en MySQL."
    except Exception as e:
        return False, f"Error al guardar en MySQL: {str(e)}"


#################################
# DESCARGAR TABLAS CON ARREGLOS #
#################################
# Generador de nombres del archivo dependiendo de los filtros
def generar_nombre_archivo(seccion, **filtros):
    """Genera un nombre de archivo descriptivo según los filtros activos."""
    partes = [seccion]
    
    for clave, valor in filtros.items():
        if valor and valor not in ("no", "asc", "desc", "MATERIA", "GRUPO", "AUSENCIAS"):
            valor_limpio = (str(valor)
                .replace(" ", "_")
                .replace("/", "-")
                .replace("º", "").replace("ª", "")
                .replace("(", "").replace(")", "")
                .replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ñ", "n")
                .replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U").replace("Ñ", "N")
            )
            partes.append(valor_limpio)
    
    nombre = "_".join(partes)
    return nombre[:63]  # MySQL permite 64 carácteres, se deja margen por si aca

###### Arreglos
def arreglo_tabla_materias(evaluacion, curso, descarte, grupo, orden_col, orden_dir):
    tabla = datas.obtener_datos_por_materia(evaluacion, curso, descarte, grupo)
    # Limpiar "Sin datos" para exportar valores reales
    tabla = tabla.replace("Sin datos", "")
    
    # Aplicar ordenación
    if not tabla.empty and orden_col in tabla.columns:
        sin_datos = tabla[tabla[orden_col] == ""]
        con_datos = tabla[tabla[orden_col] != ""].copy()
        if orden_col != "MATERIA":
            con_datos[orden_col] = pd.to_numeric(con_datos[orden_col], errors="coerce")
        con_datos = con_datos.sort_values(orden_col, ascending=(orden_dir == "asc"))
        tabla = pd.concat([con_datos, sin_datos], ignore_index=True)
    
    nombre = generar_nombre_archivo("materias", evaluacion=evaluacion, curso=curso, grupo=grupo)
    
    return tabla, nombre

def arreglo_tabla_grupos(evaluacion, estudio, descarte, materia, orden_col, orden_dir):
    tabla = datas.obtener_datos_por_grupo(evaluacion, estudio, descarte, materia)
    # Limpiar "Sin datos" para exportar valores reales
    tabla = tabla.replace("Sin datos", "")
    
    # Aplicar ordenación
    if not tabla.empty and orden_col in tabla.columns:
        sin_datos = tabla[tabla[orden_col] == ""]
        con_datos = tabla[tabla[orden_col] != ""].copy()
        if orden_col != "MATERIA":
            con_datos[orden_col] = pd.to_numeric(con_datos[orden_col], errors="coerce")
        con_datos = con_datos.sort_values(orden_col, ascending=(orden_dir == "asc"))
        tabla = pd.concat([con_datos, sin_datos], ignore_index=True)
    
    nombre = generar_nombre_archivo("grupos", evaluacion=evaluacion, estudio=estudio, materia=materia)
    
    return tabla, nombre

def arreglo_tabla_absentismo(fecha_inicio, fecha_fin, grupo, materia, estudios, tipo, orden_col, orden_dir):
    datos = datas.obtener_datos_absentismo(fecha_inicio, fecha_fin, grupo, materia, estudios)
    tabla = datos["por_grupo"] if tipo == "grupo" else datos["por_materia"]

    if not tabla.empty and orden_col in tabla.columns:
        tabla = tabla.sort_values(orden_col, ascending=(orden_dir == "asc"))

    nombre = generar_nombre_archivo(f"absentismo_{tipo}", fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, grupo=grupo, materia=materia, estudios=estudios)

    return tabla, nombre

###### EXPORTACIÓN Y DESCARGA DEL ARCHIVO
def exportar_tabla(df, nombre_archivo, formato):
    buf = io.BytesIO()

    if formato == "csv":
        df.to_csv(buf, index=False, encoding="utf-8-sig")  # utf-8-sig para Excel en Windows
        buf.seek(0)
        return send_file(buf, mimetype="text/csv", download_name=f"{nombre_archivo}.csv", as_attachment=True)

    elif formato == "xlsx":
        df.to_excel(buf, index=False, engine="openpyxl")
        buf.seek(0)
        return send_file(buf, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", download_name=f"{nombre_archivo}.xlsx", as_attachment=True)

    elif formato == "json":
        buf.write(df.to_json(orient="records", force_ascii=False, indent=2).encode("utf-8"))
        buf.seek(0)
        return send_file(buf, mimetype="application/json", download_name=f"{nombre_archivo}.json", as_attachment=True)

    elif formato == "sqlite":
        # SQLite no trabaja con BytesIO — necesita archivo temporal
        import tempfile, os
        tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        conn = sqlite3.connect(tmp.name)
        df.to_sql(nombre_archivo, conn, if_exists="replace", index=False)
        conn.close()
        return send_file(tmp.name, mimetype="application/x-sqlite3", download_name=f"{nombre_archivo}.db", as_attachment=True)


#####################
# Apartado MATERIAS #
#####################
def cargar_datos_materias(evaluacion, curso, grupo, descarte_sin_datos, orden_col, orden_dir):
    # Creación de la tabla para HTML mediante pandas con .to_html()
    tabla = datas.obtener_datos_por_materia(evaluacion, curso, descarte_sin_datos, grupo)
    
    # Ordenación — protegida por si la columna no existe (ej. df vacío)
    if not tabla.empty and orden_col in tabla.columns:
        ascendente = orden_dir == "asc"
        # Las filas "Sin datos" van siempre al final
        sin_datos = tabla[tabla[orden_col] == "Sin datos"]
        con_datos = tabla[tabla[orden_col] != "Sin datos"].copy()
        if orden_col != "MATERIA":
            con_datos[orden_col] = pd.to_numeric(con_datos[orden_col], errors="coerce")
        con_datos = con_datos.sort_values(orden_col, ascending=ascendente)
        tabla = pd.concat([con_datos, sin_datos], ignore_index=True)
    
    tabla_html = tables.generar_tabla_materias_html(tabla)
    
    # Obtener las graficas en base64 de las materias mediante plt
    grafica_aprobados = graphs_plt.generar_graficas(tabla, "%_APROBADOS")
    grafica_medias = graphs_plt.generar_graficas(tabla, "MEDIA")

    # Listas para los desplegables
    df_notas = datas.lectura_df_notas()
    df_mat = datas.lectura_df_matriculas()
    df_union = df_notas[df_notas["NOTA"].notna()].merge(df_mat, on="MATRICULA")
    
    evaluaciones = sorted(df_union["EVALUACION"].dropna().unique())
    grupos = sorted(df_union["GRUPO"].dropna().unique())
    cursos = sorted(df_union["CURSO"].dropna().unique())
    
    return tabla, tabla_html, evaluaciones, cursos, grupos, grafica_aprobados, grafica_medias

def obtener_evolucion_materias(materia_evolucion):
        df_evolucion_mat = pd.DataFrame()
        if materia_evolucion:
            df_evolucion_mat = datas.obtener_evolucion_por_materia(materia_evolucion)
        
        return graphs_plt.generar_grafica_evolucion(df_evolucion_mat)



###################
# Apartado GRUPOS #
###################
def cargar_datos_grupos(evaluacion, evaluacion_peores, estudios, materia, orden_col, orden_dir, descarte_sin_datos, grupo_detalle=None, top_n=10):
    tabla = datas.obtener_datos_por_grupo(evaluacion, estudios, descarte_sin_datos, materia)

    # Protección por si la columna no existe
    if not tabla.empty and orden_col in tabla.columns:
        ascendente = orden_dir == "asc"
        sin_datos = tabla[tabla[orden_col] == "Sin datos"]
        con_datos = tabla[tabla[orden_col] != "Sin datos"].copy()
        if orden_col != "GRUPO" and orden_col != "ESTUDIOS":
            con_datos[orden_col] = pd.to_numeric(con_datos[orden_col], errors="coerce")
        con_datos = con_datos.sort_values(orden_col, ascending=ascendente)
        tabla = pd.concat([con_datos, sin_datos], ignore_index=True)

    tabla_html = tables.generar_tabla_grupos_html(tabla)
    # Renombro GRUPO por MATERIA para reutilizar la gráfica de materias
    grafica_aprobados = graphs_plt.generar_graficas(
        tabla.rename(columns={"GRUPO": "MATERIA"}), "%_APROBADOS"
    )
    grafica_medias = graphs_plt.generar_graficas(
        tabla.rename(columns={"GRUPO": "MATERIA"}), "MEDIA"
    )

    # Peores materias, solo si se ha seleccionado un grupo concreto
    tabla_peores_html = None
    if grupo_detalle:
        df_peores = datas.obtener_peores_materias_por_grupo(grupo_detalle, evaluacion_peores, top_n)
        tabla_peores_html = tables.generar_tabla_peores_materias_html(df_peores)

    # Desplegables
    df_notas = datas.lectura_df_notas()
    df_mat = datas.lectura_df_matriculas()
    df_union = df_notas[df_notas["NOTA"].notna()].merge(df_mat, on="MATRICULA")

    evaluaciones = sorted(df_union["EVALUACION"].dropna().unique())
    lista_estudios = sorted(df_union["ESTUDIOS"].dropna().unique())
    materias = sorted(df_union["MATERIA"].dropna().unique())
    grupos = sorted(df_union["GRUPO"].dropna().unique())

    return tabla, tabla_html, grafica_aprobados, grafica_medias, tabla_peores_html, evaluaciones, lista_estudios, materias, grupos

def obtener_evolucion_grupos(grupo_evolucion):
    df_evolucion_grp = pd.DataFrame()
    if grupo_evolucion:
        df_evolucion_grp = datas.obtener_evolucion_por_grupo(grupo_evolucion)
    
    return graphs_plt.generar_grafica_evolucion(df_evolucion_grp)


########################
# Apartado ABSENTISMOS #
########################
def cargar_datos_absentismo(fecha_inicio, fecha_fin, grupo, materia, estudios, orden_col, orden_dir):
    datos = datas.obtener_datos_absentismo(fecha_inicio, fecha_fin, grupo, materia, estudios)

    por_grupo = datos["por_grupo"]
    por_materia = datos["por_materia"]

    # Ordenación
    for df, col_ref in [(por_grupo, "GRUPO"), (por_materia, "MATERIA")]:
        if not df.empty and orden_col in df.columns:
            df.sort_values(orden_col, ascending=(orden_dir == "asc"), inplace=True)

    tabla_grupo_html = tables.generar_tabla_absentismo_html(por_grupo, "grupo")
    tabla_materia_html = tables.generar_tabla_absentismo_html(por_materia, "materia")

    grafica_grupo = graphs_plt.generar_graficas(por_grupo, "AUSENCIAS", col_eje="GRUPO")
    grafica_materia = graphs_plt.generar_graficas(por_materia, "AUSENCIAS", col_eje="MATERIA")
    grafica_mes = graphs_plt.generar_grafica_absentismo_linea(datos["por_mes"])

    # Desplegables
    df_f = datas.lectura_df_faltas()
    grupos = sorted(df_f["GRUPO"].dropna().unique())
    materias = sorted(df_f["MATERIA"].dropna().unique())
    estudios_lista = sorted(df_f["ESTUDIOS"].dropna().unique())

    return (datos["totales"], por_grupo, por_materia, tabla_grupo_html, tabla_materia_html,
            grafica_grupo, grafica_materia, grafica_mes, grupos, materias, estudios_lista)


##############################
# Parte de ALUMNOS EN RIESGO #
##############################
def cargar_datos_riesgo(evaluacion, estudios, grupo, min_suspensas, max_media, min_ausencias, tipo_riesgo, orden_col="NIVEL_RIESGO", orden_dir="asc"):
    
    df_riesgo = datas.obtener_alumnado_en_riesgo(
        evaluacion, estudios, grupo, min_suspensas, max_media, min_ausencias, tipo_riesgo)
    
    if not df_riesgo.empty and orden_col in df_riesgo.columns:
        if orden_col == "NIVEL_RIESGO":
            orden_riesgo = {"BAJO": 1, "MEDIO": 2, "ALTO": 3}
            df_riesgo["_orden_riesgo"] = df_riesgo["NIVEL_RIESGO"].map(orden_riesgo)
            df_riesgo = df_riesgo.sort_values(
                "_orden_riesgo", ascending=(orden_dir == "asc")
            ).drop(columns="_orden_riesgo")
        else:
            df_riesgo = df_riesgo.sort_values(orden_col, ascending=(orden_dir == "asc"))

    totales, por_grupo = datas.obtener_resumen_riesgo(df_riesgo)
    tabla_html = tables.generar_tabla_riesgo_html(df_riesgo)
    grafica = graphs_plt.generar_grafica_riesgo_grupos(por_grupo)

    df_notas = datas.lectura_df_notas()
    df_mat = datas.lectura_df_matriculas()
    df_union = df_notas[df_notas["NOTA"].notna()].merge(df_mat, on="MATRICULA")

    evaluaciones  = sorted(df_union["EVALUACION"].dropna().unique())
    estudios_list = sorted(df_union["ESTUDIOS"].dropna().unique())
    grupos_list   = sorted(df_union["GRUPO"].dropna().unique())

    return df_riesgo, tabla_html, grafica, totales, evaluaciones, estudios_list, grupos_list