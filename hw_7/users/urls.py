from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
    path('profile', views.profile, name='profile'),
    path('login', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('signup', views.signup, name='signup'),
]
