from reservation_service.domain.category.category import Category
class CategoryUseCase:
    def __init__(self, category_repository):
        self.category_repository = category_repository

    def create_category(self, category: Category):
        return self.category_repository.save(category)

    def get_category_by_id(self, id: int):
        return self.category_repository.find_by_id(id)

    def get_all_categories(self):
        return self.category_repository.find_all()

    def update_category(self, id: int, category: Category):
        return self.category_repository.update(id, category)
    
    def delete_category(self, id: int):
        return self.category_repository.delete(id)
        