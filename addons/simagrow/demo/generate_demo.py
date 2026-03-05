import random
import os
from datetime import date, timedelta

# Configuración
num_usuarios = 25

# Datos aleatorios
first_names = [
    "Taras", "Jordi", "Cristian", "Marcos", "Sole", "Modest", "Renan", "Javi",
    "Elena", "Marina", "Sofía", "Joan", "Lucía", "Marta", "Alejandro"
]

last_names = [
    "Gómez", "López", "Pérez", "Martínez", "Sánchez", "Romero", "Díaz",
    "Fernández", "García", "Hernández", "Navarro", "Moreno", "Álvarez",
    "Morales", "Castillo", "Ortega", "Ramírez", "Muñoz", "Ibáñez", "Molina"
]

# Letras del NIF
nif_letters = "TRWAGMYFPDXBNJZSQVHLCKE"

def generar_nif():
    numero = random.randint(10000000, 99999999)
    letra = nif_letters[numero % 23]
    return f"{numero}{letra}"

def generar_fecha_nacimiento():
    # Alumnos de entre 18 y 30 años
    today = date.today()
    start = today.replace(year=today.year - 30)
    end = today.replace(year=today.year - 18)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def limpiar(texto):
    reemplazos = {"á":"a","é":"e","í":"i","ó":"o","ú":"u","ñ":"n","ü":"u"}
    return "".join(reemplazos.get(c, c) for c in texto.lower())


# Carpeta de salida: demo/ relativa al script
demo_folder = os.path.dirname(os.path.abspath(__file__))


xml_file = os.path.join(demo_folder, "usuarios.xml")

nifs_usados = set()

with open(xml_file, "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="utf-8"?>\n')
    f.write("<odoo>\n    <data>\n\n")

    for i in range(num_usuarios):
        nombre = random.choice(first_names)
        apellido1 = random.choice(last_names)
        apellido2 = random.choice(last_names)
        apellidos = f"{apellido1} {apellido2}"

        # NIF único
        nif = generar_nif()
        while nif in nifs_usados:
            nif = generar_nif()
        nifs_usados.add(nif)

        fecha_nac = generar_fecha_nacimiento().strftime("%Y-%m-%d")
        creditos = 0

        f.write(f'        <record id="simagrow.usuario_{i+1}" model="simagrow.usuario">\n')
        f.write(f'            <field name="nif">{nif}</field>\n')
        f.write(f'            <field name="nombre">{nombre}</field>\n')
        f.write(f'            <field name="apellidos">{apellidos}</field>\n')
        f.write(f'            <field name="fecha_nacimiento">{fecha_nac}</field>\n')
        f.write(f'            <field name="creditos">{creditos}</field>\n')
        f.write(f'        </record>\n\n')

    f.write("    </data>\n</odoo>\n")

print(f"✅ Archivo usuario.xml generado en: {xml_file}")
