from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token  
from . import views
from .views import CustomLoginView, CustomLogoutView 

router = DefaultRouter()
router.register(r'ticket-threads', views.TicketThreadViewSet)
router.register(r'tickets', views.TicketViewSet)
router.register(r'comments', views.CommentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('get-users/', views.get_users, name='get-users'),
    path('api/login/', CustomLoginView.as_view(), name='login'), 
    path('api/logout/', CustomLogoutView.as_view(), name='logout'), 
]
