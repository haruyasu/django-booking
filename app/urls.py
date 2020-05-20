from django.urls import path
from app import views

urlpatterns = [
    path('', views.StoreView.as_view(), name='store'),
    path('store/<int:pk>/', views.StaffView.as_view(), name='staff'),

    path('staff/<int:pk>/calendar/', views.StaffCalendar.as_view(), name='calendar'),
    path('staff/<int:pk>/calendar/<int:year>/<int:month>/<int:day>/', views.StaffCalendar.as_view(), name='calendar'),

    path('staff/<int:pk>/booking/<int:year>/<int:month>/<int:day>/<int:hour>/', views.Booking.as_view(), name='booking'),

    path('mypage/<int:pk>/calendar/', views.MyPageCalendar.as_view(), name='my_page_calendar'),
    path('mypage/<int:pk>/calendar/<int:year>/<int:month>/<int:day>/', views.MyPageCalendar.as_view(), name='my_page_calendar'),

    path('mypage/<int:pk>/config/<int:year>/<int:month>/<int:day>/', views.MyPageDayDetail.as_view(), name='my_page_day_detail'),

    path('mypage/schedule/<int:pk>/', views.MyPageSchedule.as_view(), name='my_page_schedule'),

    path('mypage/schedule/<int:pk>/delete/', views.MyPageScheduleDelete.as_view(), name='my_page_schedule_delete'),

    path('mypage/holiday/add/<int:pk>/<int:year>/<int:month>/<int:day>/<int:hour>/', views.my_page_holiday_add, name='my_page_holiday_add'),
]
