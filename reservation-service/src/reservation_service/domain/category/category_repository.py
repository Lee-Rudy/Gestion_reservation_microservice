from abc import ABC, abstractmethod
from reservation_service.domain.category.category import Category

class CategoryRepository(ABC):

    @abstractmethod
    def save(self, category: Category):
        pass

    @abstractmethod
    def find_by_id(self, id: int):
        pass

    @abstractmethod
    def find_all(self):
        pass

    @abstractmethod
    def update(self, id: int, category: Category):
        pass

    @abstractmethod
    def delete(self, id: int):
        pass