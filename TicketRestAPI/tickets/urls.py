from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import PDFView

router = DefaultRouter()
router.register(r'ticket-threads', views.TicketThreadViewSet)
router.register(r'tickets', views.TicketViewSet)
router.register(r'comments', views.CommentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('gerar_pdf/<int:user_id>/', PDFView.as_view(), name='gerar_pdf')
]
