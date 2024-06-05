import datetime
from app.routes import app
from scrape_articles import source_scrapers
import threading
import sched
import time

active_threads = []

def start_scraping_threads():
    global active_threads

    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"Starting scraping at {current_time}")

    for scrape_function in source_scrapers:
        scraping_thread = threading.Thread(target=scrape_function)
        scraping_thread.start()
        active_threads.append(scraping_thread)

    print("Scraping all sources...\n")
    print("All scraping threads started.")

def schedule_scraping(scheduler, interval=300):
    # Start scraping threads
    start_scraping_threads()

    # Schedule the next scraping task
    scheduler.enter(interval, 1, schedule_scraping, (scheduler, interval))

if __name__ == '__main__':
    try:
        # Create a scheduler
        scheduler = sched.scheduler(time.time, time.sleep)

        # Schedule the first scraping to run immediately and then every 5 minutes
        scheduler.enter(0, 1, schedule_scraping, (scheduler, 300))

        # Run the scheduler in a separate thread to avoid blocking the main thread
        scheduler_thread = threading.Thread(target=scheduler.run)
        scheduler_thread.start()

        # Start the web application
        app.run(debug=True, port=8000, use_reloader=False)

    except KeyboardInterrupt:
        pass
