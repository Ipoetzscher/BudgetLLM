from django.urls import path

from . import views


urlpatterns = [
    path("transactions/", views.transaction_list),
    path("transactions/<int:transaction_id>/", views.transaction_detail),
    path("session/", views.active_session),
]