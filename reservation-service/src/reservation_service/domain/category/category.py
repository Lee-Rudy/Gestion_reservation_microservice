class Category:
    def __init__(self, name: str, description: str, id: int = None):
        self._id = id
        self._validate_name(name)
        self._validate_description(description)

        self.id = id
        self.name = name.strip()
        self.description = description.strip() if description else ""

    def _validate_name(self, name: str):
        if not name or not name.strip():
            raise ValueError("Le nom de la catégorie est requis")

        if len(name.strip()) < 3:
            raise ValueError("Le nom de la catégorie doit contenir au moins 3 caractères")

        if len(name.strip()) > 100:
            raise ValueError("Le nom de la catégorie doit contenir moins de 100 caractères")

    def _validate_description(self, description: str):
        if description and len(description.strip()) > 100:
            raise ValueError("La description doit contenir moins de 100 caractères")