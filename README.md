# MAC Address Lookup Script

Este script de Python permite buscar fabricantes de direcciones MAC en un archivo de entrada. Utiliza tanto el registro OUI de IEEE como el API de MacVendors para encontrar información sobre los fabricantes. Es compatible con múltiples plataformas y requiere Python 3.6+ para funcionar correctamente.

## Características

- Busca direcciones MAC en un archivo de entrada
- Muestra el fabricante y la cantidad de repeticiones para cada dirección MAC
- Compatible con múltiples plataformas
- Opción para exportar los resultados a un archivo CSV
- Usa tanto el registro OUI de IEEE como el API de MacVendors

## Dependencias

- requests
- termcolor

Instala las dependencias ejecutando el siguiente comando:

pip install requests termcolor

## Uso

python mac_lookup.py <archivo_entrada> [-m|--macvendors] [-o|--oui] [-c|--csv export_archivo.csv]

Argumentos:

- `<archivo_entrada>`: Archivo de entrada con direcciones MAC
- `-m`, `--macvendors`: Forzar el uso de MacVendors
- `-o`, `--oui`: Forzar el uso de OUI
- `-c`, `--csv`: Exportar resultados a un archivo CSV

Ejemplo:

python mac_lookup.py input.txt -c results.csv

## Créditos

Creado por PanxOS
- Correo electrónico: faravena@soporteinfo.net
- GitHub: https://github.com/panxos
