from scrapling.fetchers import DynamicFetcher

class FravegaScraper:
    BASE_URL = "https://www.fravega.com/l/?keyword="

    def search(self, query):
        url = f"{self.BASE_URL}{query.replace(' ', '+')}"

        page = DynamicFetcher.fetch(
            url,
            headless=True,
            network_idle=True,
            wait=4000, # Fravega es pesado, le damos tiempo suficiente
            # ESTO ES VITAL: Sin user_agent Fravega bloquea la conexión
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )

        products = []
        # El contenedor real de cada tarjeta de producto en Fravega es a[href^="/p/"]
        cards = page.css('a[href^="/p/"]')

        for card in cards:
            try:
                # Extraemos todo el texto y lo limpiamos
                texts = [t.strip() for t in card.css("::text").getall() if t.strip()]
                
                title_parts = []
                price_str = None
                
                for t in texts:
                    if t.startswith('$'):
                        if not price_str: # Solo tomamos el primer precio (el actual)
                            price_str = t
                    elif not price_str: # Si aún no vimos precio, es parte del título
                        title_parts.append(t)
                        
                title = " ".join(title_parts)
                link = card.attrib.get("href")
                
                if link and not link.startswith("http"):
                    link = f"https://www.fravega.com{link}"
                
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
                        "tienda": "Fravega"
                    })
            except Exception:
                continue

        return products