from bs4 import BeautifulSoup
import lxml
from playwright.sync_api import sync_playwright
from urllib.parse import urlparse, unquote
import requests
import csv
import os, ssl


if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context



BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # carpeta /main/
CSV_FILE = os.path.join(BASE_DIR, "productos.csv")


# ===============================
# 1) Crear CSV vacío con columnas
# ===============================
def preparar_csv():
    # borrar si existe
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)

    # crear encabezados
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "titulo",
            "link",
            "foto",
            "disponible",
            "descripcion",
            "sabor",
            "precio"
        ])

    print("CSV inicializado correctamente.")


# ===============================
# 2) Añadir fila al CSV
# ===============================
def guardar_producto_csv(titulo, link, foto, disponible, descripcion, sabor, precio):
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([titulo, link, foto, disponible, descripcion, sabor, precio])


# ===============================
# Lógica de scraping original
# ===============================
def cargar():
    preparar_csv()
    extraer_elementos()


def cargar_todos_los_productos(page):
    load_more_selector = 'button[data-testid="loadMoreBtn"]'
    
    print("Iniciando carga de todos los productos...")
    
    load_more_button = page.locator(load_more_selector)
    
    while load_more_button.is_visible():
        try:
            load_more_button.scroll_into_view_if_needed()
            load_more_button.click(timeout=10000)
            page.wait_for_timeout(10000)
            print("Clic en 'Carga más' realizado, buscando más...")
        except Exception as e:
            print(f"Error o fin de la carga durante el click: {e}")
            break

    print("El botón 'Carga más' ya no es visible. Fin de la carga.")
    page.wait_for_timeout(10000)


def extraer_elementos():
    selector_producto = "div[class^='relative ProductTile_product-tile-container__']"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            print("Navegando a la página...")
            page.goto("https://natursur.herbalife.com/es-es/u/category/all-products")
            
            COOKIE_BUTTON_SELECTOR = "#onetrust-accept-btn-handler"
            try:
                print("Buscando y aceptando cookies...")
                page.click(COOKIE_BUTTON_SELECTOR, timeout=10000)
                print("Cookies aceptadas.")
                page.wait_for_timeout(500)
            except Exception:
                print("Banner de cookies no encontrado o ya cerrado.")

            page.wait_for_selector(selector_producto, timeout=30000)
            cargar_todos_los_productos(page)
            
            html = page.content()
            browser.close()

    except Exception as e:
        print(f"Error durante la ejecución de Playwright: {e}")
        return
    
    soup = BeautifulSoup(html, "lxml")
    productos = soup.find_all("div", class_="relative ProductTile_product-tile-container__cbS9U")
    print(f"Total de productos encontrados: {len(productos)}")

    for producto in productos:
        titulo = producto.find("p", attrs={"data-testid": "product-name"}).text.strip()
        link = "https://natursur.herbalife.com" + producto.a.get("href").strip()
        foto = producto.img.get("src").strip()

        disponible = producto.find("span", attrs={"data-testid": "out-of-stock-text"})
        disponible = False if disponible else True

        descripcion = producto.find("p", attrs={"data-testid": "product-size"})
        descripcion = descripcion.string.strip() if descripcion and descripcion.string else ""

        sabor = producto.find("p", attrs={"data-testid": "selected-flavour-text"})
        sabor = sabor.string.strip() if sabor else ""

        precio = producto.find("div", attrs={"data-testid":"price-with-gst"}) \
                         .find("p", class_="body-lg-bold whitespace-nowrap") \
                         .string.strip().replace("€", "").replace(",", ".")

        # Guardar en CSV
        guardar_producto_csv(
            titulo=titulo,
            link=link,
            foto=foto,
            disponible=disponible,
            descripcion=descripcion,
            sabor=sabor,
            precio=precio
        )

    print("CSV creado con todos los productos.")
    return len(productos)
