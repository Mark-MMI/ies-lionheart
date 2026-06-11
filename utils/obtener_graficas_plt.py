import matplotlib
matplotlib.use("Agg")  # importante: sin interfaz gráfica, se muestran luego en el template
import matplotlib.pyplot as plt
import io, base64
import pandas as pd

#################################
# Gráficas para MATERIA y GRUPO #
#################################
def generar_graficas(df_resumen, columna:str, col_eje:str="MATERIA"):
    if df_resumen.empty or columna not in df_resumen.columns:
        # Imagen en blanco con mensaje por si no hay datos disponibles en el DataFrame o la columna pasada
        fig, ax = plt.subplots(figsize=(6, 2))
        
        fig.patch.set_facecolor("#1e1e2e")
        ax.set_facecolor("#1e1e2e")
        ax.text(0.5, 0.5, "Sin datos para mostrar", color="#666", ha="center", va="center", transform=ax.transAxes, fontsize=12)
        ax.axis("off")
        buf = io.BytesIO()
        plt.savefig(buf, format="png", facecolor="#1e1e2e")
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close()
        return img_b64
    
    # Mostrar los valores en la gráfica desde arriba hasta abajo igual que el orden de la tabla
    df_resumen = df_resumen.sort_index(ascending=False) 
    
    # Para reutilizar la gráfica, se indicará el valor de la columna donde se quiere hacer la gráfica para un match 
    # y se asignen los valores propios a los datos de la columna deseada
    match columna:
        case "%_APROBADOS":
            def color_porcentage(v):
                if v >= 90: return "#4ecb71"
                if v >= 70: return "#a6ff00"
                if v >= 50: return "#f6ff00"
                if v >= 35: return "#ff9100"
                return "#ff0000"

            valor_columna = pd.to_numeric(df_resumen[columna], errors="coerce")
            colores = [color_porcentage(v) if pd.notna(v) else "#444466" for v in valor_columna]
            valor_linea_mitad = 50 # Se usa más tarde para dibujar una línea en la mitad de la gráfica, que indica el punto medio entre aprobado y suspenso
            nombre = "% Aprobados"
            limite_x = 100
            
        case "MEDIA":
            def color_media(v):
                if v >= 9: return "#4ecb71"
                if v >= 7: return "#a6ff00"
                if v >= 5: return "#f6ff00"
                if v >= 3.5: return "#ff9100"
                return "#ff0000"

            valor_columna = pd.to_numeric(df_resumen[columna], errors="coerce")
            colores = [color_media(v) if pd.notna(v) else "#444466" for v in valor_columna]
            valor_linea_mitad = 5 # Se usa más tarde para dibujar una línea en la mitad de la gráfica, que indica el punto medio entre aprobado y suspenso
            nombre = "Media"
            limite_x = 10
        
        case "AUSENCIAS":
            def color_ausencias(v):
                if v >= 200: return "#ff0000"
                if v >= 100: return "#ff9100"
                if v >= 50:  return "#f6ff00"
                return "#4ecb71"

            valor_columna = pd.to_numeric(df_resumen[columna], errors="coerce")
            colores = [color_ausencias(v) if pd.notna(v) else "#444466" for v in valor_columna]
            valor_linea_mitad = None
            nombre = "Ausencias"
            limite_x = valor_columna.max() * 1.1  # dinámico según los datos

    fig, ax = plt.subplots(figsize=(10, max(6, len(df_resumen) * 0.4)))
            
    fig.patch.set_facecolor("#1e1e2e")
    ax.set_facecolor("#1e1e2e")
    ax.barh(df_resumen[col_eje], valor_columna, color=colores)
    ax.set_xlabel(nombre, color="#cfcfe8")
    ax.tick_params(colors="#cfcfe8", labelsize=8)
    ax.spines[:].set_color("#333355")
    ax.set_xlim(0, limite_x)
    if valor_linea_mitad is not None:
        ax.axvline(x=valor_linea_mitad, color="#ffffff33", linestyle="--", linewidth=0.8)  # línea de aprobado en el 5
    
    max_len = df_resumen[col_eje].str.len().max()
    left_margin = min(0.15 + max_len * 0.005, 0.40)  # Margen izquierdo de máximo 40%, dependiendo de la longitud del texto de materia
    plt.tight_layout()
    plt.subplots_adjust(left=left_margin)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", facecolor=fig.get_facecolor())
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    return img_b64


####################################
# Línea para gráfica de ABSENTISMO #
####################################
def generar_grafica_absentismo_linea(df_mes):
    """Línea temporal de ausencias por mes."""
    if df_mes.empty:
        return _grafica_sin_datos()

    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor("#1e1e2e")
    ax.set_facecolor("#1e1e2e")

    ax.plot(df_mes["MES"], df_mes["AUSENCIAS"], color="#6c63ff",
            linewidth=2, marker="o", markersize=5, markerfacecolor="#8a84ff")
    ax.fill_between(df_mes["MES"], df_mes["AUSENCIAS"],
                    alpha=0.15, color="#6c63ff")

    ax.set_xlabel("Mes", color="#cfcfe8")
    ax.set_ylabel("Ausencias", color="#cfcfe8")
    ax.tick_params(colors="#cfcfe8", labelsize=8)
    ax.spines[:].set_color("#333355")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.1, facecolor=fig.get_facecolor())
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    return img_b64


def _grafica_sin_datos():
    """Imagen reutilizable para cuando no hay datos."""
    fig, ax = plt.subplots(figsize=(6, 2))
    fig.patch.set_facecolor("#1e1e2e")
    ax.set_facecolor("#1e1e2e")
    ax.text(0.5, 0.5, "Sin datos para mostrar", color="#666",
            ha="center", va="center", transform=ax.transAxes, fontsize=12)
    ax.axis("off")
    buf = io.BytesIO()
    plt.savefig(buf, format="png", facecolor="#1e1e2e")
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    return img_b64


##################################
# Gráfica para ALUMNOS EN RIESGO #
##################################
def generar_grafica_riesgo_grupos(por_grupo):
    if por_grupo.empty:
        return _grafica_sin_datos()

    fig, ax = plt.subplots(figsize=(10, max(4, len(por_grupo) * 0.4)))
    fig.patch.set_facecolor("#1e1e2e")
    ax.set_facecolor("#1e1e2e")

    grupos = por_grupo["GRUPO"]
    altos  = por_grupo["ALTO"]
    medios = por_grupo["MEDIO"]
    bajos  = por_grupo["BAJO"]

    ax.barh(grupos, bajos,  color="#f6ff00", label="Bajo")
    ax.barh(grupos, medios, left=bajos, color="#ff9100", label="Medio")
    ax.barh(grupos, altos,  left=bajos+medios, color="#ff0000", label="Alto")

    ax.set_xlabel("Alumnos en riesgo", color="#cfcfe8")
    ax.tick_params(colors="#cfcfe8", labelsize=8)
    ax.spines[:].set_color("#333355")
    ax.legend(loc="lower right", facecolor="#2a2a3e", labelcolor="#cfcfe8", fontsize=8)

    max_len = por_grupo["GRUPO"].str.len().max()
    left_margin = min(0.15 + max_len * 0.005, 0.35)
    fig.subplots_adjust(left=left_margin)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", pad_inches=0.1, facecolor=fig.get_facecolor())
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    return img_b64

########################################
# Gráfica para EVOLUCIÓN DE EVALUACIÓN #
########################################
def generar_grafica_evolucion(df_evolucion, titulo="Evolución entre evaluaciones"):
    """Gráfica de líneas doble: nota media y % aprobados por evaluación."""
    if df_evolucion.empty or len(df_evolucion) < 2:
        return _grafica_sin_datos()

    etiquetas = df_evolucion["EVALUACION"].tolist()
    medias    = df_evolucion["MEDIA"].tolist()
    aprobados = df_evolucion["APROBADOS"].tolist()
    x = range(len(etiquetas))

    fig, ax1 = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor("#1e1e2e")
    ax1.set_facecolor("#1e1e2e")

    # Eje izquierdo — nota media (0-10)
    ax1.plot(x, medias, color="#8a84ff", linewidth=2.5, marker="o", markersize=7, markerfacecolor="#6c63ff", label="Nota media")
    ax1.set_ylabel("Nota media", color="#8a84ff", fontsize=9)
    ax1.tick_params(axis="y", colors="#8a84ff", labelsize=8)
    ax1.set_ylim(0, 10)
    ax1.axhline(y=5, color="#ffffff22", linestyle="--", linewidth=0.8)

    # Eje derecho — % aprobados (0-100)
    ax2 = ax1.twinx()
    ax2.plot(x, aprobados, color="#4ecb71", linewidth=2.5, marker="s", markersize=7, markerfacecolor="#36a85a", label="% Aprobados")
    ax2.set_ylabel("% Aprobados", color="#4ecb71", fontsize=9)
    ax2.tick_params(axis="y", colors="#4ecb71", labelsize=8)
    ax2.set_ylim(0, 100)

    # Eje X — etiquetas de evaluación
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(etiquetas, rotation=15, ha="right",
                        color="#cfcfe8", fontsize=8)
    ax1.tick_params(axis="x", colors="#cfcfe8")
    ax1.spines[:].set_color("#333355")
    ax2.spines[:].set_color("#333355")

    # Leyenda combinada
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower left", facecolor="#2a2a3e", labelcolor="#cfcfe8", fontsize=8)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight",
                pad_inches=0.15, facecolor=fig.get_facecolor())
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close()
    return img_b64