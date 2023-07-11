from datetime import date
from django.core.management.base import BaseCommand
from professors.models import Holiday

class Command(BaseCommand):
    help = 'Populate Holiday model with Kyrgyzstan national holidays'

    def handle(self, *args, **options):
        holidays = [
            {'name': 'Новый год', 'date': date(date.today().year, 1, 1)},
            {'name': 'Рождество Христово', 'date': date(date.today().year, 1, 7)},
            {'name': 'День защитника Отечества', 'date': date(date.today().year, 2, 23)},
            {'name': 'Международный женский день', 'date': date(date.today().year, 3, 8)},
            {'name': 'Народный праздник Нооруз', 'date': date(date.today().year, 3, 21)},
            {'name': 'Праздник труда', 'date': date(date.today().year, 5, 1)},
            {'name': 'День Конституции Кыргызской Республики', 'date': date(date.today().year, 5, 5)},
            {'name': 'День Победы', 'date': date(date.today().year, 5, 9)},
            {'name': 'День независимости Кыргызской Республики', 'date': date(date.today().year, 8, 31)},
            {'name': 'День Великой Октябрьской Социалистической революции', 'date': date(date.today().year, 11, 7)},
        ]

        for holiday_data in holidays:
            holiday = Holiday.objects.create(name=holiday_data['name'], date=holiday_data['date'])
            self.stdout.write(f"Created holiday: {holiday}")

        self.stdout.write(self.style.SUCCESS('Successfully populated Holiday model with Kyrgyzstan national holidays.'))
