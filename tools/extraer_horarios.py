#!/usr/bin/env python3
"""Extrae los horarios del PDF oficial de Ferrovías y actualiza horarios.json.

Uso:
    pip install pdfplumber
    python tools/extraer_horarios.py ruta/al/horario.pdf [horarios.json]

El PDF trae una tabla por página: una fila por tren y una columna por estación.
Cada hora se asigna a su estación según la posición horizontal en la página.
Las estaciones (nombres y coordenadas) se conservan del horarios.json existente;
solo se reemplazan los servicios y los totales.
"""
import collections
import json
import re
import sys

import pdfplumber

N_EST = 23            # estaciones de Retiro a Villa Rosa
X0, PASO = 73.4, 30.74  # posición de la primera columna y ancho de columna (puntos PDF)
HORA = re.compile(r"^\d\d:\d\d$")
TREN = re.compile(r"^\d{4}$")


def leer_pdf(ruta):
    servicios = {}
    with pdfplumber.open(ruta) as pdf:
        for n_pag, pag in enumerate(pdf.pages, 1):
            palabras = [w for w in pag.extract_words() if w.get("upright")]
            ancla = next(w for w in palabras if w["text"] == "TRENES")
            titulo = " ".join(w["text"] for w in palabras if abs(w["top"] - ancla["top"]) < 2)
            dia = "lav" if "VIERNES" in titulo else "sab" if "BADOS" in titulo else "dyf" if "DOMINGOS" in titulo else None
            sentido = "ida" if "VILLA ROSA" in titulo else "vuelta" if "HACIA RETIRO" in titulo else None
            if not dia or not sentido:
                sys.exit(f"Página {n_pag}: no se reconoce el título: {titulo!r}")

            # Agrupar por fila (misma altura, con tolerancia)
            filas = []
            for w in sorted((w for w in palabras if w["top"] > ancla["top"] + 20 and (HORA.match(w["text"]) or TREN.match(w["text"]))), key=lambda w: w["top"]):
                if filas and w["top"] - filas[-1][0] <= 3:
                    filas[-1][1].append(w)
                else:
                    filas.append([w["top"], [w]])

            for _, fila in filas:
                fila.sort(key=lambda w: w["x0"])
                if not TREN.match(fila[0]["text"]):
                    sys.exit(f"Página {n_pag}: fila sin número de tren")
                horas = [None] * N_EST
                for w in fila[1:]:
                    col = (w["x0"] - X0) / PASO
                    i = round(col)
                    if abs(col - i) > 0.1 or not 0 <= i < N_EST or horas[i] is not None:
                        sys.exit(f"Página {n_pag}, tren {fila[0]['text']}: columna inesperada para {w['text']}")
                    horas[i] = w["text"]
                # Las columnas ya vienen en el orden de marcha de cada sentido
                idx = [i for i, h in enumerate(horas) if h]
                tramo = horas[idx[0]: idx[-1] + 1]
                if not all(tramo):
                    sys.exit(f"Página {n_pag}, tren {fila[0]['text']}: paradas no consecutivas")
                servicios.setdefault(dia, {}).setdefault(sentido, []).append(
                    {"tren": fila[0]["text"], "desde": idx[0], "horarios": tramo})
    return servicios


def volcar(doc):
    """JSON legible: una estación y un tren por línea."""
    s = json.dumps(doc, ensure_ascii=False, indent=1)
    s = re.sub(r'\{\s*"tren": "(\d+)",\s*"desde": (\d+),\s*"horarios": \[([^\]]*)\]\s*\}',
               lambda m: '{"tren":"%s","desde":%s,"horarios":[%s]}' % (m.group(1), m.group(2), re.sub(r"\s+", "", m.group(3))), s)
    s = re.sub(r'\{\s*"id": (\d+),\s*("nombre".*?)\s*\}',
               lambda m: '{"id": %s, %s}' % (m.group(1), re.sub(r"\s*\n\s*", " ", m.group(2))), s, flags=re.S)
    return s + "\n"


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    destino = sys.argv[2] if len(sys.argv) > 2 else "horarios.json"
    doc = json.load(open(destino, encoding="utf-8"))
    servicios = leer_pdf(sys.argv[1])
    doc["servicios"] = {d: servicios[d] for d in ("lav", "sab", "dyf")}
    trenes = [t for d in doc["servicios"].values() for s in d.values() for t in s]
    doc["meta"]["total_trenes"] = len(trenes)
    doc["meta"]["total_horarios"] = sum(len(t["horarios"]) for t in trenes)
    open(destino, "w", encoding="utf-8").write(volcar(doc))
    print(f"{destino}: {doc['meta']['total_trenes']} trenes, {doc['meta']['total_horarios']} horarios")
    print("Recordá actualizar meta.horario_numero, meta.vigente_desde y VERSION en sw.js.")


if __name__ == "__main__":
    main()
