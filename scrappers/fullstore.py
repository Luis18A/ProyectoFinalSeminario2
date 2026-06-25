from scrapling.fetchers import DynamicFetcher

class FullstoreScraper:
    BASE_URL = "https://www.fullstore.com.ar/"

    def search(self, query):
        # NOTA: Fullstore utiliza la plataforma Tiendanube.
        # Las búsquedas se realizan de forma global usando el endpoint '/search/?q=query'.
        # Intentar buscar concatenando el término a las categorías individuales no es soportado
        # por la plataforma (ignora el parámetro y devuelve toda la categoría), además de ser lento.
        # Por lo tanto, usamos la búsqueda global que busca en todas las categorías de forma eficiente.
        url = f"{self.BASE_URL}search/?q={query.replace(' ', '+')}"

        page = DynamicFetcher.fetch(
            url,
            headless=True,
            network_idle=True,
            wait=4000, # Damos tiempo suficiente para cargar
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )

        products = []
        # El contenedor de cada tarjeta de producto en Tiendanube es .js-item-product
        cards = page.css(".js-item-product")

        for card in cards:
            try:
                # Extraemos el título
                title = card.css(".js-item-name::text").get()
                if not title:
                    title = card.css("a.js-item-name-link::text").get()
                if not title:
                    title = card.css(".item-name::text").get()
                
                # Extraemos el link
                link = card.css("a.js-item-link::attr(href)").get()
                if not link:
                    link = card.css("a::attr(href)").get()
                
                if link and not link.startswith("http"):
                    link = f"{self.BASE_URL.rstrip('/')}/{link.lstrip('/')}"
                
                # Extraemos el precio
                price_str = card.css(".js-price-display::text").get() or card.css(".item-price::text").get()
                
                if not price_str:
                    # Método de respaldo robusto si fallan las clases específicas
                    price_texts = [t.strip() for t in card.css("::text").getall() if t.strip()]
                    prices = []
                    for t in price_texts:
                        if "$" in t:
                            val_part = t.split(",")[0]
                            clean_price = "".join(filter(str.isdigit, val_part))
                            if clean_price:
                                val = int(clean_price)
                                if val > 0:
                                    prices.append(val)
                    price = min(prices) if prices else None
                else:
                    # Extraemos el valor numérico
                    val_part = price_str.split(",")[0]
                    clean_price = "".join(filter(str.isdigit, val_part))
                    price = int(clean_price) if clean_price else None
                
                if title and price and link:
                    products.append({
                        "titulo": title.strip(),
                        "precio": price,
                        "moneda": "ARS",
                        "link": link,
                        "condicion": "Nuevo",
                        "tienda": "Fullstore"
                    })
            except Exception:
                continue

        return products