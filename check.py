# archivo de chequeo
import pandas as pd
from utils import obtener_datos as datas

########## ¿Por qué hay 215 materias disponibles pero, en materias y sin filtros, aparecen sólo 214?
df_notas = datas.lectura_df_notas()

df = datas.merge_notas_matriculas()

materias_notas = set(df_notas["MATERIA"].dropna().unique())
materias_merge = set(df["MATERIA"].dropna().unique())

print("\nMaterias en notas:", len(materias_notas))
print("Materias tras merge:", len(materias_merge))
print("Materia que falta:", materias_notas - materias_merge)
print("""- Posible explicación -> Seguramente todos los alumnos de esa materia hayan anulado su matrícula.
Por esa razón, al limpiar el archivo de primeras, dropeando los NaN, al haber notas o registros se ha mantenido.
Pero en matrícula, si todos los alumnos anularon la matrícula, entonces se quita el registro entero.\n""")

########## Comprobación del merge para abreviaturas de asignaturas en materias_centro.csv con datNotas
df_materias = datas.lectura_df_materias()
df_materias = df_materias.rename(columns={"DESCRIPCION": "MATERIA"})
df_abreviaturas = df_notas.merge(df_materias, on="MATERIA")

print("Nº de asignaturas a las que se les podía asignar abreviatura:", df_abreviaturas["MATERIA"].nunique())