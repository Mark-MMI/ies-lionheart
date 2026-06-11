##############################################################
# Obtención de tabla HTML para materias con Styler de Pandas #
##############################################################
def generar_tabla_materias_html(resumen):
    """
    Genera una tabla HTML para el apartado de materias, apta desde un DataFrame con estilos propios.
    Se utiliza el Styler de Pandas para los estilos.
    """
    # Si no hay datos válidos, protejo la tabla para que no muestre ningún dato erróneo
    if resumen.empty:
        return '<p class="tabla-vacia">No hay datos para los filtros seleccionados.</p>'
    
    df = resumen.copy()

    def color_media(val):
        if val == "Sin datos": return "color: #888"
        v = float(val)
        if v >= 9: return "color: #4ecb71; font-weight: 500"
        if v >= 7: return "color: #a6ff00; font-weight: 500"
        if v >= 5: return "color: #f6ff00; font-weight: 500"
        if v >= 3.5: return "color: #ff9100; font-weight: 500"
        return "color: #ff0000; font-weight: 500"
    
    def color_pct_aprobados(val):
        if val == "Sin datos": return "color: #888"
        v = float(val)
        if v >= 90: return "color: #4ecb71; font-weight: 500"
        if v >= 70: return "color: #a6ff00; font-weight: 500"
        if v >= 50: return "color: #f6ff00; font-weight: 500"
        if v >= 35: return "color: #ff9100; font-weight: 500"
        return "color: #ff0000; font-weight: 500"

    def color_pct_suspensos(val):
        if val == "Sin datos": return "color: #888"
        v = float(val)
        if v >= 90: return "color: #ff0000; font-weight: 500"
        if v >= 70: return "color: #ff9100; font-weight: 500"
        if v >= 50: return "color: #f6ff00; font-weight: 500"
        if v >= 30: return "color: #a6ff00; font-weight: 500"
        return "color: #4ecb71; font-weight: 500"

    def color_sin_datos(val):
        if val == "Sin datos": return "color: #666; font-style: italic"
        return ""

    styled = (df.style
        .map(color_media, subset=["MEDIA"])
        .map(color_pct_aprobados, subset=["%_APROBADOS"])
        .map(color_pct_suspensos, subset=["%_SUSPENSOS"])
        .map(color_sin_datos, subset=["ALUMNOS", "MEDIA", "EVAL. APROBADAS", "EVAL. SUSPENSAS"])
        .set_table_attributes('class="tabla-datos tabla-materias"')
        .hide(axis="index")
        .format({
            "ALUMNOS": lambda x: x if x == "Sin datos" else f"{int(x)}",
            "MEDIA": lambda x: x if x == "Sin datos" else f"{x:.2f}",
            "EVAL. APROBADAS": lambda x: x if x == "Sin datos" else f"{int(x)}",
            "EVAL. SUSPENSAS": lambda x: x if x == "Sin datos" else f"{int(x)}",
            "%_APROBADOS": lambda x: x if x == "Sin datos" else f"{x:.2f}%",
            "%_SUSPENSOS": lambda x: x if x == "Sin datos" else f"{x:.2f}%",
        })
    )

    return styled.to_html()


###################################################
# Obtención de tabla HTML para grupos con estilos #
###################################################
def generar_tabla_grupos_html(resumen):
    if resumen.empty:
        return '<p class="tabla-vacia">No hay datos para los filtros seleccionados.</p>'

    df = resumen.copy()

    def color_media(val):
        if val == "Sin datos": return "color: #888"
        v = float(val)
        if v >= 9: return "color: #4ecb71; font-weight: 500"
        if v >= 7: return "color: #a6ff00; font-weight: 500"
        if v >= 5: return "color: #f6ff00; font-weight: 500"
        if v >= 3.5: return "color: #ff9100; font-weight: 500"
        return "color: #ff0000; font-weight: 500"

    def color_pct_aprobados(val):
        if val == "Sin datos": return "color: #888"
        v = float(val)
        if v >= 90: return "color: #4ecb71; font-weight: 500"
        if v >= 70: return "color: #a6ff00; font-weight: 500"
        if v >= 50: return "color: #f6ff00; font-weight: 500"
        if v >= 35: return "color: #ff9100; font-weight: 500"
        return "color: #ff0000; font-weight: 500"

    def color_pct_suspensos(val):
        if val == "Sin datos": return "color: #888"
        v = float(val)
        if v >= 90: return "color: #ff0000; font-weight: 500"
        if v >= 70: return "color: #ff9100; font-weight: 500"
        if v >= 50: return "color: #f6ff00; font-weight: 500"
        if v >= 30: return "color: #a6ff00; font-weight: 500"
        return "color: #4ecb71; font-weight: 500"

    def color_sin_datos(val):
        if val == "Sin datos": return "color: #666; font-style: italic"
        return ""

    styled = (df.style
        .map(color_media, subset=["MEDIA"])
        .map(color_pct_aprobados, subset=["%_APROBADOS"])
        .map(color_pct_suspensos, subset=["%_SUSPENSOS"])
        .map(color_sin_datos, subset=["ALUMNOS", "MEDIA", "NOTAS APROBADAS", "NOTAS SUSPENSAS"])
        .set_table_attributes('class="tabla-datos tabla-grupos"')
        .hide(axis="index")
        .format({
            "ALUMNOS": lambda x: x if x == "Sin datos" else f"{int(x)}",
            "MEDIA": lambda x: x if x == "Sin datos" else f"{x:.2f}",
            "NOTAS APROBADAS": lambda x: x if x == "Sin datos" else f"{int(x)}",
            "NOTAS SUSPENSAS": lambda x: x if x == "Sin datos" else f"{int(x)}",
            "%_APROBADOS": lambda x: x if x == "Sin datos" else f"{x:.2f}%",
            "%_SUSPENSOS": lambda x: x if x == "Sin datos" else f"{x:.2f}%",
        })
    )
    return styled.to_html()

### Para opcional de mostrar las peores materias por la media del grupo
def generar_tabla_peores_materias_html(resumen):
    """Tabla secundaria de peores materias por grupo."""
    if resumen.empty:
        return '<p class="tabla-vacia">Sin datos para este grupo.</p>'

    df = resumen.copy()

    def color_media(val):
        if val == "Sin datos": return "color: #888"
        v = float(val)
        if v >= 9: return "color: #4ecb71; font-weight: 500"
        if v >= 7: return "color: #a6ff00; font-weight: 500"
        if v >= 5: return "color: #f6ff00; font-weight: 500"
        if v >= 3.5: return "color: #ff9100; font-weight: 500"
        return "color: #ff0000; font-weight: 500"

    def color_pct_aprobados(val):
        if val == "Sin datos": return "color: #888"
        v = float(val)
        if v >= 90: return "color: #4ecb71; font-weight: 500"
        if v >= 70: return "color: #a6ff00; font-weight: 500"
        if v >= 50: return "color: #f6ff00; font-weight: 500"
        if v >= 35: return "color: #ff9100; font-weight: 500"
        return "color: #ff0000; font-weight: 500"

    def color_pct_suspensos(val):
        if val == "Sin datos": return "color: #888"
        v = float(val)
        if v >= 90: return "color: #ff0000; font-weight: 500"
        if v >= 70: return "color: #ff9100; font-weight: 500"
        if v >= 50: return "color: #f6ff00; font-weight: 500"
        if v >= 30: return "color: #a6ff00; font-weight: 500"
        return "color: #4ecb71; font-weight: 500"

    def color_sin_datos(val):
        if val == "Sin datos": return "color: #666; font-style: italic"
        return ""
    
    styled = (df.style
        .map(color_media, subset=["MEDIA"])
        .map(color_pct_aprobados, subset=["%_APROBADOS"])
        .map(color_sin_datos, subset=["ALUMNOS", "MEDIA"])
        .set_table_attributes('class="tabla-datos tabla-peores-grupos"')
        .hide(axis="index")
        .format({
            "MEDIA": lambda x: f"{x:.2f}",
            "ALUMNOS": lambda x: f"{int(x)}",
            "%_APROBADOS": lambda x: f"{x:.1f}%",
        })
    )
    return styled.to_html()


#######################################################
# Obtención de tabla HTML para absentismo con estilos #
#######################################################
def generar_tabla_absentismo_html(resumen, tipo="grupo"):
    
    df = resumen.copy()
    
    if df.empty:
        return '<p class="tabla-vacia">No hay datos para los filtros seleccionados.</p>'

    col_nombre = "GRUPO" if tipo == "grupo" else "MATERIA"

    def color_ausencias(val):
        v = int(val)
        if v >= 200: return "color: #ff2b2b; font-weight: 500"
        if v >= 100: return "color: #ff952b; font-weight: 500"
        if v >= 50:  return "color: #fff42b; font-weight: 500"
        return "color: #ffffff"

    def color_no_justificadas(val):
        v = int(val)
        if v >= 100: return "color: #ff2b2b; font-weight: 500"
        if v >= 50:  return "color: #ff952b; font-weight: 500"
        if v >= 20:  return "color: #fff42b; font-weight: 500"
        return "color: #ffffff"

    styled = (df.style
        .map(color_ausencias, subset=["AUSENCIAS", "TOTAL"])
        .map(color_no_justificadas, subset=["NO_JUSTIFICADAS"])
        .set_table_attributes(f'class="tabla-datos tabla-absentismo-{tipo}"')
        .hide(axis="index")
        .format({
            "AUSENCIAS": lambda x: f"{int(x)}",
            "RETRASOS": lambda x: f"{int(x)}",
            "JUSTIFICADAS": lambda x: f"{int(x)}",
            "NO_JUSTIFICADAS": lambda x: f"{int(x)}",
            "TOTAL": lambda x: f"{int(x)}",
        })
    )
    return styled.to_html()


###################################
#  Obtención de tabla HTML para   #
#  ALUMNOS EN RIESGO con estilos  #
###################################
def generar_tabla_riesgo_html(df):
    if df.empty:
        return '<p class="tabla-vacia">No hay alumnado en riesgo con los criterios seleccionados.</p>'

    def color_nivel(val):
        if val == "ALTO":  return "color: #ff0000; font-weight: bold"
        if val == "MEDIO": return "color: #ff9100; font-weight: bold"
        if val == "BAJO":  return "color: #f6ff00; font-weight: bold"
        return ""

    def color_suspensas(val):
        v = int(val)
        if v >= 5: return "color: #ff0000; font-weight: 500"
        if v >= 3: return "color: #ff9100; font-weight: 500"
        return "color: #cfcfe8"

    def color_media(val):
        v = float(val)
        if v < 3:   return "color: #ff0000; font-weight: 500"
        if v < 4:   return "color: #ff9100; font-weight: 500"
        if v < 5:   return "color: #f6ff00; font-weight: 500"
        return "color: #cfcfe8"

    def color_ausencias(val):
        v = int(val)
        if v >= 100: return "color: #ff0000; font-weight: 500"
        if v >= 50:  return "color: #ff9100; font-weight: 500"
        if v >= 20:  return "color: #f6ff00; font-weight: 500"
        return "color: #cfcfe8"

    styled = (df.style
        .map(color_nivel, subset=["NIVEL_RIESGO"])
        .map(color_suspensas, subset=["MATERIAS_SUSPENSAS"])
        .map(color_media, subset=["MEDIA"])
        .map(color_ausencias, subset=["AUSENCIAS"])
        .set_table_attributes('class="tabla-datos tabla-riesgo"')
        .hide(axis="index")
        .format({
            "MATRICULA": lambda x: f"{int(x)}",
            "MEDIA": lambda x: f"{x:.2f}",
            "MATERIAS_SUSPENSAS": lambda x: f"{int(x)}",
            "MATERIAS_EVALUADAS": lambda x: f"{int(x)}",
            "AUSENCIAS": lambda x: f"{int(x)}",
            "RETRASOS": lambda x: f"{int(x)}",
        })
    )
    return styled.to_html()