"""
Base repository with generic CRUD operations.
"""
from typing import TypeVar, Generic, Type, Optional, List, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.database import Base
from utils.exceptions import DatabaseException
import structlog

logger = structlog.get_logger()

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository providing generic CRUD operations with transaction management.
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get_by_id(self, id: str) -> Optional[ModelType]:
        """Get a single record by ID."""
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error("get_by_id_failed", model=self.model.__name__, id=id, error=str(e))
            raise DatabaseException(str(e))
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination."""
        try:
            return self.db.query(self.model).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error("get_all_failed", model=self.model.__name__, error=str(e))
            raise DatabaseException(str(e))
    
    def create(self, obj_in: dict) -> ModelType:
        """Create a new record with automatic rollback on error."""
        try:
            db_obj = self.model(**obj_in)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("create_failed", model=self.model.__name__, error=str(e))
            raise DatabaseException(str(e))
    
    def update(self, id: str, obj_in: dict) -> Optional[ModelType]:
        """Update an existing record with automatic rollback on error."""
        try:
            db_obj = self.get_by_id(id)
            if not db_obj:
                return None
            
            for field, value in obj_in.items():
                if hasattr(db_obj, field) and value is not None:
                    setattr(db_obj, field, value)
            
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("update_failed", model=self.model.__name__, id=id, error=str(e))
            raise DatabaseException(str(e))
    
    def delete(self, id: str) -> bool:
        """Delete a record with automatic rollback on error."""
        try:
            db_obj = self.get_by_id(id)
            if not db_obj:
                return False
            
            self.db.delete(db_obj)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error("delete_failed", model=self.model.__name__, id=id, error=str(e))
            raise DatabaseException(str(e))
    
    def filter_by(self, **kwargs: Any) -> List[ModelType]:
        """Filter records by arbitrary fields."""
        try:
            query = self.db.query(self.model)
            for key, value in kwargs.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
            return query.all()
        except SQLAlchemyError as e:
            logger.error("filter_by_failed", model=self.model.__name__, error=str(e))
            raise DatabaseException(str(e))

