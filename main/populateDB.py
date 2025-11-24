from bs4 import BeautifulSoup
import lxml
from main.products.models import Product
from playwright.sync_api import sync_playwright
from django.core.files.base import ContentFile
from urllib.parse import urlparse, unquote
#import requests

import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


def cargar():
    Product.objects.all().delete()
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
                # Intentamos hacer click. Si falla (por timeout), el banner no estaba.
                page.click(COOKIE_BUTTON_SELECTOR, timeout=10000) 
                print("Cookies aceptadas.")
                page.wait_for_timeout(500)
            except Exception:
                print("Banner de cookies no encontrado o ya cerrado, continuando...")

            page.wait_for_selector(selector_producto, timeout=30000)
            
            cargar_todos_los_productos(page)
            
            f = page.content()
            browser.close()
    except Exception as e:
        print(f"Error durante la ejecución de Playwright: {e}")
        return
    s = BeautifulSoup(f, "lxml")
    productos = s.find_all("div", class_="relative ProductTile_product-tile-container__cbS9U")
    print(f"Total de productos encontrados: {len(productos)}")
    int=0
    for producto in productos:
        int+=1
        titulo = producto.find("p", attrs={"data-testid": "product-name"}).text.strip()
        link = "https://natursur.herbalife.com" + producto.a.get("href").strip()
        foto = producto.img.get("src").strip()
        disponible = producto.find("span", attrs={"data-testid": "out-of-stock-text"})
        if disponible:
            disponible = False
        else:
            disponible = True
        descripcion = producto.find("p", attrs={"data-testid": "product-size"})
        if descripcion:
            descripcion = descripcion.string
            if descripcion:
                descripcion = descripcion.strip()
            else :
                descripcion = ""
        else:
            descripcion = ""
        
        sabor = producto.find("p", attrs={"data-testid": "selected-flavour-text"})
        if sabor:
            sabor = sabor.string.strip()
        else:
            sabor = ""
        precio = producto.find("div", attrs={"data-testid":"price-with-gst"}).find("p",class_="body-lg-bold whitespace-nowrap").string.strip().replace("€","").replace(",",".")
        # Crear instancia sin guardar aún la imagen en ImageField
        p = Product(
            name=titulo,
            ref=link,
            price=float(precio),
            flavor=sabor,
            size=descripcion,
        )

        # Intentar descargar la imagen externa y guardarla en el ImageField
        try:
            if foto and foto.lower().startswith(('http://', 'https://')):
                resp = requests.get(foto, timeout=15)
                if resp.status_code == 200 and resp.content:
                    # construir nombre de archivo a partir de la URL
                    parsed = urlparse(foto)
                    fname = unquote(parsed.path.split('/')[-1])
                    if not fname:
                        fname = f"product_{int}.png"
                    # ContentFile para guardar en ImageField
                    p.image.save(fname, ContentFile(resp.content), save=False)
                else:
                    print(f"No se pudo descargar imagen (status {resp.status_code}) para: {foto}")
        except Exception as e:
            print(f"Error al descargar la imagen {foto}: {e}")

        p.save()
    return Product.objects.all().count()