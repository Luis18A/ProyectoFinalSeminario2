from scrapling.fetchers import DynamicFetcher

class MegatoneScraper:
    BASE_URL = "https://www.megatone.net/resultados-busqueda/"

    def search(self, query):
        url = f"{self.BASE_URL}?q={query.replace(' ', '+')}"

        page = DynamicFetcher.fetch(
            url,
            headless=True,
            network_idle=True,
            wait=4000, # Megatone es pesado, le damos tiempo suficiente
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )

        products = []
        # El contenedor real de cada tarjeta de producto en Megatone es a.producto
        cards = page.css("a.producto")

        for card in cards:
            try:
                # El título suele estar en h3 o .nombre
                title_h3 = card.css("h3::text").get()
                title_nombre = card.css(".nombre::text").get()
                title = title_h3 if title_h3 else title_nombre
                
                # Probamos todos los selectores de precio posibles que usa Megatone
                price_str = card.css(".promocional::text").get() or card.css(".precio-ahora::text").get() or card.css(".lista::text").get()
                
                # El link está en el atributo href del propio contenedor a.producto
                link = card.attrib.get("href")
                
                if link and not link.startswith("http"):
                    link = f"https://www.megatone.net{link}"
                
                if title and price_str:
                    # Limpiamos el precio dejando solo los dígitos
                    clean_price = "".join(filter(str.isdigit, price_str))
                    price = int(clean_price)
                    
                    products.append({
                        "titulo": title.strip(),
                        "precio": price,
                        "moneda": "ARS",
                        "link": link,
                        "condicion": "Nuevo",
                        "tienda": "Megatone"
                    })
            except Exception:
                continue

        return products