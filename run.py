from app.routes import app
from scrape_articles import source_scrapers
import threading

active_threads = []

if __name__ == '__main__':
    try:
        for scrape_function in source_scrapers:
            scraping_thread = threading.Thread(target=scrape_function)
            scraping_thread.start()
            active_threads.append(scraping_thread)

        print("Scraping all sources...\n")
        print("All scraping threads started.")

        app.run(debug=True, port=8000, use_reloader=False)

    except KeyboardInterrupt:
        pass
