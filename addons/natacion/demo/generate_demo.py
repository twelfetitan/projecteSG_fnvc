import random
import os

# Configuración
num_swimmers = 1000
num_clubs = 20

# Nombres y apellidos
first_names = [
    "MARC", "JORDI", "PAU", "CARLOS", "DANIEL", "ALVARO", "DAVID", "SERGI",
    "ANDREA", "LAURA", "SARA", "MARINA", "PABLO", "IVAN", "SOLEDAD",
    "JORDI", "JOAN", "CRISTIAN", "RENAN", "TARAS"
]

last_names = [
    "GOMEZ", "LOPEZ", "PEREZ", "MARTINEZ", "SANCHEZ", "ROMERO", "DIAZ",
    "FERNANDEZ", "GARCIA", "HERNANDEZ", "NAVARRO", "MORENO", "ALVAREZ",
    "MORALES", "CASTILLO", "ORTEGA", "RAMIREZ", "MUÑOZ", "IBANEZ", "OLEFIRENKO"
]

# Nombres de clubes aleatorios
club_names = [
    "TORNADO SWIM CLUB", "OLIMPIC WAVES", "NEPTUNO TEAM", "TORPEDO AQUA",
    "TRITON SWIMMERS", "AQUA FORCE", "RAPID STREAM", "BLUE CURRENT",
    "SPLASH TEAM", "MARLIN SWIMMERS", "AQUA STARS", "WAVE RIDERS",
    "SEA HAWKS", "OCEAN FURY", "DOLPHIN SWIMMERS", "AQUATIC TITANS",
    "RIVER SHARKS", "WATER WARRIORS", "AQUA PHANTOMS", "SURGE SWIMMERS"
]

towns = [
    "Barcelona", "Madrid", "Valencia", "Sevilla", "Bilbao", "Zaragoza",
    "Málaga", "Granada", "Vigo", "Santander", "Alicante", "Córdoba",
    "Oviedo", "Pamplona", "Salamanca", "Burgos", "Toledo", "León",
    "Murcia", "Valladolid"
]

# Categorías adultas
categories = [
    {"id": "category_1", "name": "JOVEN_ADULTO", "min_age": 18, "max_age": 25},
    {"id": "category_2", "name": "ADULTO", "min_age": 26, "max_age": 35},
    {"id": "category_3", "name": "ADULTO_MADURO", "min_age": 36, "max_age": 45},
    {"id": "category_4", "name": "VETERANO", "min_age": 46, "max_age": 55},
    {"id": "category_5", "name": "SENIOR", "min_age": 56, "max_age": 65}
]

# Carpeta demo
demo_folder = os.path.dirname(os.path.abspath(__file__))

# --- Crear categories.xml ---
xml_categories_file = os.path.join(demo_folder, "categories.xml")
with open(xml_categories_file, "w", encoding="utf-8") as f:
    f.write("<odoo>\n    <data>\n\n")
    for cat in categories:
        f.write(f'        <record id="natacion.{cat["id"]}" model="natacion.category">\n')
        f.write(f'            <field name="name">{cat["name"]}</field>\n')
        f.write(f'            <field name="minimum_age">{cat["min_age"]}</field>\n')
        f.write(f'            <field name="maximum_age">{cat["max_age"]}</field>\n')
        f.write(f'        </record>\n\n')
    f.write("    </data>\n</odoo>\n")
print(f"Archivo categories.xml generado en {demo_folder}")

# --- Crear clubs.xml ---
xml_clubs_file = os.path.join(demo_folder, "clubs.xml")
with open(xml_clubs_file, "w", encoding="utf-8") as f:
    f.write("<odoo>\n    <data>\n\n")
    for i in range(num_clubs):
        f.write(f'        <record id="natacion.club_club{i+1}" model="natacion.club">\n')
        f.write(f'            <field name="name">{club_names[i]}</field>\n')
        f.write(f'            <field name="town">{towns[i]}</field>\n')
        f.write(f'        </record>\n\n')
    f.write("    </data>\n</odoo>\n")
print(f"Archivo clubs.xml generado en {demo_folder}")

# --- Crear swimmers.xml ---
xml_swimmers_file = os.path.join(demo_folder, "swimmers.xml")
with open(xml_swimmers_file, "w", encoding="utf-8") as f:
    f.write("<odoo>\n    <data>\n\n")
    for i in range(num_swimmers):
        name = f"{random.choice(first_names)} {random.choice(last_names)} {random.choice(last_names)}"
        year_birth = random.randint(1960, 2007)  # edad 18-65
        age = 2025 - year_birth

        # Asignar categoría según edad
        category_ref = ""
        for cat in categories:
            if cat["min_age"] <= age <= cat["max_age"]:
                category_ref = f"natacion.{cat['id']}"
                break

        club_id = f"natacion.club_club{random.randint(1, num_clubs)}"
        photo_file = f"natacion/demo/cares/{i+1:04}.jpg"

        f.write(f'        <record id="natacion.swimmer_swimmer_{i}" model="natacion.swimmer">\n')
        f.write(f'            <field name="name">{name}</field>\n')
        f.write(f'            <field name="year_birth">{year_birth}</field>\n')
        f.write(f'            <field name="age">{age}</field>\n')
        f.write(f'            <field name="category_id" ref="{category_ref}"/>\n')
        f.write(f'            <field name="club_id" ref="{club_id}"/>\n')
        f.write(f'            <field name="image" type="base64" file="{photo_file}"/>\n')
        f.write(f'        </record>\n\n')
    f.write("    </data>\n</odoo>\n")
print(f"Archivo swimmers.xml generado en {demo_folder}")
