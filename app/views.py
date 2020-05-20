from datetime import datetime, date, timedelta, time
from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import generic
from .models import Store, Staff, Schedule
from django.contrib import messages
from django.utils.timezone import make_aware
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST


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

        start_time = datetime.combine(start_day, time(hour=9, minute=0, second=0))
        end_time = datetime.combine(end_day, time(hour=17, minute=0, second=0))
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


class MyPageCalendar(StaffCalendar):
    template_name = 'app/mycalendar.html'


class MyPageDayDetail(generic.TemplateView):
    template_name = 'app/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        staff = get_object_or_404(Staff, pk=pk)
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        base_date = date(year=year, month=month, day=day)

        calendar = {}
        for hour in range(9, 18):
            calendar[hour] = []

        start_time = datetime.combine(base_date, time(hour=9, minute=0, second=0))
        end_time = datetime.combine(base_date, time(hour=17, minute=0, second=0))
        schedule_data = Schedule.objects.filter(staff=staff).exclude(Q(start__gt=end_time) | Q(end__lt=start_time))
        for schedule in schedule_data:
            local_dt = timezone.localtime(schedule.start)
            booking_date = local_dt.date()
            booking_hour = local_dt.hour
            if booking_hour in calendar:
                calendar[booking_hour].append(schedule)

        context['calendar'] = calendar
        context['staff'] = staff
        return context


class MyPageSchedule(generic.UpdateView):
    model = Schedule
    fields = ('start', 'end', 'name')
    success_url = reverse_lazy('profile')
    template_name = 'app/schedule.html' 


class MyPageScheduleDelete(generic.DeleteView):
    model = Schedule
    success_url = reverse_lazy('profile')


@require_POST
def my_page_holiday_add(request, pk, year, month, day, hour):
    staff = get_object_or_404(Staff, pk=pk)
    if staff.user == request.user or request.user.is_superuser:
        start = datetime(year=year, month=month, day=day, hour=hour)
        end = datetime(year=year, month=month, day=day, hour=hour + 1)
        Schedule.objects.create(staff=staff, start=start, end=end, name='休暇')
        return redirect('my_page_day_detail', pk=pk, year=year, month=month, day=day)

    raise PermissionDenied
