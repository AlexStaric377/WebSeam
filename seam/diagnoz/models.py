from django.db import models



class Complaint(models.Model):
    KeyComplaint = models.TextField('Код нездужання')
    Name = models.TextField('Нездужання')
    IdUser = models.CharField('код користувача', max_length=100, default='')

    def __str__(self):
        return self.KeyComplaint, self.Name

    class Meta:
        ordering = ['KeyComplaint']


class Feature(models.Model):
    KeyComplaint = models.TextField('Код нездужання')
    KeyFeature = models.TextField('Код характера нездужання ')
    Name = models.TextField('назва характера нездужання ')
    IdUser = models.CharField('код користувача', max_length=100, default='')

    class Meta:
        ordering = ['KeyComplaint']

    def __str__(self):
        return self.KeyComplaint, self.KeyFeature, self.Name


# --- Профіль пацієнта

class Pacient(models.Model):
    kodPacient = models.CharField("Код пацієнта", max_length=37, default='')
    kodKabinet = models.CharField("Код кабінету", max_length=37, default='')
    name = models.CharField("Ім'я", max_length=37, default='')
    surname = models.CharField("Прізвище", max_length=37, default='')
    gender = models.CharField("Стать", max_length=4, default='')
    age = models.IntegerField("Вік")
    profession = models.CharField("Професія", max_length=70, default='')
    weight = models.IntegerField("Вага")
    growth = models.IntegerField("Зріст")
    pind = models.CharField("Поштовий індекс", max_length=5, default='')
    tel = models.IntegerField("Телефон")
    email = models.EmailField("Электронна пошта (Email)", max_length=70, default='')

    class Meta:
        ordering = ['kodPacient']

    def __str__(self):
        return self.kodPacient, self.name, self.surname
