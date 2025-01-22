from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path("",views.Login.as_view(),name="login"),
    path("index/",views.Index.as_view(),name="index"),
    path("register/",views.Register.as_view(),name="register"),
    path("add/",views.AddView.as_view(),name="add"),
    path('delete/<int:pk>/', views.Delete.as_view(), name='delete'),
    path('update/<int:pk>/', views.Update.as_view(), name='update'),
    path("view/",views.View.as_view(),name="view"),
    path('export_csv/',views.export_csv, name='export_csv'),
    path('export_excel/',views.export_excel, name='export_excel'),
    path('logout/', views.logout, name='logout'),
    path('delete_account/', views.delete_account, name='delete_account'),
]