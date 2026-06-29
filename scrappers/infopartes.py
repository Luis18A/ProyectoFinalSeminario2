from scrapling.fetchers import DynamicFetcher

class InfoPartesScraper:
    BASE_URL = "https://infopartes.com.ar"

    def search(self, query):
        url = f"{self.BASE_URL}/search/?q={query.replace(' ', '+')}"

        page = DynamicFetcher.fetch(
            url,
            headless=True,
            network_idle=True,
            wait=4000, # Damos tiempo suficiente para cargar
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )

        products = []
        # El contenedor de cada tarjeta de producto en InfoPartes
        cards = page.css("div.js-product-container")

        for card in cards:
            try:
                # Extraemos el título
                title = card.css(".product-item-name::text").get()
                if not title:
                    title = card.css("a.product-item-link::text").get()
                
                # Extraemos el link
                link = card.css("a.product-item-link::attr(href)").get()
                if not link:
                    link = card.css("a::attr(href)").get()
                
                if link and not link.startswith("http"):
                    link = f"{self.BASE_URL}{link}"
                
                # Extraemos todos los textos dentro de la tarjeta
                price_texts = [t.strip() for t in card.css("::text").getall() if t.strip()]
                
                prices = []
                for t in price_texts:
                    if "$" in t:
                        # Descartamos los centavos (ej: $69.444,10 -> $69.444)
                        val_part = t.split(",")[0]
                        clean_price = "".join(filter(str.isdigit, val_part))
                        if clean_price:
                            val = int(clean_price)
                            if val > 0:
                                prices.append(val)
                
                if title and prices and link:
                    price = min(prices)
                    products.append({
                        "titulo": title.strip(),
                        "precio": price,
                        "moneda": "ARS",
                        "link": link,
                        "condicion": "Nuevo",
                        "tienda": "InfoPartes"
                    })
            except Exception:
                continue

        return products