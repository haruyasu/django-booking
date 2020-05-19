from datetime import datetime, date, timedelta, time
from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import generic
from .models import Store, Staff, Schedule
from django.contrib import messages
from django.utils.timezone import make_aware


class StoreList(generic.ListView):
    model = Store
    ordering = 'name'
    template_name = "app/store.html"

    def get(self, request, *args, **kwargs):
        # 店が1つの場合->スタッフ画面
        store_list = Store.objects.all()
        if store_list.count() == 1:
            store = store_list.first()
            return redirect('staff_list', pk=store.pk)
        return super().get(request, *args, **kwargs)


class StaffList(generic.ListView):
    model = Staff
    ordering = 'name'
    template_name = "app/staff.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['store'] = self.store
        return context

    def get_queryset(self):
        store = self.store = get_object_or_404(Store, pk=self.kwargs['pk'])
        queryset = super().get_queryset().filter(store=store)
        return queryset

    def get(self, request, *args, **kwargs):
        # スタッフが1人の場合->カレンダー画面
        store = get_object_or_404(Store, pk=self.kwargs['pk'])
        staff_list = Staff.objects.filter(store=store)
        if staff_list.count() == 1:
            staff = staff_list.first()
            return redirect('calendar', pk=staff.pk)
        return super().get(request, *args, **kwargs)


class StaffCalendar(generic.TemplateView):
    template_name = 'app/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staff = get_object_or_404(Staff, pk=self.kwargs['pk'])
        today = datetime.today()

        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        if year and month and day:
            base_date = date(year=year, month=month, day=day)
        else:
            base_date = today

        days = [base_date + timedelta(days=day) for day in range(7)]
        start_day = days[0]
        end_day = days[-1]

        calendar = {}
        for hour in range(9, 18):
            row = {}
            for day in days:
                # row[day] = []
                row[day] = True
            calendar[hour] = row

        start_time = datetime.combine(start_day, time(hour=9, minute=0))
        end_time = datetime.combine(end_day, time(hour=17, minute=0))
        schedule_data = Schedule.objects.filter(staff=staff).exclude(Q(start__gt=end_time) | Q(end__lt=start_time))

        for schedule in schedule_data:
            local_time = timezone.localtime(schedule.start)
            booking_date = local_time.date()
            booking_hour = local_time.hour
            if booking_hour in calendar and booking_date in calendar[booking_hour]:
                # calendar[booking_hour][booking_date].append(schedule)
                calendar[booking_hour][booking_date] = False

        context['staff'] = staff
        context['calendar'] = calendar
        context['days'] = days
        context['start_day'] = start_day
        context['end_day'] = end_day
        context['before'] = days[0] - timedelta(days=7)
        context['next'] = days[-1] + timedelta(days=1)
        context['today'] = today
        context['public_holidays'] = settings.PUBLIC_HOLIDAYS
        return context


class Booking(generic.CreateView):
    model = Schedule
    fields = ('name',)
    template_name = 'app/booking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['staff'] = get_object_or_404(Staff, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        staff = get_object_or_404(Staff, pk=self.kwargs['pk'])
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        hour = self.kwargs.get('hour')
        start = datetime(year=year, month=month, day=day, hour=hour)
        end = datetime(year=year, month=month, day=day, hour=hour + 1)
        if Schedule.objects.filter(staff=staff, start=start).exists():
            messages.error(self.request, 'すみません、入れ違いで予約がありました。別の日時はどうですか。')
        else:
            schedule = form.save(commit=False)
            schedule.staff = staff
            schedule.start = start
            schedule.end = end
            schedule.save()
        return redirect('calendar', pk=staff.pk, year=year, month=month, day=day)
