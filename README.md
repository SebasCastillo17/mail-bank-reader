# mail-bank-reader

Proyecto para extraer gastos desde correos (etiqueta "Banco") y volcarlos
en una hoja de cálculo de Google Sheets.

**Resumen**: Este proyecto conecta a una cuenta de correo (IMAP), busca
mensajes no leídos en la etiqueta "Banco", extrae montos y detalles de
compras, categoriza automáticamente y envía los registros a una hoja de
cálculo llamada `gastos` (hoja/worksheet `reporte_banco`).

**Requisitos**
- Python 3.8+
- Ver [requirements.txt](requirements.txt) para dependencias exactas.

**Instalación**
1. Crear y activar un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configurar credenciales de Google Sheets:
- Crear una cuenta de servicio en Google Cloud y descargar el JSON de claves.
- Compartir la hoja `gastos` con el correo de la cuenta de servicio.
- Guardar la ruta al JSON en la variable de entorno `JSON_PATH`.

3. Variables de entorno: crear un archivo `.env` en la raíz con al menos:

```
JSON_PATH=/ruta/a/servicio-credentials.json
MAIL=tu@correo.com
PASSWORD=tu_contraseña_o_app_password
```

Nota: Si usas Gmail, probablemente necesites un App Password y tener IMAP
habilitado en la cuenta.

**Uso**
- Ejecutar el script cargador:

```bash
python automation_spreadsheet/loader.py
```

El flujo es:
- `automation_spreadsheet/mail_reader.py` -> conecta al IMAP, busca correos
	no leídos en la etiqueta "Banco", extrae monto, detalle y fecha, y devuelve
	un `DataFrame` con las filas encontradas.
- `automation_spreadsheet/loader.py` -> llama a la función anterior, y si hay
	datos, se conecta a Google Sheets y agrega las filas en la hoja
	`reporte_banco`, aplicando formato básico.

**Descripción de archivos**
- [automation_spreadsheet/mail_reader.py](automation_spreadsheet/mail_reader.py):
	Lógica para conectarse al servidor IMAP (imap.gmail.com), parsear los
	mensajes y mapear a columnas: `Categoría`, `Subcategoría`, `Detalle`,
	`Pago`, `Fecha`.
- [automation_spreadsheet/loader.py](automation_spreadsheet/loader.py):
	Orquestador que carga variables de entorno, obtiene el `DataFrame` desde
	`mail_reader`, y lo sube a Google Sheets usando `gspread`.
- [requirements.txt](requirements.txt): dependencias usadas por el proyecto.

**Detalles y consideraciones**
- El extractor busca el patrón `TOTAL: CRC <monto>` en el cuerpo del correo.
	Si el patrón no aparece, el correo se ignora.
- La categorización es por reglas simples de coincidencia de texto dentro del
	cuerpo. Puedes ampliar `mail_reader.py` para añadir más reglas o integrar
	un mapeo externo.
- Los registros marcados como procesados se marcan como leídos (`\Seen`).

**Mejoras posibles**
- Soportar búsqueda por rangos de fechas y mensajes ya leídos.
- Extraer la fecha real del correo en lugar de usar `datetime.now()`.
- Añadir pruebas unitarias y manejo de errores más robusto (reintentos,
	fallos de red, validación de esquemas).

Si quieres, puedo: generar un ejemplo de `.env`, añadir un script de inicio
en `Makefile` o ampliar la documentación con ejemplos concretos de correos
soportados.