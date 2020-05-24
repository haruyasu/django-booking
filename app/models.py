from django.db import models
from django.utils import timezone
from accounts.models import CustomUser


class Store(models.Model):
    name = models.CharField('店舗', max_length=100)
    address = models.CharField('住所', max_length=100, null=True, blank=True)
    tel = models.CharField('電話番号', max_length=100, null=True, blank=True)
    description = models.TextField('説明', default="", blank=True)
    image = models.ImageField(upload_to='images', verbose_name='イメージ画像', null=True, blank=True)

    def __str__(self):
        return self.name


class Staff(models.Model):
    user = models.OneToOneField(CustomUser, verbose_name='スタッフ', on_delete=models.CASCADE)
    store = models.ForeignKey(Store, verbose_name='店舗', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.store}：{self.user}'


class Booking(models.Model):
    staff = models.ForeignKey(Staff, verbose_name='スタッフ', on_delete=models.CASCADE)
    first_name = models.CharField('姓', max_length=100, null=True, blank=True)
    last_name = models.CharField('名', max_length=100, null=True, blank=True)
    tel = models.CharField('電話番号', max_length=100, null=True, blank=True)
    remarks = models.TextField('備考', default="", blank=True)
    start = models.DateTimeField('開始時間', default=timezone.now)
    end = models.DateTimeField('終了時間', default=timezone.now)

    def __str__(self):
        start = timezone.localtime(self.start).strftime('%Y/%m/%d %H:%M')
        end = timezone.localtime(self.end).strftime('%Y/%m/%d %H:%M')
        return f'{self.first_name}{self.last_name} {start} ~ {end} {self.staff}'
