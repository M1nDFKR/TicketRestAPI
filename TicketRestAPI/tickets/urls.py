from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'ticket-threads', views.TicketThreadViewSet)
router.register(r'tickets', views.TicketViewSet)
router.register(r'comments', views.CommentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
