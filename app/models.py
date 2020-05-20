from django.conf import settings
from django.db import models
from django.utils import timezone


class Store(models.Model):
    name = models.CharField('店舗', max_length=100)
    address = models.CharField('住所', max_length=100, null=True, blank=True)
    tel = models.CharField('電話番号', max_length=100, null=True, blank=True)
    description = models.TextField('説明', default="", blank=True)
    image = models.ImageField(upload_to='images', verbose_name='イメージ画像', null=True, blank=True)

    def __str__(self):
        return self.name


class Person(models.Model):
    name = models.CharField('スタッフ', max_length=50)
    description = models.TextField('説明', default="", blank=True)
    image = models.ImageField(upload_to='images', verbose_name='イメージ画像', null=True, blank=True)

    def __str__(self):
        return self.name


class Staff(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='ユーザー', on_delete=models.CASCADE)
    store = models.ForeignKey(Store, verbose_name='店舗', on_delete=models.CASCADE)
    person = models.ForeignKey(Person, verbose_name='スタッフ', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'store'], name='unique_staff')
        ]

    def __str__(self):
        return f'{self.store}：{self.person.name}'


class Schedule(models.Model):
    staff = models.ForeignKey(Staff, verbose_name='スタッフ', on_delete=models.CASCADE)
    name = models.CharField('予約者名', max_length=255)
    start = models.DateTimeField('開始時間', default=timezone.now)
    end = models.DateTimeField('終了時間', default=timezone.now)

    def __str__(self):
        start = timezone.localtime(self.start).strftime('%Y/%m/%d %H:%M')
        end = timezone.localtime(self.end).strftime('%Y/%m/%d %H:%M')
        return f'{self.name} {start} ~ {end} {self.staff}'
