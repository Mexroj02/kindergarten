from django.urls import path
from .views import user_logout, user_login, register_view, profile_view, permission_denied_view, user_list_view, edit_user_view, delete_user_view

urlpatterns = [
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path('permission-denied/', permission_denied_view, name='permission_denied'),
    path('users/', user_list_view, name='user_list'),
    path('users/<int:user_id>/edit/', edit_user_view, name='edit_user'),
    path('users/<int:user_id>/delete/', delete_user_view, name='delete_user'),
]