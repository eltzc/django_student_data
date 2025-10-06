from django.db import models

class StudentData(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    grade = models.DecimalField(max_digits=5, decimal_places=2)
    date_received = models.DateField()
    # Вот эта строка должна быть:
    save_to = models.CharField(max_length=4, choices=[('db', 'Сохранить в базу данных'), ('file', 'Сохранить в файл')], default='db')

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.subject}"