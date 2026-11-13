# Horarios de trenes: Belgrano Norte

Web app que muestra las próximas salidas del tren Belgrano Norte (Ferrovías, Retiro a Villa Rosa) desde la estación más cercana a tu ubicación. Pensada para el celular: se puede instalar en Android y funciona sin conexión.

**Demo:** https://matiasperrone.github.io/horarios-trenes/

> Sitio no oficial. Muestra horarios programados, no el estado del servicio en tiempo real.

## Qué hace

- Elige la estación más cercana usando el GPS del dispositivo.
- Muestra las próximas salidas en ambos sentidos, con destino, número de tren, hora de llegada y cuenta regresiva.
- Botón **Cambiar estación** para elegir otra a mano, o volver al modo automático.
- Botón **Estaciones favoritas** para elegir hasta 3 destinos habituales. Con favoritas elegidas, la app muestra las salidas que llegan a cada una, con la hora de llegada y la duración del viaje, en lugar de los destinos terminales. Se pueden cambiar en cualquier momento y quedan guardadas en el dispositivo.
- Botón **Hoy es feriado** para aplicar el horario de domingos y feriados durante el día actual.
- Botón **Instalar app**, visible cuando el navegador permite instalarla (Chrome y Edge), para agregarla a la pantalla principal sin pasar por el menú.
- Usa siempre la hora de Buenos Aires y contempla los trenes que cruzan la medianoche.

## Cómo está hecho

Sitio estático, sin backend, sin dependencias y sin paso de compilación.

| Archivo | Contenido |
| --- | --- |
| `index.html` | Toda la interfaz y la lógica (HTML, CSS y JavaScript) |
| `horarios.json` | Estaciones con coordenadas y todos los servicios |
| `sw.js` | Service worker para instalar la app y usarla sin conexión |
| `manifest.webmanifest` | Datos de instalación (nombre, colores, iconos) |
| `tools/extraer_horarios.py` | Extrae los horarios del PDF oficial hacia `horarios.json` |

La ubicación se usa solo dentro del navegador para calcular distancias. No se envía a ningún servidor.

## Formato de `horarios.json`

```json
{
  "meta": { "horario_numero": 21, "vigente_desde": "2026-05-19" },
  "estaciones": [ { "id": 0, "nombre": "Retiro", "lat": -34.5906, "lon": -58.3761 } ],
  "servicios": {
    "lav": {
      "ida":    [ { "tren": "3001", "desde": 0, "horarios": ["00:20", "00:26"] } ],
      "vuelta": [ ]
    }
  }
}
```

- Tipos de día: `lav` (lunes a viernes), `sab` (sábados), `dyf` (domingos y feriados).
- Sentidos: `ida` (hacia Villa Rosa) y `vuelta` (hacia Retiro).
- `desde` es la posición de la primera parada del tren en el orden de marcha del sentido. En `ida` coincide con el `id` de la estación; en `vuelta` es `22 - id`.
- `horarios` son las horas de las paradas consecutivas a partir de esa posición.

## Probarlo en tu máquina

```bash
python3 -m http.server 8000
# abrir http://localhost:8000
```

La geolocalización del navegador solo funciona en `localhost` o bajo HTTPS.

## Actualizar los horarios

Cuando Ferrovías publica un horario nuevo:

```bash
pip install pdfplumber
python tools/extraer_horarios.py ruta/al/horario.pdf
```

Después hay que actualizar `meta.horario_numero` y `meta.vigente_desde` en `horarios.json`, y cambiar `VERSION` en `sw.js` para renovar la caché de quienes ya instalaron la app.

## Cómo colaborar

Las coordenadas de las estaciones son **aproximadas** (las marcadas con `"coordenadas_aproximadas": true`). Una corrección contra OpenStreetMap o Google Maps es la mejor contribución posible en este momento: alcanza con editar `lat` y `lon` en `horarios.json` y abrir un pull request.

## Licencia

Código bajo licencia [MIT](LICENSE). Los horarios son información pública del servicio operado por Ferrovías; este proyecto no tiene relación con la empresa.
