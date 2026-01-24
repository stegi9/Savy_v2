"""
Job Queue abstraction.
Allows switching between Redis/RQ and DB-based fallback.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import structlog
from sqlalchemy.orm import Session
from models.job import BackgroundJob

logger = structlog.get_logger()

class JobQueue(ABC):
    @abstractmethod
    def enqueue(self, task_name: str, payload: Dict[str, Any], queue: str = "default"):
        pass

class DbJobQueue(JobQueue):
    """
    Fallback implementation using MySQL `background_jobs` table.
    Suitable for MVP and environments without Redis.
    """
    def __init__(self, db_session: Session):
        self.db = db_session

    def enqueue(self, task_name: str, payload: Dict[str, Any], queue: str = "default"):
        """
        Inserts a job into the database.
        """
        try:
            job = BackgroundJob(
                task_name=task_name,
                payload=payload,
                queue_name=queue,
                status="PENDING"
            )
            self.db.add(job)
            self.db.commit()
            logger.info("job_enqueued_db", task=task_name, job_id=job.id)
            return job.id
        except Exception as e:
            logger.error("job_enqueue_failed", task=task_name, error=str(e))
            self.db.rollback()
            raise e

# Factory or Singleton logic can be added here if needed
# e.g. get_job_queue(settings) -> JobQueue
