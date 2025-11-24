import csv
import os
import requests
from django.core.files.base import ContentFile
from django.conf import settings
from main.products.models import Product

#python manage.py shell -c "from main.import_csv import cargar; print(cargar())"

# Ruta del CSV donde lo guardaste
CSV_PATH = os.path.join(settings.BASE_DIR, "main", "productos.csv")


def importar_productos_desde_csv():

    print("Borrando tabla de productos...")
    Product.objects.all().delete()

    print(f"Leyendo CSV desde: {CSV_PATH}")

    if not os.path.exists(CSV_PATH):
        print("ERROR: No se encuentra el archivo productos.csv")
        return

    with open(CSV_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        total = 0
        for row in reader:
            total += 1

            name = row["titulo"]
            ref = row["link"]
            foto_url = row["foto"]
            disponible = row["disponible"].lower() == "true"
            descripcion = row["descripcion"]
            sabor = row["sabor"]
            precio = float(row["precio"])

            # Crear producto (sin imagen todavía)
            p = Product(
                name=name,
                ref=ref,
                price=precio,
                flavor=sabor,
                size=descripcion,
            )

            # Descargar imagen del producto si existe
            try:
                if foto_url.startswith("http"):
                    img_resp = requests.get(foto_url, timeout=10)
                    if img_resp.status_code == 200:
                        filename = foto_url.split("/")[-1]
                        p.image.save(filename, ContentFile(img_resp.content), save=False)
            except Exception as e:
                print(f"Error descargando imagen {foto_url}: {e}")

            p.save()

        print(f"Importación finalizada. Productos añadidos: {total}")


def añadir_personalizados():
    # Añadir productos personalizados si es necesario
    # CR7 Drive de Herbalife24®,https://natursur.herbalife.com/es-es/u/products/cr7-drive-herbalife24-frutos-acai-540g-1466,https://natursur.herbalife.com/dmassets/regional-reusable-assets/emea/images/product-canister/pc-1466-es-pt.png:tile-w405h566?fmt=webp-alpha,True,540 g,Frutos Acai,24.86
    # Botella Deportiva CR7 Drive,https://natursur.herbalife.com/es-es/u/products/botella-deportiva-cr7-drive-245a,https://natursur.herbalife.com/dmassets/regional-reusable-assets/emea/images/product-canister/pc-245a-emea.png:tile-w405h566?fmt=webp-alpha,True,,,7.70
    # CR7 Drive de Herbalife24®,https://natursur.herbalife.com/es-es/u/products/cr7-drive-herbalife24-frutos-acai-10-x-27g-1467,https://natursur.herbalife.com/dmassets/regional-reusable-assets/emea/images/product-canister/pc-1467-es-pt.png:tile-w405h566?fmt=webp-alpha,True,10 x 27 g,Frutos Acai,15.00
    productos_personalizados = [
        {
            "titulo": "CR7 Drive de Herbalife24®",
            "link": "https://natursur.herbalife.com/es-es/u/products/cr7-drive-herbalife24-frutos-acai-540g-1466",
            "foto": "https://natursur.herbalife.com/dmassets/regional-reusable-assets/emea/images/product-canister/pc-1466-es-pt.png:tile-w405h566?fmt=webp-alpha",
            "disponible": "True",
            "descripcion": "540 g",
            "sabor": "Frutos Acai",
            "precio": "24.86"
        },
        {
            "titulo": "Botella Deportiva CR7 Drive",
            "link": "https://natursur.herbalife.com/es-es/u/products/botella-deportiva-cr7-drive-245a",
            "foto": "https://natursur.herbalife.com/dmassets/regional-reusable-assets/emea/images/product-canister/pc-245a-emea.png:tile-w405h566?fmt=webp-alpha",
            "disponible": "True",
            "descripcion": "",
            "sabor": "",
            "precio": "7.70"
        },
        {
            "titulo": "CR7 Drive de Herbalife24®",
            "link": "https://natursur.herbalife.com/es-es/u/products/cr7-drive-herbalife24-frutos-acai-10-x-27g-1467",
            "foto": "https://natursur.herbalife.com/dmassets/regional-reusable-assets/emea/images/product-canister/pc-1467-es-pt.png:tile-w405h566?fmt=webp-alpha",
            "disponible": "True",
            "descripcion": "10 x 27 g",
            "sabor": "Frutos Acai",
            "precio": "15.00"
        }
    ]

    print("Añadiendo productos personalizados...")


    for prod in productos_personalizados:

        # 1. Guardar en base de datos
        p = Product(
            name=prod["titulo"],
            ref=prod["link"],
            price=float(prod["precio"]),
            flavor=prod["sabor"],
            size=prod["descripcion"]
        )

        # Descargar imagen
        foto_url = prod["foto"]
        try:
            if foto_url.startswith("http"):
                img_resp = requests.get(foto_url, timeout=10)
                if img_resp.status_code == 200:
                    filename = foto_url.split("/")[-1]
                    p.image.save(filename, ContentFile(img_resp.content), save=False)
        except Exception as e:
            print(f"Error descargando imagen {foto_url}: {e}")

        p.save()
           
    print("Productos personalizados añadidos.")

def cargar():
    importar_productos_desde_csv()
    añadir_personalizados()
