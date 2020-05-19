from django.conf import settings
from django.db import models
from django.utils import timezone


class Store(models.Model):
    name = models.CharField('店舗', max_length=255)

    def __str__(self):
        return self.name


class Staff(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='ユーザー', on_delete=models.CASCADE)
    store = models.ForeignKey(Store, verbose_name='店舗', on_delete=models.CASCADE)
    name = models.CharField('スタッフ', max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'store'], name='unique_staff')
        ]

    def __str__(self):
        return self.name


class Schedule(models.Model):
    staff = models.ForeignKey(Staff, verbose_name='スタッフ', on_delete=models.CASCADE)
    name = models.CharField('予約者名', max_length=255)
    start = models.DateTimeField('開始時間')
    end = models.DateTimeField('終了時間')

    def __str__(self):
        return self.name
