import mysql.connector
from reservation_service.infrastructure.database.database import get_connection
from reservation_service.domain.category.category_repository import CategoryRepository
from reservation_service.domain.category.category import Category

class CategoryRepositoryImpl(CategoryRepository):

    def save(self, category: Category):
        conn = get_connection()
        cursor = conn.cursor()

        if category.id is None:
            query = """
            INSERT INTO categories (name, description)
            VALUES (%s, %s)
            """
            cursor.execute(query, (category.name, category.description))
            conn.commit()
            category.id = cursor.lastrowid

        cursor.close()
        conn.close()
        return category

    def find_by_id(self, id: int):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM categories WHERE id=%s", (id,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if not result:
            return None

        category = Category(result["name"], result["description"])
        category.id = result["id"]
        return category

    def find_all(self):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM categories")
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return [
            Category(r["name"], r["description"], r["id"]) for r in results
        ]

    def update(self, id: int, category: Category):
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        UPDATE categories
        SET name=%s, description=%s
        WHERE id=%s
        """
        cursor.execute(query, (category.name, category.description, id))
        conn.commit()

        cursor.close()
        conn.close()

        return self.find_by_id(id)

    def delete(self, id: int):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM categories WHERE id=%s", (id,))
        conn.commit()
       
        deleted = cursor.rowcount > 0 
        
        cursor.close()
        conn.close()
        
        return deleted  