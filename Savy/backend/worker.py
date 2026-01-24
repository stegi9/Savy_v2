"""
Standalone Worker.
Processes background jobs (Redis or DB Fallback).
"""
import time
import structlog
import traceback
from sqlalchemy.orm import Session
from sqlalchemy import select, update

from db.database import SessionLocal
from models.job import BackgroundJob
from services.affiliate_matching_service import AffiliateMatchingService

logger = structlog.get_logger()

class Worker:
    def __init__(self):
        self.running = True
        
    def run(self):
        logger.info("worker_started")
        while self.running:
            try:
                self._process_one_job()
            except Exception as e:
                logger.error("worker_loop_error", error=str(e))
                time.sleep(5) # Backoff
            
            time.sleep(1) # Polling interval

    def _process_one_job(self):
        with SessionLocal() as db:
            # 1. Fetch pending job (Locking would be better, simplistic for MVP)
            job = db.execute(
                select(BackgroundJob)
                .where(BackgroundJob.status == "PENDING")
                .limit(1)
                .with_for_update(skip_locked=True) 
            ).scalars().first()
            
            if not job:
                return # Sleep in main loop
                
            logger.info("worker_job_found", job_id=job.id, task=job.task_name)
            
            # 2. Mark Running
            job.status = "RUNNING"
            db.commit()
            
            try:
                # 3. Execute Task
                self._execute(db, job.task_name, job.payload)
                
                # 4. Mark Complete
                job.status = "COMPLETED"
                logger.info("worker_job_completed", job_id=job.id)
                
            except Exception as e:
                job.status = "FAILED"
                job.result = str(e)
                logger.error("worker_job_failed", job_id=job.id, error=str(e))
                # traceback.print_exc()
            
            db.commit()

    def _execute(self, db: Session, task_name: str, payload: dict):
        if task_name == "match_affiliate_offers":
            user_id = payload.get("user_id")
            # For robustness, we could pass individual tx_ids, but for MVP fetching recent is fine
            # We need to find recent transactions for this user.
            
            # Re-instantiate service inside worker scope
            service = AffiliateMatchingService(db)
            
            # Fetch recent transactions (e.g. last 24h or just unflagged ones)
            # Simplification: The service needs IDs. Let's fetch IDs of transactions created recently.
            # In a real event system, we'd pass the IDs. 
            # Here: payload check. If payload has tx_ids, use them.
            
            tx_ids = payload.get("tx_ids", [])
            
            if not tx_ids:
                # Fallback: Process all recent transactions (last 1h)
                # This is a bit loose but works for MVP sync "catch-up"
                from models.transaction import Transaction
                from datetime import datetime, timedelta
                
                recent_txs = db.query(Transaction.id).filter(
                    Transaction.user_id == user_id,
                    Transaction.created_at >= datetime.utcnow() - timedelta(hours=1)
                ).all()
                tx_ids = [t[0] for t in recent_txs]
            
            if tx_ids:
                service.process_user_transactions(user_id, tx_ids)
            else:
                logger.info("worker_no_txs_to_process", user_id=user_id)
        
        else:
             logger.warning("worker_unknown_task", task=task_name)

if __name__ == "__main__":
    w = Worker()
    w.run()
