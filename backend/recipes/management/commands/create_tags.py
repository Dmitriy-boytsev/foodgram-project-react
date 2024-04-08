from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Создание тегов'

    def handle(self, *args, **kwargs):
        tag_data = (
            {'name': 'Завтрак', 'color': '#FFA726', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#66BB6A', 'slug': 'lunch'},
            {'name': 'Ужин', 'color': '#5E35B1', 'slug': 'dinner'}
        )
        Tag.objects.bulk_create(Tag(**tag) for tag in tag_data)
        self.stdout.write(self.style.SUCCESS('Теги созданы!'))
