from datetime import datetime, date, timedelta, time
from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import generic
from django.views.generic import View, TemplateView
from app.models import Store, Staff, Schedule
from accounts.models import CustomUser
from django.contrib import messages
from django.utils.timezone import make_aware
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from app.forms import BookingForm


class StoreView(View):
    def get(self, request, *args, **kwargs):
        store_data = Store.objects.all()

        return render(request, 'app/store.html', {
            'store_data': store_data,
        })


class StaffView(View):
    def get(self, request, *args, **kwargs):
        store_data = get_object_or_404(Store, id=self.kwargs['pk'])
        staff_data = Staff.objects.filter(store=store_data)

        return render(request, 'app/staff.html', {
            'store_data': store_data,
            'staff_data': staff_data,
        })


class CalendarView(View):
    def get(self, request, *args, **kwargs):
        staff_data = get_object_or_404(Staff, id=self.kwargs['pk'])
        today = date.today()
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        if year and month and day:
            # 週初め
            start_date = date(year=year, month=month, day=day)
        else:
            start_date = today
        # 1週間
        days = [start_date + timedelta(days=day) for day in range(7)]
        start_day = days[0]
        end_day = days[-1]

        calendar = {}
        # 10時～21時
        for hour in range(10, 22):
            row = {}
            for day in days:
                row[day] = True
            calendar[hour] = row
        start_time = datetime.combine(start_day, time(hour=10, minute=0, second=0))
        end_time = datetime.combine(end_day, time(hour=21, minute=0, second=0))
        schedule_data = Schedule.objects.filter(staff=staff_data).exclude(Q(start__gt=end_time) | Q(end__lt=start_time))
        for schedule in schedule_data:
            local_time = timezone.localtime(schedule.start)
            booking_date = local_time.date()
            booking_hour = local_time.hour
            if (booking_hour in calendar) and (booking_date in calendar[booking_hour]):
                calendar[booking_hour][booking_date] = False

        return render(request, 'app/calendar.html', {
            'staff_data': staff_data,
            'calendar': calendar,
            'days': days,
            'start_day': start_day,
            'end_day': end_day,
            'before': days[0] - timedelta(days=7),
            'next': days[-1] + timedelta(days=1),
            'today': today,
        })


class BookingView(View):
    def get(self, request, *args, **kwargs):
        staff_data = get_object_or_404(Staff, id=self.kwargs['pk'])
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        hour = self.kwargs.get('hour')
        form = BookingForm(request.POST or None)

        return render(request, 'app/booking.html', {
            'staff_data': staff_data,
            'year': year,
            'month': month,
            'day': day,
            'hour': hour,
            'form': form,
        })

    def post(self, request, *args, **kwargs):

        print('aaaaaaaa')

        staff_data = get_object_or_404(Staff, id=self.kwargs['pk'])
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')
        hour = self.kwargs.get('hour')
        start_time = datetime(year=year, month=month, day=day, hour=hour)
        end_time = datetime(year=year, month=month, day=day, hour=hour + 1)
        schedule_data = Schedule.objects.filter(staff=staff_data, start=start_time)
        if schedule_data.exists():
            messages.error(self.request, '既に予約があります')
        else:
            form = BookingForm(request.POST or None)
            print('form')
            if form.is_valid():
                print('valid')
                schedule = Schedule()
                schedule.staff = staff_data
                schedule.start = start_time
                schedule.end = end_time
                schedule.first_name = form.cleaned_data['first_name']
                schedule.last_name = form.cleaned_data['last_name']
                schedule.tel = form.cleaned_data['tel']
                schedule.remarks = form.cleaned_data['remarks']
                schedule.save()
                print('redirect')
                return redirect('thanks')
        print('bad')

        return redirect('calendar', pk=staff_data.id, year=year, month=month, day=day)


class ThanksView(TemplateView):
    template_name = 'app/thanks.html'







class MyPageCalendar(CalendarView):
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
