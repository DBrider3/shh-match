import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from zoneinfo import ZoneInfo

from app.services.recommendation_service import build_weekly_recommendations

logger = structlog.get_logger()

scheduler: AsyncIOScheduler = None


def init_scheduler():
    """Initialize the scheduler"""
    global scheduler

    scheduler = AsyncIOScheduler(timezone=ZoneInfo("Asia/Seoul"))

    # Add weekly recommendation job - run every Monday at 10:00 AM KST
    scheduler.add_job(
        run_weekly_recommendations,
        trigger=CronTrigger(
            day_of_week='mon',
            hour=10,
            minute=0,
            timezone=ZoneInfo("Asia/Seoul")
        ),
        id='weekly-recommendations',
        name='Weekly Recommendations Generation',
        replace_existing=True
    )

    logger.info("Scheduler initialized with weekly recommendation job")
    return scheduler


def start_scheduler():
    """Start the scheduler"""
    global scheduler
    if scheduler and not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")


def shutdown_scheduler():
    """Shutdown the scheduler"""
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shutdown")


def run_weekly_recommendations():
    """Job function to run weekly recommendations"""
    try:
        # Generate current week label
        now = datetime.now(tz=ZoneInfo("Asia/Seoul"))
        year, week, _ = now.isocalendar()
        week_label = f"{year}-W{week:02d}"

        logger.info(f"Starting weekly recommendation generation", week=week_label)

        result = build_weekly_recommendations(week_label)

        logger.info(
            f"Weekly recommendation generation completed",
            week=week_label,
            result=result
        )

    except Exception as e:
        logger.error(f"Failed to run weekly recommendations: {str(e)}", exc_info=True)