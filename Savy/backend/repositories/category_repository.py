"""
Category repository for user categories operations.
"""
from typing import List, Optional, Set
from sqlalchemy.orm import Session
from models.category import UserCategory
from .base_repository import BaseRepository


# Vibrant color palette for auto-assignment
CATEGORY_COLORS = [
    "#10B981",  # Emerald Green
    "#3B82F6",  # Blue
    "#F59E0B",  # Amber
    "#EF4444",  # Red
    "#8B5CF6",  # Purple
    "#EC4899",  # Pink
    "#06B6D4",  # Cyan
    "#F97316",  # Orange
    "#14B8A6",  # Teal
    "#84CC16",  # Lime
    "#A855F7",  # Violet
    "#F43F5E",  # Rose
    "#0EA5E9",  # Sky Blue
    "#22C55E",  # Green
    "#FBBF24",  # Yellow
    "#6366F1",  # Indigo
]


class CategoryRepository(BaseRepository[UserCategory]):
    """Repository for UserCategory operations."""
    
    def __init__(self, db: Session):
        super().__init__(UserCategory, db)
    
    def get_user_categories(self, user_id: str) -> List[UserCategory]:
        """Get all categories for a user (system + custom)."""
        return self.db.query(UserCategory)\
            .filter(UserCategory.user_id == user_id)\
            .order_by(UserCategory.created_at.asc())\
            .all()
    
    def get_by_id_and_user(self, category_id: str, user_id: str) -> Optional[UserCategory]:
        """Get a category by ID and user ID (for authorization)."""
        return self.db.query(UserCategory)\
            .filter(
                UserCategory.id == category_id,
                UserCategory.user_id == user_id
            )\
            .first()
    
    def get_used_colors(self, user_id: str) -> Set[str]:
        """Get colors already used by user's categories."""
        categories = self.get_user_categories(user_id)
        return {cat.color.upper() for cat in categories if cat.color}
    
    def get_next_available_color(self, user_id: str) -> str:
        """Get the next available color from the palette."""
        used_colors = self.get_used_colors(user_id)
        
        for color in CATEGORY_COLORS:
            if color.upper() not in used_colors:
                return color
        
        # If all colors used, start from beginning (cycle through)
        category_count = len(self.get_user_categories(user_id))
        return CATEGORY_COLORS[category_count % len(CATEGORY_COLORS)]
    
    def create_user_category(self, user_id: str, name: str, icon: Optional[str] = None, 
                            color: Optional[str] = None, category_type: str = "expense",
                            budget_monthly: Optional[float] = None) -> UserCategory:
        """Create a new custom category with auto-assigned color if not provided."""
        # Auto-assign color if not provided
        final_color = color
        if not final_color:
            final_color = self.get_next_available_color(user_id)
        
        return self.create({
            "user_id": user_id,
            "name": name,
            "icon": icon or "category",
            "color": final_color,
            "category_type": category_type,
            "budget_monthly": budget_monthly,
            "is_system": False
        })
    
    def delete_user_category(self, category_id: str, user_id: str) -> bool:
        """Delete a user category (only if not system)."""
        category = self.get_by_id_and_user(category_id, user_id)
        
        if not category:
            return False
        
        if category.is_system:
            raise ValueError("Cannot delete system categories")
        
        return self.delete(category_id)
    
    def initialize_system_categories(self, user_id: str) -> List[UserCategory]:
        """Create default system categories for a new user."""
        default_categories = [
            {"name": "Alimentari", "icon": "shopping_cart", "color": "#10B981", "is_system": True},
            {"name": "Trasporti", "icon": "directions_car", "color": "#3B82F6", "is_system": True},
            {"name": "Ristoranti", "icon": "restaurant", "color": "#F59E0B", "is_system": True},
            {"name": "Bollette", "icon": "receipt", "color": "#EF4444", "is_system": True},
            {"name": "Intrattenimento", "icon": "movie", "color": "#8B5CF6", "is_system": True},
            {"name": "Shopping", "icon": "shopping_bag", "color": "#EC4899", "is_system": True},
            {"name": "Salute", "icon": "health_and_safety", "color": "#06B6D4", "is_system": True},
            {"name": "Casa", "icon": "home", "color": "#F97316", "is_system": True},
            {"name": "Altro", "icon": "category", "color": "#6B7280", "is_system": True}
        ]
        
        created_categories = []
        for cat_data in default_categories:
            cat_data["user_id"] = user_id
            created_categories.append(self.create(cat_data))
        
        return created_categories




