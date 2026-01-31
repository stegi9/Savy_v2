"""
Celery worker for asynchronous background tasks.
"""
from celery import Celery
from celery.schedules import crontab
from config import settings
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

# Create Celery app
celery_app = Celery(
    "savy",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Rome',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Celery Beat Schedule (Scheduled Tasks)
celery_app.conf.beat_schedule = {
    'send-bill-reminders-daily': {
        'task': 'backend.celery_tasks.send_bill_reminders',
        'schedule': crontab(hour=9, minute=0),  # Every day at 9:00 AM
    },
    'cleanup-expired-tokens': {
        'task': 'backend.celery_tasks.cleanup_expired_tokens',
        'schedule': crontab(hour=2, minute=0),  # Every day at 2:00 AM
    },
}


# ============================================================================
# CELERY TASKS
# ============================================================================

@celery_app.task(name="backend.celery_tasks.send_verification_email")
def send_verification_email(user_email: str, full_name: str, token: str):
    """
    Send email verification link to user.
    
    Args:
        user_email: User's email address
        full_name: User's full name
        token: Verification token
    """
    from services.email_service import get_email_service
    
    logger.info("task_send_verification_email_started", email=user_email)
    
    try:
        email_service = get_email_service()
        success = email_service.send_verification_email(user_email, full_name, token)
        
        if success:
            logger.info("task_send_verification_email_success", email=user_email)
        else:
            logger.error("task_send_verification_email_failed", email=user_email)
            
        return {"success": success, "email": user_email}
    
    except Exception as e:
        logger.error("task_send_verification_email_error", email=user_email, error=str(e))
        raise


@celery_app.task(name="backend.celery_tasks.send_password_reset_email")
def send_password_reset_email(user_email: str, full_name: str, token: str):
    """
    Send password reset link to user.
    
    Args:
        user_email: User's email address
        full_name: User's full name
        token: Password reset token
    """
    from services.email_service import get_email_service
    
    logger.info("task_send_password_reset_email_started", email=user_email)
    
    try:
        email_service = get_email_service()
        success = email_service.send_password_reset_email(user_email, full_name, token)
        
        if success:
            logger.info("task_send_password_reset_email_success", email=user_email)
        else:
            logger.error("task_send_password_reset_email_failed", email=user_email)
            
        return {"success": success, "email": user_email}
    
    except Exception as e:
        logger.error("task_send_password_reset_email_error", email=user_email, error=str(e))
        raise


@celery_app.task(name="backend.celery_tasks.send_bill_reminders")
def send_bill_reminders():
    """
    Send reminders for upcoming bills (runs daily at 9:00 AM).
    Finds bills due in the next 3 days and sends email reminders.
    """
    from db.database import SessionLocal
    from models.recurring_bill import RecurringBill
    from models.user import User
    from services.email_service import get_email_service
    from sqlalchemy import and_
    
    logger.info("task_send_bill_reminders_started")
    
    db = SessionLocal()
    email_service = get_email_service()
    
    try:
        # Find bills due in the next 3 days
        today = datetime.now().date()
        three_days_later = today + timedelta(days=3)
        
        bills = db.query(RecurringBill).filter(
            and_(
                RecurringBill.next_due_date >= today,
                RecurringBill.next_due_date <= three_days_later,
                RecurringBill.is_active == True
            )
        ).all()
        
        sent_count = 0
        
        for bill in bills:
            user = db.query(User).filter(User.id == bill.user_id).first()
            if user and user.budget_notifications:
                success = email_service.send_bill_reminder_email(
                    to=user.email,
                    full_name=user.full_name,
                    bill_name=bill.name,
                    amount=float(bill.amount),
                    due_date=bill.next_due_date.strftime("%d/%m/%Y")
                )
                if success:
                    sent_count += 1
        
        logger.info("task_send_bill_reminders_completed", sent=sent_count, total=len(bills))
        return {"sent": sent_count, "total": len(bills)}
    
    except Exception as e:
        logger.error("task_send_bill_reminders_error", error=str(e))
        raise
    
    finally:
        db.close()


@celery_app.task(name="backend.celery_tasks.cleanup_expired_tokens")
def cleanup_expired_tokens():
    """
    Clean up expired verification and reset tokens (runs daily at 2:00 AM).
    """
    from db.database import SessionLocal
    from models.user import User
    
    logger.info("task_cleanup_expired_tokens_started")
    
    db = SessionLocal()
    
    try:
        now = datetime.utcnow()
        
        # Clean expired email verification tokens
        result = db.query(User).filter(
            and_(
                User.email_verification_token.isnot(None),
                User.email_verification_expires < now
            )
        ).update({
            "email_verification_token": None,
            "email_verification_expires": None
        })
        
        db.commit()
        
        logger.info("task_cleanup_expired_tokens_verification", cleaned=result)
        
        # Clean expired password reset tokens
        result = db.query(User).filter(
            and_(
                User.password_reset_token.isnot(None),
                User.password_reset_expires < now
            )
        ).update({
            "password_reset_token": None,
            "password_reset_expires": None
        })
        
        db.commit()
        
        logger.info("task_cleanup_expired_tokens_password_reset", cleaned=result)
        
        return {"success": True}
    
    except Exception as e:
        logger.error("task_cleanup_expired_tokens_error", error=str(e))
        db.rollback()
        raise
    
    finally:
        db.close()


@celery_app.task(name="backend.celery_tasks.process_affiliate_matching")
def process_affiliate_matching(user_id: str, transaction_ids: list[str]):
    """
    Process affiliate matching for new transactions (asynchronous).
    
    Args:
        user_id: User UUID
        transaction_ids: List of transaction IDs to process
    """
    from db.database import SessionLocal
    from services.affiliate_matching_service import AffiliateMatchingService
    
    logger.info("task_process_affiliate_matching_started", user_id=user_id, tx_count=len(transaction_ids))
    
    db = SessionLocal()
    
    try:
        service = AffiliateMatchingService(db)
        service.process_user_transactions(user_id, transaction_ids)
        
        logger.info("task_process_affiliate_matching_completed", user_id=user_id)
        return {"success": True, "processed": len(transaction_ids)}
    
    except Exception as e:
        logger.error("task_process_affiliate_matching_error", user_id=user_id, error=str(e))
        raise
    
    finally:
        db.close()


@celery_app.task(name="backend.celery_tasks.send_push_notification")
def send_push_notification(user_id: str, title: str, body: str, data: dict = None):
    """
    Send push notification to user via Firebase FCM.
    
    Args:
        user_id: User UUID
        title: Notification title
        body: Notification body
        data: Additional data payload
    """
    from db.database import SessionLocal
    from models.user import User
    
    logger.info("task_send_push_notification_started", user_id=user_id)
    
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.fcm_token:
            logger.warning("task_send_push_notification_no_token", user_id=user_id)
            return {"success": False, "reason": "no_fcm_token"}
        
        # Firebase FCM integration
        # TODO: Implement Firebase Admin SDK push notification
        # For now, just log
        logger.info(
            "task_send_push_notification_mock",
            user_id=user_id,
            title=title,
            body=body,
            fcm_token=user.fcm_token[:20] + "..."
        )
        
        return {"success": True, "user_id": user_id}
    
    except Exception as e:
        logger.error("task_send_push_notification_error", user_id=user_id, error=str(e))
        raise
    
    finally:
        db.close()


# ============================================================================
# HELPER TO TRIGGER TASKS FROM API
# ============================================================================

def trigger_send_verification_email(user_email: str, full_name: str, token: str):
    """Helper to trigger verification email task."""
    send_verification_email.delay(user_email, full_name, token)


def trigger_send_password_reset_email(user_email: str, full_name: str, token: str):
    """Helper to trigger password reset email task."""
    send_password_reset_email.delay(user_email, full_name, token)


def trigger_affiliate_matching(user_id: str, transaction_ids: list[str]):
    """Helper to trigger affiliate matching task."""
    process_affiliate_matching.delay(user_id, transaction_ids)


def trigger_push_notification(user_id: str, title: str, body: str, data: dict = None):
    """Helper to trigger push notification task."""
    send_push_notification.delay(user_id, title, body, data or {})
