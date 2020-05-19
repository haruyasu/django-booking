from django.urls import path
from app import views

urlpatterns = [
    path('', views.StoreList.as_view(), name='store_list'),
    path('store/<int:pk>/staffs/', views.StaffList.as_view(), name='staff_list'),
]
