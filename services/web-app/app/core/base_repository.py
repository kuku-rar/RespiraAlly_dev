# services/web-app/app/core/base_repository.py
"""
基礎儲存庫類別，提供通用的資料庫操作方法
所有儲存庫都應該繼承此類別
"""
from typing import Type, TypeVar, Generic, Optional, List, Dict, Any
from sqlalchemy import select, desc, asc
from sqlalchemy.orm import Query
from ..extensions import db
from ..models import db as database

T = TypeVar('T')  # 泛型類型變數，代表模型類型


class BaseRepository(Generic[T]):
    """
    基礎儲存庫類別，提供 CRUD 操作的標準實作
    
    使用範例:
        class UserRepository(BaseRepository[User]):
            def __init__(self):
                super().__init__(User)
    """
    
    def __init__(self, model: Type[T]):
        """
        初始化儲存庫
        
        Args:
            model: SQLAlchemy 模型類別
        """
        self.model = model
        self.session = db.session
    
    def find_by_id(self, entity_id: Any) -> Optional[T]:
        """
        根據 ID 查詢實體
        
        Args:
            entity_id: 實體的主鍵值
            
        Returns:
            找到的實體或 None
        """
        return self.session.get(self.model, entity_id)
    
    def find_all(
        self, 
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_direction: str = 'asc',
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[T]:
        """
        查詢所有符合條件的實體
        
        Args:
            filters: 過濾條件字典 {"column": value}
            order_by: 排序欄位名稱
            order_direction: 排序方向 ('asc' 或 'desc')
            limit: 返回數量限制
            offset: 跳過的記錄數
            
        Returns:
            實體列表
        """
        query = select(self.model)
        
        # 應用過濾條件
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        
        # 應用排序
        if order_by and hasattr(self.model, order_by):
            order_column = getattr(self.model, order_by)
            if order_direction.lower() == 'desc':
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))
        
        # 應用分頁
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return self.session.scalars(query).all()
    
    def find_one(self, filters: Dict[str, Any]) -> Optional[T]:
        """
        查詢符合條件的單一實體
        
        Args:
            filters: 過濾條件字典
            
        Returns:
            找到的第一個實體或 None
        """
        query = select(self.model)
        
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        
        return self.session.scalars(query).first()
    
    def save(self, entity: T) -> T:
        """
        儲存實體（新增或更新）
        
        Args:
            entity: 要儲存的實體
            
        Returns:
            儲存後的實體
        """
        self.session.add(entity)
        return entity
    
    def save_all(self, entities: List[T]) -> List[T]:
        """
        批量儲存實體
        
        Args:
            entities: 要儲存的實體列表
            
        Returns:
            儲存後的實體列表
        """
        self.session.add_all(entities)
        return entities
    
    def delete(self, entity: T) -> bool:
        """
        刪除實體
        
        Args:
            entity: 要刪除的實體
            
        Returns:
            是否成功刪除
        """
        try:
            self.session.delete(entity)
            return True
        except Exception:
            return False
    
    def delete_by_id(self, entity_id: Any) -> bool:
        """
        根據 ID 刪除實體
        
        Args:
            entity_id: 要刪除的實體 ID
            
        Returns:
            是否成功刪除
        """
        entity = self.find_by_id(entity_id)
        if entity:
            return self.delete(entity)
        return False
    
    def commit(self) -> bool:
        """
        提交資料庫變更
        
        Returns:
            是否成功提交
        """
        try:
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            raise e
    
    def rollback(self):
        """回滾資料庫變更"""
        self.session.rollback()
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        計算符合條件的實體數量
        
        Args:
            filters: 過濾條件字典
            
        Returns:
            實體數量
        """
        query = select(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        
        return self.session.query(self.model).filter(query.whereclause).count()
    
    def exists(self, filters: Dict[str, Any]) -> bool:
        """
        檢查是否存在符合條件的實體
        
        Args:
            filters: 過濾條件字典
            
        Returns:
            是否存在
        """
        return self.find_one(filters) is not None
    
    def paginate(
        self,
        page: int = 1,
        per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_direction: str = 'asc'
    ) -> Dict[str, Any]:
        """
        分頁查詢
        
        Args:
            page: 頁碼（從 1 開始）
            per_page: 每頁數量
            filters: 過濾條件
            order_by: 排序欄位
            order_direction: 排序方向
            
        Returns:
            包含分頁資訊的字典
        """
        # 計算總數
        total = self.count(filters)
        
        # 計算分頁參數
        offset = (page - 1) * per_page
        
        # 查詢當前頁資料
        items = self.find_all(
            filters=filters,
            order_by=order_by,
            order_direction=order_direction,
            limit=per_page,
            offset=offset
        )
        
        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
