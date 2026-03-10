"""
Category service for business logic.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from repositories.category_repository import CategoryRepository
from models.category import UserCategory
import structlog

logger = structlog.get_logger()


class CategoryService:
    """Service for category-related business logic."""
    
    def __init__(self, db: Session):
        self.repo = CategoryRepository(db)
    
    def get_all_categories(self, user_id: str, category_type: Optional[str] = None) -> List[dict]:
        """Get all categories for a user."""
        categories = self.repo.get_user_categories(user_id)
        
        if category_type:
             categories = [c for c in categories if c.category_type == category_type]
        
        return [
            {
                "id": cat.id,
                "user_id": cat.user_id,
                "name": cat.name,
                "icon": cat.icon,
                "color": cat.color,
                "category_type": cat.category_type or "expense",
                "budget_monthly": float(cat.budget_monthly) if cat.budget_monthly else None,
                "is_system": cat.is_system,
                "created_at": cat.created_at.isoformat() if cat.created_at else None,
                "updated_at": cat.updated_at.isoformat() if cat.updated_at else None
            }
            for cat in categories
        ]
    
    def create_category(self, user_id: str, name: str, icon: Optional[str] = None,
                       color: Optional[str] = None, category_type: str = "expense",
                       budget_monthly: Optional[float] = None) -> dict:
        """Create a new category."""
        logger.info("creating_category", user_id=user_id, name=name, category_type=category_type)
        
        category = self.repo.create_user_category(
            user_id=user_id,
            name=name,
            icon=icon,
            color=color,
            category_type=category_type,
            budget_monthly=budget_monthly
        )
        
        logger.info("category_created", category_id=category.id)
        
        return {
            "id": category.id,
            "user_id": category.user_id,
            "name": category.name,
            "icon": category.icon,
            "color": category.color,
            "category_type": category.category_type or "expense",
            "budget_monthly": float(category.budget_monthly) if category.budget_monthly else None,
            "is_system": category.is_system,
            "created_at": category.created_at.isoformat() if category.created_at else None,
            "updated_at": category.updated_at.isoformat() if category.updated_at else None
        }
    
    def update_category(self, category_id: str, user_id: str, 
                       name: Optional[str] = None, icon: Optional[str] = None,
                       color: Optional[str] = None, budget_monthly: Optional[float] = None) -> Optional[dict]:
        """Update an existing category."""
        logger.info("updating_category", category_id=category_id, user_id=user_id)
        
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if icon is not None:
            update_data["icon"] = icon
        if color is not None:
            # Validate color uniqueness on update
            existing_category = self.repo.get(category_id)
            if existing_category and existing_category.color != color:
                used_colors = self.repo.get_used_colors(user_id)
                if color.upper() in used_colors:
                    raise ValueError("Colore già in uso per un'altra categoria")
            update_data["color"] = color
        if budget_monthly is not None:
            update_data["budget_monthly"] = budget_monthly
        
        category = self.repo.update(category_id, update_data)
        
        if not category:
            return None
        
        # Verify ownership
        if category.user_id != user_id:
            return None
        
        return {
            "id": category.id,
            "user_id": category.user_id,
            "name": category.name,
            "icon": category.icon,
            "color": category.color,
            "category_type": category.category_type or "expense",
            "budget_monthly": float(category.budget_monthly) if category.budget_monthly else None,
            "is_system": category.is_system,
            "created_at": category.created_at.isoformat() if category.created_at else None,
            "updated_at": category.updated_at.isoformat() if category.updated_at else None
        }
    
    def delete_category(self, category_id: str, user_id: str) -> bool:
        """Delete a category."""
        logger.info("deleting_category", category_id=category_id, user_id=user_id)
        
        try:
            return self.repo.delete_user_category(category_id, user_id)
        except ValueError as e:
            logger.error("category_delete_failed", error=str(e))
            raise
    
    def initialize_defaults(self, user_id: str) -> List[dict]:
        """Initialize default system categories for a new user."""
        logger.info("initializing_default_categories", user_id=user_id)
        
        categories = self.repo.initialize_system_categories(user_id)
        
        return [
            {
                "id": cat.id,
                "user_id": cat.user_id,
                "name": cat.name,
                "icon": cat.icon,
                "color": cat.color,
                "category_type": cat.category_type or "expense",
                "budget_monthly": float(cat.budget_monthly) if cat.budget_monthly else None,
                "is_system": cat.is_system,
                "created_at": cat.created_at.isoformat() if cat.created_at else None,
                "updated_at": cat.updated_at.isoformat() if cat.updated_at else None
            }
            for cat in categories
        ]




