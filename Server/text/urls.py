from django.urls import path
from text import views


urlpatterns = [
    path('<ipfsHash>/', views.TextDetailView.as_view()),
    path('', views.TextListView.as_view()),
]