# services/web-app/app/core/base_service.py
"""
基礎服務類別，提供通用的業務邏輯處理
所有服務都應該繼承此類別
"""
from typing import Type, TypeVar, Generic, Optional, List, Dict, Any
from abc import ABC, abstractmethod
import logging
from .base_repository import BaseRepository

T = TypeVar('T')  # 泛型類型變數，代表實體類型
R = TypeVar('R', bound=BaseRepository)  # 泛型類型變數，代表儲存庫類型

logger = logging.getLogger(__name__)


class BaseService(Generic[T, R], ABC):
    """
    基礎服務類別，提供業務邏輯的標準實作
    
    使用範例:
        class UserService(BaseService[User, UserRepository]):
            def __init__(self):
                super().__init__(UserRepository())
    """
    
    def __init__(self, repository: R):
        """
        初始化服務
        
        Args:
            repository: 儲存庫實例
        """
        self.repository = repository
        self.logger = logger
    
    def get_by_id(self, entity_id: Any) -> Optional[T]:
        """
        根據 ID 取得實體
        
        Args:
            entity_id: 實體 ID
            
        Returns:
            實體或 None
        """
        try:
            entity = self.repository.find_by_id(entity_id)
            if not entity:
                self.logger.warning(f"Entity with ID {entity_id} not found")
            return entity
        except Exception as e:
            self.logger.error(f"Error getting entity by ID {entity_id}: {e}")
            raise
    
    def get_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        pagination: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """
        取得所有符合條件的實體
        
        Args:
            filters: 過濾條件
            pagination: 分頁參數 {"page": 1, "per_page": 20}
            
        Returns:
            實體列表
        """
        try:
            if pagination:
                result = self.repository.paginate(
                    page=pagination.get('page', 1),
                    per_page=pagination.get('per_page', 20),
                    filters=filters,
                    order_by=pagination.get('order_by'),
                    order_direction=pagination.get('order_direction', 'asc')
                )
                return result['items']
            else:
                return self.repository.find_all(filters=filters)
        except Exception as e:
            self.logger.error(f"Error getting all entities: {e}")
            raise
    
    def create(self, data: Dict[str, Any]) -> T:
        """
        建立新實體
        
        Args:
            data: 實體資料
            
        Returns:
            建立的實體
        """
        try:
            # 驗證資料
            validation_errors = self.validate_create(data)
            if validation_errors:
                raise ValueError(f"Validation failed: {validation_errors}")
            
            # 預處理資料
            processed_data = self.preprocess_create(data)
            
            # 建立實體
            entity = self.create_entity(processed_data)
            
            # 儲存實體
            self.repository.save(entity)
            self.repository.commit()
            
            # 後處理
            self.postprocess_create(entity)
            
            self.logger.info(f"Created entity: {entity}")
            return entity
        except Exception as e:
            self.logger.error(f"Error creating entity: {e}")
            self.repository.rollback()
            raise
    
    def update(self, entity_id: Any, data: Dict[str, Any]) -> Optional[T]:
        """
        更新實體
        
        Args:
            entity_id: 實體 ID
            data: 更新資料
            
        Returns:
            更新後的實體或 None
        """
        try:
            # 取得實體
            entity = self.repository.find_by_id(entity_id)
            if not entity:
                self.logger.warning(f"Entity with ID {entity_id} not found for update")
                return None
            
            # 驗證資料
            validation_errors = self.validate_update(entity, data)
            if validation_errors:
                raise ValueError(f"Validation failed: {validation_errors}")
            
            # 預處理資料
            processed_data = self.preprocess_update(entity, data)
            
            # 更新實體
            updated_entity = self.update_entity(entity, processed_data)
            
            # 儲存變更
            self.repository.save(updated_entity)
            self.repository.commit()
            
            # 後處理
            self.postprocess_update(updated_entity)
            
            self.logger.info(f"Updated entity with ID {entity_id}")
            return updated_entity
        except Exception as e:
            self.logger.error(f"Error updating entity with ID {entity_id}: {e}")
            self.repository.rollback()
            raise
    
    def delete(self, entity_id: Any) -> bool:
        """
        刪除實體
        
        Args:
            entity_id: 實體 ID
            
        Returns:
            是否成功刪除
        """
        try:
            # 取得實體
            entity = self.repository.find_by_id(entity_id)
            if not entity:
                self.logger.warning(f"Entity with ID {entity_id} not found for deletion")
                return False
            
            # 驗證是否可以刪除
            if not self.can_delete(entity):
                self.logger.warning(f"Entity with ID {entity_id} cannot be deleted")
                return False
            
            # 前處理
            self.preprocess_delete(entity)
            
            # 刪除實體
            success = self.repository.delete(entity)
            if success:
                self.repository.commit()
                
                # 後處理
                self.postprocess_delete(entity_id)
                
                self.logger.info(f"Deleted entity with ID {entity_id}")
            
            return success
        except Exception as e:
            self.logger.error(f"Error deleting entity with ID {entity_id}: {e}")
            self.repository.rollback()
            raise
    
    def exists(self, filters: Dict[str, Any]) -> bool:
        """
        檢查是否存在符合條件的實體
        
        Args:
            filters: 過濾條件
            
        Returns:
            是否存在
        """
        return self.repository.exists(filters)
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        計算符合條件的實體數量
        
        Args:
            filters: 過濾條件
            
        Returns:
            數量
        """
        return self.repository.count(filters)
    
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
            page: 頁碼
            per_page: 每頁數量
            filters: 過濾條件
            order_by: 排序欄位
            order_direction: 排序方向
            
        Returns:
            分頁結果
        """
        return self.repository.paginate(
            page=page,
            per_page=per_page,
            filters=filters,
            order_by=order_by,
            order_direction=order_direction
        )
    
    # ========== 抽象方法，子類別必須實作 ==========
    
    @abstractmethod
    def create_entity(self, data: Dict[str, Any]) -> T:
        """
        建立實體物件
        
        Args:
            data: 實體資料
            
        Returns:
            實體物件
        """
        pass
    
    @abstractmethod
    def update_entity(self, entity: T, data: Dict[str, Any]) -> T:
        """
        更新實體物件
        
        Args:
            entity: 原實體
            data: 更新資料
            
        Returns:
            更新後的實體
        """
        pass
    
    # ========== 可選覆寫的方法 ==========
    
    def validate_create(self, data: Dict[str, Any]) -> Optional[str]:
        """
        驗證建立資料
        
        Args:
            data: 要驗證的資料
            
        Returns:
            錯誤訊息或 None
        """
        return None
    
    def validate_update(self, entity: T, data: Dict[str, Any]) -> Optional[str]:
        """
        驗證更新資料
        
        Args:
            entity: 原實體
            data: 要驗證的資料
            
        Returns:
            錯誤訊息或 None
        """
        return None
    
    def can_delete(self, entity: T) -> bool:
        """
        檢查是否可以刪除實體
        
        Args:
            entity: 要刪除的實體
            
        Returns:
            是否可以刪除
        """
        return True
    
    def preprocess_create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        建立前的資料預處理
        
        Args:
            data: 原始資料
            
        Returns:
            處理後的資料
        """
        return data
    
    def preprocess_update(self, entity: T, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新前的資料預處理
        
        Args:
            entity: 原實體
            data: 原始資料
            
        Returns:
            處理後的資料
        """
        return data
    
    def preprocess_delete(self, entity: T):
        """
        刪除前的處理
        
        Args:
            entity: 要刪除的實體
        """
        pass
    
    def postprocess_create(self, entity: T):
        """
        建立後的處理
        
        Args:
            entity: 建立的實體
        """
        pass
    
    def postprocess_update(self, entity: T):
        """
        更新後的處理
        
        Args:
            entity: 更新的實體
        """
        pass
    
    def postprocess_delete(self, entity_id: Any):
        """
        刪除後的處理
        
        Args:
            entity_id: 刪除的實體 ID
        """
        pass
