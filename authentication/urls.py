from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('signin', views.signin, name="signin"),
    path('signup', views.signup, name="signup"),
    path('signout', views.signout, name="signout"),
    path('activate/<uidb64>/<token>', views.activate, name="activate"),
    path('forgot_password', views.forgot_password, name="forgot_password"),
    path('reset_password/<uidb64>/<token>', views.reset_password, name="reset_password"),
    path('update_password', views.update_password, name="update_password")
]
