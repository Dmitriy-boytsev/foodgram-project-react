from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Дает доступ к объекту только автору.
    Чтение доступно всем пользователям.

    Реализация:
    Этот разрешительный класс расширяет IsAuthenticatedOrReadOnly,
    чтобы дать доступ к объекту только его автору.
    """

    def has_object_permission(self, request, view, obj):
        """
        Проверяет разрешение на доступ к объекту.

        Разрешение предоставляется если:
        - Метод запроса является безопасным (GET, HEAD, OPTIONS).
        - Пользователь запроса является автором объекта.

        Args:
            request: Запрос, который пытается получить доступ к объекту.
            view: Представление, в котором происходит попытка доступа.
            obj: Объект, к которому пытается получить доступ пользователь.

        Returns:
            bool: True, если доступ разрешен, False в противном случае.
        """
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)
