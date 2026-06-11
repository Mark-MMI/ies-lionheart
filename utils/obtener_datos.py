import pandas as pd
import numpy as np

def lectura_df_faltas():
    return pd.read_csv("data/datFaltas.csv", sep=";", encoding="latin1")

def lectura_df_matriculas(anuladas=False):
    """
    Leo el archivo de datMatriculas con unas columnas por defecto, para no usar las que contengan datos personales o
    que no se vayan a utilizar.
    Con anuladas indico si incluir o no las matrículas anuladas al total de matrículas. Si se quieren saber, se generará un valor
    entero como variable a parte de la del DF.
    """
    cols = ["MATRICULA", "ETAPA", "ANNO", "ESTUDIOS", "GRUPO", "REPETIDOR", "ESTADOMATRICULA"]
    
    df_mat = pd.read_csv("data/datMatriculas.csv", sep=";", encoding="latin1", usecols=cols)
    df_mat_sin_anuladas = df_mat[df_mat["ESTADOMATRICULA"] != "Anulada"] # Quito las matrículas anuladas para que no cuenten en los datos
    mat_anuladas = 0
    if anuladas: 
        mat_anuladas = df_mat[df_mat["ESTADOMATRICULA"] == "Anulada"].shape[0]
        return df_mat_sin_anuladas, mat_anuladas
    return df_mat_sin_anuladas

def lectura_df_notas():
    # Al haber cursos que no ponen direcramente valor numérico sino sobresaliente, notable... o apto o no apto,
    # Se hará un mapeo donde se asigna un valor numérico que se acerque aprox. al valor real.
    df_notas = pd.read_csv("data/datNotas.csv", sep=";", encoding="latin1")
    mapeo = {
        "Sobresaliente": "9.5", 
        "Notable": "8", 
        "Bien": "6.5", 
        "Suficiente": "5.5", 
        "Insuficiente": "2.5",
        "Apto": "7.5",
        "No apto": "2.5"
    }
    # Si uso .map(), me reemplaza lo que le digo, pero lo que no esté en el diccionario lo toma como NaN
    # Mejor guardar el diccionario de cambios y usar .replace(), que sólo cambia lo indicado
    df_notas["NOTA"] = df_notas["NOTA"].replace(mapeo)
    df_notas["NOTA"] = pd.to_numeric(df_notas["NOTA"], errors="coerce")
    return df_notas

# def lectura_df_unidades():
#     # !!! No aporta información que no esté en las demás tablas
#     return pd.read_csv("data/datUnidades.csv", sep=";", encoding="latin1")

# def lectura_df_materias(): 
#     # !!!!!! No se pueden poner las abreviaturas porque no coge la totalidad de materias al haber discrepancias entre nombres
#     # En los merges, sólo es capaz de asignar ===> 86 <=== abreviaturas
#     return pd.read_csv("data/materias_centro.csv", sep=";", encoding="latin1")

def merge_notas_matriculas():
    """
    Función auxiliar deduplicada que une datNotas con datMatriculas por MATRICULA 
    para evitar repetir el merge en cada función de análisis.
    """
    return lectura_df_notas().merge(lectura_df_matriculas(), on="MATRICULA")

#######################################################
# Función principal de obtención de datos para Inicio #
#######################################################

def obtener_resumen_general():
    """
    Se obtendrán los datos necesarios para mostrar en las tarjetas del dashboard (total de matrículas, materias, aprobados...)
    y los datos que pasar para gráficas y referencias.
    """
    
    # Importo ambas porque hay datos que se tienen que sacar de un csv unitariamente
    df_notas = lectura_df_notas()
    df_mat = lectura_df_matriculas()

    # limpieza + unión (join)
    df = merge_notas_matriculas()
    df_notas_validas = df[df["NOTA"].notna()]

    # conteos
    total_matriculas = df_mat["MATRICULA"].nunique()
    total_grupos = df_mat["GRUPO"].nunique()
    total_materias = df_notas["MATERIA"].nunique()
    nota_media = df_notas_validas["NOTA"].mean()

    aprobados = (df_notas_validas["NOTA"] >= 5).sum()
    total_notas = len(df_notas_validas)
    porcentaje_aprobados = round((aprobados / total_notas) * 100, 2)
    
    repetidores = df_mat[df_mat["REPETIDOR"] == "S"]["MATRICULA"].nunique() # Obtengo la cantidad total de repetidores únicos respecto a matrícula
    porcentaje_repetidores = round((repetidores / total_matriculas) * 100, 2)
    
    aprobados_final = (df_notas_validas[df_notas_validas["EVALUACION"] == "Primera Ordinaria"]["NOTA"] >= 5).sum()
    total_notas_finales = len(df_notas_validas[df_notas_validas["EVALUACION"] == "Primera Ordinaria"])
    pct_aprobados_final = round((aprobados_final / total_notas_finales) * 100, 2)

    return {
        "total_matriculas": total_matriculas,
        "total_grupos": total_grupos,
        "total_materias": total_materias,
        "nota_media": nota_media,
        "porcentaje_aprobados": porcentaje_aprobados,
        "porcentaje_repetidores": porcentaje_repetidores,
        "total_evaluados_final": total_notas_finales,
        "pct_aprobados_final": pct_aprobados_final
    }

###############################################
# Función de obtención de datos para Materias #
###############################################

def obtener_datos_por_materia(evaluacion=None, curso=None, descarte_sin_datos=False, grupo=None):
    """
    Une notas y matrículas aplicando filtros dinámicos de Jinja2.
    descarte_sin_datos: Si se pone en True, eliminará de la tabla final las asignaturas pendientes o evaluaciones vacías que devuelvan "Sin datos".
    Con estos datos, hago las métricas para entregar el DataFrame con la información deseada (nº total de ALUMNOS, media, 
    arpobados, etc.) agrupados por materia.
    """

    # Merge de TODAS las matrículas con notas
    df = merge_notas_matriculas()

    # Aplicar filtros
    if evaluacion:
        df = df[df["EVALUACION"] == evaluacion]
    if curso:
        df = df[df["CURSO"] == curso]
    if grupo:
        df = df[df["GRUPO"] == grupo]
    
    # Si con los filtros no hay datos en el DataFrame, se devuelven las columnas
    if df.empty:
        return pd.DataFrame(columns=["MATERIA", "ALUMNOS", "MEDIA", "EVAL. APROBADAS", "EVAL. SUSPENSAS", "%_APROBADOS", "%_SUSPENSOS"])

    # Me quedo con la última nota por alumno y materia (deduplicar) si hay un filtro de evaluación
    if evaluacion:
        df = df.sort_values("EVALUACION").groupby(
            ["MATRICULA", "MATERIA"], as_index=False
        ).last()
    
    # Agrupamiento y calculo de métricas por materia
    def metricas(g):
        notas = g["NOTA"].dropna()
        
        con_nota = len(notas)
        if con_nota == 0:
            return pd.Series({
                "ALUMNOS": np.nan,
                "MEDIA": np.nan,
                "EVAL. APROBADAS": np.nan,
                "EVAL. SUSPENSAS": np.nan,
                "%_APROBADOS": np.nan,
                "%_SUSPENSOS": np.nan,
            })
        
        media = round(notas.mean(), 2)
        aprobados = int((notas >= 5).sum())
        suspensos = int((notas < 5).sum())
        pct_aprobados = round((notas >= 5).mean() * 100, 1)
        pct_suspensos = round((notas < 5).mean() * 100, 1)
        
        return pd.Series({
            "ALUMNOS": g["MATRICULA"].nunique(),
            "MEDIA": media,
            "EVAL. APROBADAS": aprobados,
            "EVAL. SUSPENSAS": suspensos,
            "%_APROBADOS": pct_aprobados,
            "%_SUSPENSOS": pct_suspensos,
        })
    
    resumen = df.groupby("MATERIA").apply(metricas, include_groups=False).reset_index()
    
    # Si se quiere limpiar las materias "fantasma" o vacías del listado:
    if descarte_sin_datos:
        resumen = resumen.dropna(subset=["ALUMNOS"])
    
    # Rellenar los registros que legítimamente no tengan notas en esa evaluación
    resumen = resumen.fillna("Sin datos")

    return resumen

#################################################
# Funciones de obtención de datos para Grupos   #
#################################################

def obtener_datos_por_grupo(evaluacion=None, estudios=None, descarte_sin_datos=False, materia=None):
    """
    Se generará un DataFrame, agrupado por 'GRUPO', con la información existente para los grupos
    del centro dependiendo de los filtros aplicados.
    """
    
    df = merge_notas_matriculas()

    if evaluacion:
        df = df[df["EVALUACION"] == evaluacion]
    if estudios:
        df = df[df["ESTUDIOS"] == estudios]
    if materia:
        df = df[df["MATERIA"] == materia]

    if df.empty:
        return pd.DataFrame(columns=["GRUPO", "ESTUDIOS", "ALUMNOS", "MEDIA", "NOTAS APROBADAS", "NOTAS SUSPENSAS", "%_APROBADOS", "%_SUSPENSOS"])

    # Me quedo con la última nota por alumno y materia si hay un filtro de evaluación
    if evaluacion:
        df = df.sort_values("EVALUACION").groupby(
            ["MATRICULA", "MATERIA"], as_index=False
        ).last()

    def metricas(g):
        notas = g["NOTA"].dropna()
        con_nota = len(notas)
        estudios_val = g["ESTUDIOS"].iloc[0] if not g["ESTUDIOS"].isna().all() else "Sin datos"
        if con_nota == 0:
            return pd.Series({
                "ESTUDIOS": estudios_val, 
                "ALUMNOS": np.nan, 
                "MEDIA": np.nan, 
                "NOTAS APROBADAS": np.nan, 
                "NOTAS SUSPENSAS": np.nan, 
                "%_APROBADOS": np.nan,
                "%_SUSPENSOS": np.nan})
        return pd.Series({
            "ESTUDIOS": estudios_val,
            "ALUMNOS": g["MATRICULA"].nunique(),
            "MEDIA": round(notas.mean(), 2),
            "NOTAS APROBADAS": int((notas >= 5).sum()),
            "NOTAS SUSPENSAS": int((notas < 5).sum()),
            "%_APROBADOS": round((notas >= 5).mean() * 100, 1),
            "%_SUSPENSOS": round((notas < 5).mean() * 100, 1),
        })

    resumen = df.groupby("GRUPO").apply(metricas, include_groups=False).reset_index()
    
    # Si se quiere limpiar las materias "fantasma" o vacías del listado
    if descarte_sin_datos:
        resumen = resumen.dropna(subset=["ALUMNOS"])
    
    # Rellenar los registros que legítimamente no tengan notas en esa evaluación
    resumen = resumen.fillna("Sin datos")

    return resumen


def obtener_peores_materias_por_grupo(grupo, evaluacion=None, top_n=10):
    """Devuelve las top_n materias con peor media para un grupo dado. Por defecto top 10."""

    df = merge_notas_matriculas()
    df = df[df["GRUPO"] == grupo]

    if evaluacion:
        df = df[df["EVALUACION"] == evaluacion]

    df_val = df[df["NOTA"].notna()]
    if df_val.empty:
        return pd.DataFrame(columns=["MATERIA", "MEDIA", "ALUMNOS", "%_APROBADOS"])

    # Quedarse con la última nota por alumno y materia
    df_val = df_val.sort_values("EVALUACION").groupby(
        ["MATRICULA", "MATERIA"], as_index=False
    ).last()

    resumen = df_val.groupby("MATERIA").apply(lambda g: pd.Series({
        "MEDIA": round(g["NOTA"].mean(), 2),
        "ALUMNOS": g["MATRICULA"].nunique(), # Sólo quiero alumnos únicos
        "%_APROBADOS": round((g["NOTA"] >= 5).mean() * 100, 1),
    })).reset_index()

    return resumen.sort_values("MEDIA").head(top_n)

###################################################
# Función de obtención de datos para ABSENTISMO   #
###################################################

def obtener_datos_absentismo(fecha_inicio=None, fecha_fin=None, grupo=None, materia=None, estudios=None):
    """
    Obtención de diferentes DataFrames para las tarjetas, indicando los datos de absistencia por grupo,
    materia, mes y el total.
    """
    
    df_faltas = lectura_df_faltas()
    
    # Convertir fecha a datetime
    df_faltas["FECHA_FALTA"] = pd.to_datetime(df_faltas["FECHA_FALTA"], format="%d/%m/%Y", errors="coerce")

    # Filtros
    if fecha_inicio:
        df_faltas = df_faltas[df_faltas["FECHA_FALTA"] >= pd.to_datetime(fecha_inicio)]
    if fecha_fin:
        df_faltas = df_faltas[df_faltas["FECHA_FALTA"] <= pd.to_datetime(fecha_fin)]
    if grupo:
        df_faltas = df_faltas[df_faltas["GRUPO"] == grupo]
    if materia:
        df_faltas = df_faltas[df_faltas["MATERIA"] == materia]
    if estudios:
        df_faltas = df_faltas[df_faltas["ESTUDIOS"] == estudios]

    if df_faltas.empty:
        return {
            "por_grupo": pd.DataFrame(columns=["GRUPO", "AUSENCIAS", "RETRASOS", "JUSTIFICADAS", "NO_JUSTIFICADAS", "TOTAL"]),
            "por_materia": pd.DataFrame(columns=["MATERIA", "AUSENCIAS", "RETRASOS", "JUSTIFICADAS", "NO_JUSTIFICADAS", "TOTAL"]),
            "por_mes": pd.DataFrame(columns=["MES", "AUSENCIAS"]),
            "totales": {"ausencias": 0, "retrasos": 0, "justificadas": 0, "no_justificadas": 0, "total": 0}
        }

    # Métricas globales
    totales = {
        "ausencias": int(df_faltas["AUSENCIAS"].sum()),
        "retrasos": int(df_faltas["RETRASOS"].sum()),
        "justificadas": int(df_faltas["JUSTIFICADAS"].sum()),
        "no_justificadas": int(df_faltas["AUSENCIAS"].sum() - df_faltas["JUSTIFICADAS"].sum()),
        "total": int(df_faltas["AUSENCIAS"].sum() + df_faltas["RETRASOS"].sum()),
    }

    # Por grupo
    por_grupo = df_faltas.groupby("GRUPO").agg(
        AUSENCIAS=("AUSENCIAS", "sum"),
        RETRASOS=("RETRASOS", "sum"),
        JUSTIFICADAS=("JUSTIFICADAS", "sum"),
    ).reset_index()
    por_grupo["NO_JUSTIFICADAS"] = por_grupo["AUSENCIAS"] - por_grupo["JUSTIFICADAS"]
    por_grupo["TOTAL"] = por_grupo["AUSENCIAS"] + por_grupo["RETRASOS"]
    por_grupo = por_grupo.sort_values("AUSENCIAS", ascending=False)

    # Por materia
    por_materia = df_faltas.groupby("MATERIA").agg(
        AUSENCIAS=("AUSENCIAS", "sum"),
        RETRASOS=("RETRASOS", "sum"),
        JUSTIFICADAS=("JUSTIFICADAS", "sum"),
    ).reset_index()
    por_materia["NO_JUSTIFICADAS"] = por_materia["AUSENCIAS"] - por_materia["JUSTIFICADAS"]
    por_materia["TOTAL"] = por_materia["AUSENCIAS"] + por_materia["RETRASOS"]
    por_materia = por_materia.sort_values("AUSENCIAS", ascending=False)

    # Por mes
    df_faltas["MES"] = df_faltas["FECHA_FALTA"].dt.to_period("M")
    por_mes = df_faltas.groupby("MES")["AUSENCIAS"].sum().reset_index()
    por_mes["MES"] = por_mes["MES"].astype(str)
    por_mes = por_mes.sort_values("MES")

    return {
        "por_grupo": por_grupo,
        "por_materia": por_materia,
        "por_mes": por_mes,
        "totales": totales
    }

#############################################
# Función de obtención de datos para Riesgo #
#############################################

def obtener_alumnado_en_riesgo(evaluacion=None, estudios=None, grupo=None, min_suspensas=3, max_media=4.0, min_ausencias=50, tipo_riesgo=None):
    """ 
    Identifica al alumnado en situación de riesgo académico, cruzando datos de notas y absentismo, según 3 criterios:
    Mínimo de asignaturas suspensas (por defecto 3), máxima nota media (por defecto 4) y mínimo de ausencias (por defecto 50).
    Se asigna un riesgo de bajo, medio o alto dependiendo de si cumple de 1 a 3 criterios respectivamente.
    """    
    
    df = merge_notas_matriculas()
    df_faltas = lectura_df_faltas()

    if evaluacion:
        df = df[df["EVALUACION"] == evaluacion]
    if estudios:
        df = df[df["ESTUDIOS"] == estudios]
    if grupo:
        df = df[df["GRUPO"] == grupo]

    if df.empty:
        return pd.DataFrame(columns=[
            "MATRICULA","GRUPO","ESTUDIOS","MEDIA", "MATERIAS_SUSPENSAS","MATERIAS_EVALUADAS",
            "AUSENCIAS","RETRASOS","NIVEL_RIESGO"
        ])

    df_val = df[df["NOTA"].notna()]
    if not evaluacion:
        df_val = df_val.sort_values("EVALUACION").groupby(
            ["MATRICULA", "MATERIA"], as_index=False).last()

    # Métricas académicas por alumno
    resumen = df_val.groupby("MATRICULA").agg(
        GRUPO=("GRUPO", "first"),
        ESTUDIOS=("ESTUDIOS", "first"),
        MEDIA=("NOTA", "mean"),
        MATERIAS_SUSPENSAS=("NOTA", lambda x: int((x < 5).sum())),
        MATERIAS_EVALUADAS=("NOTA", "count"),
    ).reset_index()
    resumen["MEDIA"] = resumen["MEDIA"].round(2)

    # Absentismo por alumno
    df_faltas_agg = df_faltas.groupby("EXPEDIENTE").agg(
        AUSENCIAS=("AUSENCIAS", "sum"),
        RETRASOS=("RETRASOS", "sum"),
    ).reset_index().rename(columns={"EXPEDIENTE": "MATRICULA"})

    resumen = resumen.merge(df_faltas_agg, on="MATRICULA", how="left")
    resumen["AUSENCIAS"] = resumen["AUSENCIAS"].fillna(0).astype(int)
    resumen["RETRASOS"] = resumen["RETRASOS"].fillna(0).astype(int)

    # Calcular nivel de riesgo según cuántos criterios cumple
    def nivel_riesgo(row):
        criterios = 0
        if row["MATERIAS_SUSPENSAS"] >= min_suspensas:
            criterios += 1
        if row["MEDIA"] <= max_media:
            criterios += 1
        if row["AUSENCIAS"] >= min_ausencias:
            criterios += 1
        if criterios == 3:
            return "ALTO"
        if criterios == 2:
            return "MEDIO"
        if criterios == 1:
            return "BAJO"
        return None  # Sin riesgo

    resumen["NIVEL_RIESGO"] = resumen.apply(nivel_riesgo, axis=1)

    # Solo alumnos con algún criterio de riesgo
    resumen = resumen[resumen["NIVEL_RIESGO"].notna()]
    
    if tipo_riesgo:
        resumen = resumen[resumen["NIVEL_RIESGO"] == tipo_riesgo]
    
    orden_riesgo = {"ALTO": 3, "MEDIO": 2, "BAJO": 1}
    resumen["_orden_riesgo"] = resumen["NIVEL_RIESGO"].map(orden_riesgo) # Creo una columna auxiliar temporal
    resumen = resumen.sort_values(
        ["_orden_riesgo", "MATERIAS_SUSPENSAS"],
        ascending=[True, False]  # BAJO primero
    ).drop(columns="_orden_riesgo")
    
    return resumen


def obtener_resumen_riesgo(df_riesgo):
    """Cuenta alumnos por nivel y grupos con más riesgo."""
    if df_riesgo.empty:
        return {"alto": 0, "medio": 0, "bajo": 0, "total": 0}, pd.DataFrame()

    conteo = df_riesgo["NIVEL_RIESGO"].value_counts().to_dict()
    totales = {
        "alto": conteo.get("ALTO", 0),
        "medio": conteo.get("MEDIO", 0),
        "bajo": conteo.get("BAJO", 0),
        "total": len(df_riesgo)
    }

    por_grupo = df_riesgo.groupby("GRUPO").agg(
        TOTAL_RIESGO=("MATRICULA", "count"),
        ALTO=("NIVEL_RIESGO", lambda x: (x == "ALTO").sum()),
        MEDIO=("NIVEL_RIESGO", lambda x: (x == "MEDIO").sum()),
        BAJO=("NIVEL_RIESGO", lambda x: (x == "BAJO").sum()),
    ).reset_index().sort_values("TOTAL_RIESGO", ascending=False)

    return totales, por_grupo

###################################################
# Funciones de evolución entre evaluaciones       #
###################################################

ORDEN_EVALUACIONES = [
    "1ª Evaluación",
    "Recuperación de 1ª",
    "2ª Evaluación",
    "Primera Ordinaria",
    "Segunda Ordinaria",
]

def obtener_evolucion_global():
    """Evolución de nota media y % aprobados por evaluación — vista global del centro."""
    df_notas = lectura_df_notas()
    df_val = df_notas[df_notas["NOTA"].notna()]

    resumen = df_val.groupby("EVALUACION").agg(
        MEDIA=("NOTA", "mean"),
        APROBADOS=("NOTA", lambda x: (x >= 5).mean() * 100),
        TOTAL=("NOTA", "count"),
    ).reset_index()

    resumen["MEDIA"] = resumen["MEDIA"].round(2)
    resumen["APROBADOS"] = resumen["APROBADOS"].round(1)

    # Ordenar según el orden lógico del curso
    resumen["_orden"] = resumen["EVALUACION"].map(
        {e: i for i, e in enumerate(ORDEN_EVALUACIONES)}
    )
    resumen = resumen.sort_values("_orden").drop(columns="_orden")
    resumen = resumen[resumen["EVALUACION"].isin(ORDEN_EVALUACIONES)]

    return resumen


def obtener_evolucion_por_materia(materia):
    """Evolución de una materia concreta entre evaluaciones."""
    df_notas = lectura_df_notas()
    df_val = df_notas[(df_notas["NOTA"].notna()) & (df_notas["MATERIA"] == materia)]

    if df_val.empty:
        return pd.DataFrame(columns=["EVALUACION", "MEDIA", "APROBADOS", "TOTAL"])

    resumen = df_val.groupby("EVALUACION").agg(
        MEDIA=("NOTA", "mean"),
        APROBADOS=("NOTA", lambda x: (x >= 5).mean() * 100),
        TOTAL=("NOTA", "count"),
    ).reset_index()

    resumen["MEDIA"] = resumen["MEDIA"].round(2)
    resumen["APROBADOS"] = resumen["APROBADOS"].round(1)
    resumen["_orden"] = resumen["EVALUACION"].map(
        {e: i for i, e in enumerate(ORDEN_EVALUACIONES)}
    )
    resumen = resumen.sort_values("_orden").drop(columns="_orden")
    resumen = resumen[resumen["EVALUACION"].isin(ORDEN_EVALUACIONES)]

    return resumen


def obtener_evolucion_por_grupo(grupo):
    """Evolución de un grupo concreto entre evaluaciones."""
    df = merge_notas_matriculas()
    df_val = df[(df["NOTA"].notna()) & (df["GRUPO"] == grupo)]

    if df_val.empty:
        return pd.DataFrame(columns=["EVALUACION", "MEDIA", "APROBADOS", "TOTAL"])

    resumen = df_val.groupby("EVALUACION").agg(
        MEDIA=("NOTA", "mean"),
        APROBADOS=("NOTA", lambda x: (x >= 5).mean() * 100),
        TOTAL=("NOTA", "count"),
    ).reset_index()

    resumen["MEDIA"] = resumen["MEDIA"].round(2)
    resumen["APROBADOS"] = resumen["APROBADOS"].round(1)
    resumen["_orden"] = resumen["EVALUACION"].map(
        {e: i for i, e in enumerate(ORDEN_EVALUACIONES)}
    )
    resumen = resumen.sort_values("_orden").drop(columns="_orden")
    resumen = resumen[resumen["EVALUACION"].isin(ORDEN_EVALUACIONES)]

    return resumen