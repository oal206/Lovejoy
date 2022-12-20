from django.urls import path, include
from . import views

app_name = "request_evaluation"

urlpatterns = [
    path('create_request', views.create_request, name="create_request"),
]
