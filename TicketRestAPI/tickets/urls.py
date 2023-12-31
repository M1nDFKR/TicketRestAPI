from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token  
from . import views
from .views import CustomObtainAuthToken, LogoutView
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'ticket-threads', views.TicketThreadViewSet)
router.register(r'tickets', views.TicketViewSet)
router.register(r'comments', views.CommentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('get-users/', views.get_users, name='get-users'),
    path('api/userinfo/', views.get_authenticated_user, name='userinfo'),
    path('api/login/', CustomObtainAuthToken.as_view(), name='api_token_auth'),
    path('api/logout/', LogoutView.as_view(), name='api_token_logout'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
