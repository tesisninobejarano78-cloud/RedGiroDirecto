# -*- coding: utf-8 -*-
"""
Corre todos los programas de la red observada, en orden, desde la descarga hasta el visor.

Pasos:
   1. descargar-anexos-giro.py       baja los anexos de Lupa al Giro que falten (necesita internet)
   2. ingerir-anexos-giro.py         lee los anexos y arma la tabla de relaciones
   3. clasificar-prestadores.py      clasifica a cada prestador con el REPS
   4. describir-red-observada.py     descriptivos por mes y cotejo con el boletín de la ADRES
   5. metricas-red-observada.py      red bipartita y métricas de estructura
   6. variables-capa-informacion.py  variables de la capa de información por EPS y mes
   7. verificar-metodos.py           prueba los métodos de redes_metodos.py
   8. teoria-redes-observada.py      centralidad, distribuciones, comunidades y estabilidad
   9. contraste-y-acoplamiento.py    comparación con la red normada y acoplamiento entre capas
  10. proyecciones-y-comparacion.py  proyecciones y comparación con la norma por criterios
  11. figuras-teoria-redes.py        figuras del análisis
  12. construir-visor-observada.py   visor interactivo

Si un paso falla, se detiene y no corre los siguientes.

Opciones:
  --sin-descarga   no baja anexos: usa los que ya están en datos/anexos/
  --reps-nuevo     baja un extracto nuevo del REPS antes de clasificar (por defecto se usa el último
                   extracto guardado, para que los resultados no cambien de una corrida a otra)
  --desde PASO     empieza en ese paso (número de la lista), por ejemplo --desde 8

Ejecutar:  python correr-todo.py [--sin-descarga] [--reps-nuevo] [--desde PASO]
"""
import argparse
import os
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
PASOS = [
    "descargar-anexos-giro.py",
    "ingerir-anexos-giro.py",
    "clasificar-prestadores.py",
    "describir-red-observada.py",
    "metricas-red-observada.py",
    "variables-capa-informacion.py",
    "verificar-metodos.py",
    "teoria-redes-observada.py",
    "contraste-y-acoplamiento.py",
    "proyecciones-y-comparacion.py",
    "figuras-teoria-redes.py",
    "construir-visor-observada.py",
]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Corre todos los programas de la red observada.")
    ap.add_argument("--sin-descarga", action="store_true", help="no bajar anexos")
    ap.add_argument("--reps-nuevo", action="store_true", help="bajar un extracto nuevo del REPS")
    ap.add_argument("--desde", type=int, default=1, help="paso en el que se empieza (1 a %d)" % len(PASOS))
    args = ap.parse_args()
    if not 1 <= args.desde <= len(PASOS):
        ap.error("--desde debe estar entre 1 y %d" % len(PASOS))

    entorno = dict(os.environ, PYTHONIOENCODING="utf-8")
    inicio = time.time()
    for n, programa in enumerate(PASOS, start=1):
        if n < args.desde or (programa == "descargar-anexos-giro.py" and args.sin_descarga):
            continue
        extra = ["--descargar"] if programa == "clasificar-prestadores.py" and args.reps_nuevo else []
        print("\n=== Paso %d de %d: %s" % (n, len(PASOS), programa), flush=True)
        t = time.time()
        r = subprocess.run([sys.executable, os.path.join(AQUI, programa)] + extra, cwd=AQUI, env=entorno)
        if r.returncode != 0:
            sys.exit("\nEl paso %d (%s) falló. Los pasos siguientes no se corrieron." % (n, programa))
        print("=== %s terminó en %.0f s" % (programa, time.time() - t), flush=True)
    print("\nTodo listo en %.0f s. Resultados en salida/ y visor en visor-red-observada.html."
          % (time.time() - inicio))


if __name__ == "__main__":
    main()
