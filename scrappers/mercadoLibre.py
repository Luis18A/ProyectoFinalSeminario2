from scrapling.fetchers import StealthyFetcher

class MercadoLibreScraper:
    BASE_URL = "https://listado.mercadolibre.com.ar/"

    def search(self, query):
        # MercadoLibre uses hyphen separated query
        formatted_query = query.replace(' ', '-')
        url = f"{self.BASE_URL}{formatted_query}"

        # Usamos StealthyFetcher para evadir captchas y bloqueos mediante Camoufox con fingerprinting avanzado
        page = StealthyFetcher.fetch(
            url,
            headless=True,
            network_idle=True,
            wait=1500
        )

        products = []
        
        # 1. Intentamos buscar con la nueva estructura de MercadoLibre (.poly-card)
        cards = page.css(".poly-card")
        layout_type = "poly"

        # 2. Si no hay resultados, intentamos con la estructura clásica (.ui-search-layout__item o .ui-search-result__wrapper)
        if not cards:
            cards = page.css(".ui-search-layout__item") or page.css(".ui-search-result__wrapper") or page.css(".ui-search-result")
            layout_type = "classic"

        print(f"[Scraper ML] Detectados {len(cards)} productos usando layout: {layout_type}")

        for card in cards:
            try:
                title = None
                price_str = None
                currency = "$"
                link = None
                is_used = False

                if layout_type == "poly":
                    # Título
                    title = card.css(".poly-component__title::text").get() or card.css(".poly-component__title-link::text").get()
                    # Precio
                    price_str = card.css(".andes-money-amount__fraction::text").get()
                    currency = card.css(".andes-money-amount__currency-symbol::text").get() or "$"
                    # Enlace
                    link = card.css("a.poly-component__title::attr(href)").get() or card.css(".poly-component__title-link::attr(href)").get()
                    # Condición (si tiene un pill/etiqueta que dice "Usado" o similar)
                    pill = card.css(".poly-component__pill")
                    if pill:
                        pill_text = "".join(pill.css("::text").getall()).lower()
                        if "usado" in pill_text or "reacondicionado" in pill_text:
                            is_used = True
                else:
                    # Layout clásico
                    title = card.css(".ui-search-item__title::text").get() or card.css("h2.ui-search-item__title::text").get()
                    price_str = card.css(".ui-search-price__part--medium .andes-money-amount__fraction::text").get() or card.css(".andes-money-amount__fraction::text").get()
                    currency = card.css(".ui-search-price__part--medium .andes-money-amount__currency-symbol::text").get() or card.css(".andes-money-amount__currency-symbol::text").get() or "$"
                    link = card.css("a.ui-search-link::attr(href)").get() or card.css("a.ui-search-item__group__element::attr(href)").get()
                    
                    # Condición
                    condition_lbl = card.css(".ui-search-item__condition-label::text").get()
                    if condition_lbl and "usado" in condition_lbl.lower():
                        is_used = True

                if title and price_str:
                    # Limpiamos y convertimos el precio
                    clean_price = "".join(filter(str.isdigit, price_str))
                    price = int(clean_price)
                    
                    products.append({
                        "titulo": title.strip(),
                        "precio": price,
                        "moneda": "ARS" if currency == "$" else currency,
                        "link": link,
                        "condicion": "Usado" if is_used else "Nuevo",
                        "tienda": "MercadoLibre"
                    })
            except Exception:
                # Silenciosamente continuamos para no romper el scraper si falla un solo item
                continue

        return products