# Manual – Open LISA Server

Esta programa provee servicios para ser integrados con la SDK desde nodos clientes
[Open LISA SDK](https://github.com/aalvarezwindey/Open-LISA-SDK).

## Instalación

Para ejecutar el servidor se requieren instalar las siguientes dependencias, cada una desarrollada en un punto de este
documento

1. Python 3.9.6 for Windows
2. Librerías Python `pyvisa`, `pyvisa-py`, `pyserial`, `python-dotenv`, `pysondb`.
3. Librerías para correr tests: `pytest`, `pytest-cov`.
4. Controladores de cada instrumento provistos por el fabricante
5. Compilador de C

### 1. Python

La lógica del servidor que hace de interfaz con los instrumentos fue codificada en el lenguaje de programación Python.
Dicho lenguaje debe ser ejecutado por un intérprete de Python, y la versión necesaria (con la que se probó) es la
3.9.6, que se puede encontrar en el siguiente link:

https://www.python.org/downloads/

### 2. Librerías Python pyvisa y pyvisa-py

Estas librerías son las encargadas de enviar y recibir información a los instrumentos mediante el protocolo SCPI,
independientemente si éste esté conectado por USB, Ethernet, RS232, etc. Para más información sobre esta librería
puede ingresar al siguiente link: https://pyvisa.readthedocs.io/en/latest/

Para instalar estas librerías debe ejecutar:

`pip install pyvisa`

`pip install pyvisa-py`

### 3. Librería Python pyserial

Esta librería es requerida para la conexión serial RS232 que puede establecer una PC cliente con el servidor OpenLISA.
Para más información sobre esta librería puede ingresar al siguiente link: https://pythonhosted.org/pyserial/

Para instalar esta librería se debe ejecutar:

`pip install pyserial`

### 4. Controladores de cada instrumento provistos por el fabricante

Para la demo de este proyecto se controla un osciloscopio de la marca Tektronix. El fabricante provee un instalador
para Windows con los controladores para comunicarse via SCPI con los instrumentos de su marca (DAQ, osciloscopios,
fuentes, voltímetros, etc.). En la carpeta `controllers/tektronix` de este repositorio se encuentra el manual que indica
todos los modelos de instrumentos soportados, y un README con el link para descargar este controlador.

### 5. Compilador de C

El servidor permite integrar instrumentos para los cuales el fabricante provea drivers que sean integrables en el
lenguaje de programación C. Para ver más detalle, ver la sección "Integración con código C". Si éste es el caso,
se necesita un compilador de este lenguaje de programación para Windows.

## Ejecución

Para ejecutar el servidor en ambiente de prueba se debe correr desde la raíz del proyecto

```bash
python main.py  --env test --mode TCP --tcp_port 8080 --log-level DEBUG
```

## Registrar un nuevo instrumento

Registrar un nuevo instrumento consta de dos partes:

1. Registrar el instrumento y su dirección física.
2. Registrar el mapeo de comandos del instrumento.

Cada una se desarrollará en una sección.

### 1. Registrar el instrumento y su dirección física.

Se debe agregar una nueva entrada en el archivo de instrumentos `server/open_lisa/instrument/instruments.json`

```json
{
  "brand": "tektronix",
  "model": "tds1002b",
  "description": "Osciloscopio principal",
  "command_file": "tektronix_tds1002b_cmd.json",
  "id": "USB0::0x0699::0x0363::C107676::INSTR"
}
```

En donde:

| Campo          | Descripción                                           |
| -------------- | ----------------------------------------------------- |
| `brand`        | Marca del instrumento                                 |
| `model`        | Modelo del instrumento                                |
| `description`  | Texto libre como descripción a fines de documentación |
| `command_file` | Archivo de configuración de los comandos disponibles  |
| `id`           | Dirección física del instrumento                      |

Tras agregar un nuevo instrumento, se recomienda ejecutar el validador de este archivo, de la siguiente manera:

1. Ubicar una terminal en el directorio `open_lisa/instrument/`
2. Ejecutar `python validate_instruments.py`
3. Observar la salida del programa, hacer las correcciones indicadas.

### 2. Registrar el mapeo de comandos del instrumento.

Para agregar comandos al instrumento se debe agregar un archivo con el nombre indicado en el campo `command_file` del
archivo en `open_lisa/instrument/instruments.json`, en la carpeta
`open_lisa/instrument/specs`. Existen dos tipos de archivo, dependiendo el controlador del instrumento
elegido: si es mediante comandos SCPI o mediante librería customizada en C. A continuación se da un ejemplo de cada caso:

#### Comandos SCPI

A un instrumento que cumple con el protocolo SCPI se le pueden registrar los comandos con un archivo JSON con el siguiente formato

```json
{
  "get_is_in_acquisitions_state": {
    "command": "*OPC?",
    "type": "query",
    "description": "Ask if it's in acquisitions state"
  },
  "set_trigger_level": {
    "command": "TRIGger:MAIn:LEVel {}",
    "type": "set",
    "description": "Sets de oscilloscope edge and pulse width trigger level.",
    "params": [
      {
        "position": 1,
        "type": "float",
        "example": "1.4",
        "description": "Main trigger level, in volts."
      }
    ]
  },
  "get_waveform_data": {
    "command": "CURVE?",
    "type": "query_buffer",
    "description": "Transfers oscilloscope waveform data to and from the oscilloscope in binary or ASCII format. Each waveform that is transferred has an associated waveform preamble that contains information such as data format and scale."
  }
}
```

Donde:

- `get_is_in_acquisitions_state` es el nombre del comando o función que invocará el cliente a través de la SDK.
- `command` corresponde al comando SCPI indicado en el manual del instrumento.
- `type` indica el tipo de comando, los tipos soportados son:
  - `query`: comando de consulta que se espera que devuelva un valor de interés
  - `set`: comando para establecer un valor en el instrumento (a la SDK cliente se le envía la cantidad de bytes enviados al instrumento)
  - `query_buffer`: comando para leer del buffer de datos del instrumento (por debajo utiliza la función `read_raw` del módulo `pyvisa`)
  - `clib`: ver sección siguiente
- `description`: campo con fines documentativos para el comando
- `params`: listado opcional de parámetros que recibe el comando, la cantidad de parámetros se condice con la cantidad de _placeholders_ `{}` que tiene el campo `command`:
  - `position`: indica la posición del argumento recibido (iniciando en 1 y contando según lo enviado por el cliente de izquierda a derecha)
  - `type`: tipo de dato del parámetro. Tipos soportados son: `float`, `int`, `string`.
  - `example`: ejemplo del valor que se espera en el parámetro. Este campo tieen fines informativos para el cliente en caso de ejecutar un comando equívocamente.
  - `description`: campo con fines documentativos para el parámetro.

Tras conformar este archivo, se recomienda ejecutar un validador del mismo de la siguiente manera:

1. Ubicar una terminal en el directorio `open_lisa/instrument/specs`
2. Ejecutar `python validate_specs.py <filename>`
3. Observar la salida del programa, hacer las correcciones indicadas.

PD: El validador solo debe utilizarse para archivos de mapeo de comandos de instrumentosn que pretendan controlarse
mediante comandos SCPI, y no con librerías de C.

#### Integración con código C

Es común en la industria que determinados instrumentos no cumplan con el protocolo SCPI en cuyos casos los fabricantes proveen sus propias SDKs para integrarse con el instrumento. Las SDKs suelen estar implementadas en lenguajes de bajo nivel como C, es por esto que se pueden registrar comandos cuya función este implementada en dicho lenguaje. Por ejemplo:

```json
{
  "init_cammera": {
    "command": "init",
    "type": "clib",
    "lib_path": "/absolute-path-for-lib/lib.so",
    "description": "Provide a full description of what this command intends to do",
    "params": [
      {
        "position": 1,
        "type": "int",
        "example": "5",
        "description": "Documentation for param"
      },
      {
        "position": 2,
        "type": "float",
        "example": "5.0",
        "description": "Documentation for param"
      }
    ],
    "return": {
      "type": "int",
      "description": "Provide an explanation of return values for documentation purposes"
    }
  },
  "get_image": {
    "command": "get_image",
    "type": "clib",
    "lib_path": "/absolute-path-for-lib/lib.so",
    "description": "Provide a full description of what this command intends to do",
    "return": {
      "type": "bytes",
      "description": "Provide an explanation of return values for documentation purposes"
    }
  }
}
```

Diferencias a tener en cuenta con el formato de los comandos SCPI:

- `init_cammera` en el primer ejemplo corresponde al comando que envía el cliente a través de la Open-LISA-SDK y `command` corresponde a la función C expuesta por la librería.
- `lib_path` ruta a la librería C (`.so` para sistemas Unix o `.dll` para sistemas Windows). Se recomienda que sea la ruta absoluta.
- `return` indica el tipo de dato devuelto por la función C. Valores soportados actualmente `int`, `float` y `bytes`. Para el último caso es necesario que la función C expuesta por la librería reciba un último argumento del tipo `char *`. Esto es necesario ya que para la integración entre Python y C para el caso de este tipo de dato de retorna se utiliza un archivo binario temporal cuya ruta es indicado en este parámetro adicional y es donde debe ser escrito el resultado a retornar al client (como por ejemplo bytes correspondientes a imágenes capturadas por una cámara)

## Ejecución

Ubicado en la raíz del proyecto ejecutar:

```bash
python main.py -h
```

Para obtener la siguiente ayuda de ejecución:

```bash
usage: Optional app description [-h] --mode {SERIAL,TCP} [--rs_232_port RS_232_PORT] [--tcp_port TCP_PORT] [--rs_232_baudrate RS_232_BAUDRATE] [--rs_232_timeout RS_232_TIMEOUT]

optional arguments:
  -h, --help            show this help message and exit
  --mode {SERIAL,TCP}   SERIAL or TCP
  --rs_232_port RS_232_PORT
                        RS232 connection port, i.e. COM3
  --tcp_port TCP_PORT   TCP Listening port, i.e. 8080
  --rs_232_baudrate RS_232_BAUDRATE
                        Baudrate of RS232 connection, i.e. 19200
  --rs_232_timeout RS_232_TIMEOUT
                        Timeout in seconds for RS232 connection reads
```

Una vez ejecutado, el servidor escuchará nuevas conexiones en el puerto TCP o COM Serial indicado

### Para obtener la dirección IP del servidor:

1. Abrir una terminal en Windows:

![image](https://user-images.githubusercontent.com/12588243/132144280-377a1ae6-b36b-4608-a76c-90b416da3727.png)

2. Ejecutar el siguiente comando: `ipconfig`

3. En la salida del programa, identificar la dirección IPv4 de la interfaz de red utilizada para conectarse a la red de área local. En la MINI PC ésta interfaz posiblemente sea la de WiFi, ya que la interfaz Ethernet estaría reservada para comunicarse con algún instrumento:

![image](https://user-images.githubusercontent.com/12588243/132144404-3f07af75-7ce7-43cd-a791-673cd9072164.png)

En el caso del ejemplo esta dirección es 192.168.1.109

### Para obtener la el puerto serial COM del servidor:

1. Abrir "Administrador de dispositivos" en Windows:

![serial_1](https://user-images.githubusercontent.com/12588243/170373974-053fc59b-587c-47d4-a19d-35f0afa2a836.png)

2. Desplegar "Puertos (COM y LPT)"

![serial_2](https://user-images.githubusercontent.com/12588243/170374010-2774d99e-df08-436b-ae0c-a4d3205c426e.PNG)

En el ejemplo de la foto anterior, el puerto COM utilizado por el servidor será "COM4"
