from celery.task.schedules import crontab
from celery.decorators import periodic_task
from scraper.source.schiphol_source import retrieve_schiphol_flights
from celery.utils.log import get_task_logger
from datetime import datetime

logger = get_task_logger(__name__)

# A periodic task that will run every minute (the symbol "*" means every)
@periodic_task(run_every=(crontab(hour="*", minute="*/5", day_of_week="*")))
def retrieve_flights():
    logger.info("Start task")
    retrieve_schiphol_flights('arrivals')
    retrieve_schiphol_flights('departures')
    logger.info('Task finished: Flights retrieved')
