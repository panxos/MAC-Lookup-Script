import argparse
import re
import requests
import sys
import datetime
import os
from collections import Counter
from termcolor import colored
import csv

print(colored(r"""
    ____   __ __                ____  _____
   / __ \ / // /  ____   _  __ / __ \/ ___/
  / /_/ // // /_ / __ \ | |/_// / / /\__ \
 / ____//__  __// / / /_>  < / /_/ /___/ /
/_/       /_/  /_/ /_//_/|_| \____//____/

""", 'yellow'))
print("Creado por PanxOS")
print("Cualquier duda o consulta: faravena@soporteinfo.net")
print("https://github.com/panxos")
print("")
print("==============================================")
print("")

def extract_mac_addresses(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    mac_pattern = r"(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})|(?:[0-9A-Fa-f]{4}\.){2}(?:[0-9A-Fa-f]{4})"
    mac_addresses = re.findall(mac_pattern, content)
    formatted_macs = []
    for addr in mac_addresses:
        if "." in addr:
            addr = addr.replace(".", "")
        if "-" in addr:
            addr = addr.replace("-", ":")
        if len(addr) == 12:
            formatted_mac = ":".join([addr[i:i+2] for i in range(0, len(addr), 2)])
        else:
            formatted_mac = addr.upper()
        formatted_macs.append(formatted_mac)
    return formatted_macs


def get_manufacturer(mac, source):
    try:
        if source == "OUI":
            oui_data = load_oui_data(oui_file_path)
            mac_prefix = mac[:8].upper().replace(":", "-")
            manufacturer = re.search(f"{mac_prefix}(.{{1,}})", oui_data)
            if manufacturer:
                return manufacturer.group(1).strip()
        elif source == "MacVendors":
            response = requests.get(f"https://api.maclookup.app/v2/macs/{mac}")
            data = response.json()
            return data.get("company")
    except:
        pass
    return "unknown"
    
def load_oui_data(local_file_path):
    if os.path.isfile(local_file_path):
        with open(local_file_path, 'r') as f:
            oui_data = f.read()
    else:
        url = "http://standards-oui.ieee.org/oui.txt"
        response = requests.get(url)
        oui_data = response.text
        with open(local_file_path, 'w') as f:
            f.write(oui_data)
    return oui_data

# def parse_args():
#     parser = argparse.ArgumentParser(description="Busca fabricantes de direcciones MAC en un archivo")
#     parser.add_argument("input_file", nargs="?", help="Archivo de entrada con direcciones MAC")
#     group = parser.add_mutually_exclusive_group()
#     group.add_argument("-m", "--macvendors", action="store_true", help="Forzar el uso de MacVendors")
#     group.add_argument("-o", "--oui", action="store_true", help="Forzar el uso de OUI")
#     parser.add_argument("-c", "--csv", help="Exportar resultados a un archivo CSV", metavar="nombrearchivo.csv")
#     return parser.parse_args()

def parse_args():
    parser = argparse.ArgumentParser(description="Busca fabricantes de direcciones MAC en un archivo")
    parser.add_argument("input_file", nargs="?", help="Archivo de entrada con direcciones MAC")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-m", "--macvendors", action="store_true", help="Forzar el uso de MacVendors")
    group.add_argument("-o", "--oui", action="store_true", help="Forzar el uso de OUI")
    parser.add_argument("-c", "--csv", action="store", dest="csv", help="Exportar resultados a un archivo CSV", metavar="nombrearchivo.csv")
    return parser.parse_args()


args = parse_args()

oui_file_path = "oui.txt"

if not args.input_file:
    print("Uso: python mac_lookup.py <archivo_entrada> [-m|--macvendors] [-o|--oui] [-c|--cvs export_archivo.cvs] ")
    sys.exit(1)

file_path = args.input_file
mac_addresses = extract_mac_addresses(file_path)
mac_counter = Counter(mac_addresses)
source = "OUI" if args.oui else "MacVendors" if args.macvendors else "default"

if source == "OUI":
    oui_data = load_oui_data(oui_file_path)
else:
    oui_data = ""
print(colored("MAC                     | Fabricante                    | Repeticiones | Detección", 'yellow'))
print("------------------------------------------------------------------------------")

for mac, count in mac_counter.items():
    manufacturer = get_manufacturer(mac, source)
    if manufacturer is None or manufacturer == "unknown" or manufacturer == "":
        if source != "default":
            manufacturer = get_manufacturer(mac, "OUI" if source == "MacVendors" else "MacVendors")
        else:
            manufacturer = get_manufacturer(mac, "OUI")
            if manufacturer is None or manufacturer == "unknown" or manufacturer == "":
                manufacturer = get_manufacturer(mac, "MacVendors")
    if manufacturer is None or manufacturer == "unknown" or manufacturer == "":
        manufacturer = colored("Fabricante no reconocido", 'red')
    else:
        manufacturer = colored(manufacturer[:24].ljust(24), 'blue')
    detection = "OUI" if source == "OUI" else "MacVendors" if source == "MacVendors" else "Ambos"
    print(f"{colored(mac, 'green')}\t| {manufacturer}\t| {colored(str(count), 'red')}\t| {colored(detection, 'magenta' if detection == 'OUI' else ('cyan' if detection == 'MacVendors' else 'blue'))}")

oui_data = load_oui_data(oui_file_path)
# update_line = re.search(r"Updated:\s+(.+)", oui_data)
# if update_line:
#     update_date = datetime.datetime.strptime(update_line.group(1), "%Y-%m-%d %H:%M:%S (%z)")
#     print("\nÚltima actualización de OUI realizada el", update_date.strftime("%d de %B a las %H:%M"))
#     print("Desde: http://standards-oui.ieee.org/oui.txt")
# else:
#     print("\nNo se pudo obtener la fecha de la última actualización de OUI.")

unique_mac_count = len(mac_counter)
print(f"\nSe encontraron {unique_mac_count} MAC válidas únicas.")  # Agrega esta línea

def export_to_csv(filename, mac_counter, source):
    with open(filename, "w", newline="") as csvfile:
        fieldnames = ["MAC", "Fabricante", "Repeticiones", "Detección"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for mac, count in mac_counter.items():
            manufacturer = get_manufacturer(mac, source)
            if manufacturer is None or manufacturer == "unknown" or manufacturer == "":
                manufacturer = "Fabricante no reconocido"
            detection = "OUI" if source == "OUI" else "MacVendors"
            row = {
                "MAC": mac,
                "Fabricante": manufacturer,
                "Repeticiones": count,
                "Detección": detection,
            }
            writer.writerow(row)

if args.csv:
    export_to_csv(args.csv, mac_counter, source)
    print(f"\nResultados exportados a {args.csv}")