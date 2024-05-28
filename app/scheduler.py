# scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from scrape_articles import scrape_all_sources

scheduler = BackgroundScheduler()
scheduler.add_job(func=scrape_all_sources, trigger="interval", minutes=5)
scheduler.start()

def shutdown_scheduler():
    scheduler.shutdown()
