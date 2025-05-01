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
