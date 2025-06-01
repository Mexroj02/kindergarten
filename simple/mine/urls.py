from django.urls import path
from . import views

urlpatterns = [
    path('meals/', views.meal_list, name='meal_list'),
    path('meals/create/', views.create_meal, name='create_meal'),
    path('meals/<int:meal_id>/edit/', views.update_meal, name='update_meal'),
    path('meals/<int:meal_id>/delete/', views.delete_meal, name='delete_meal'),
    path('meals/serve/<int:meal_id>/', views.serve_meal, name='serve_meal'),
    path('ingredients/', views.ingredient_list, name='ingredient_list'),
    path('ingredients/create/', views.create_ingredient, name='create_ingredient'),
    path('ingredients/update/<int:ingredient_id>/', views.update_ingredient, name='update_ingredient'),
    path('ingredients/delete/<int:ingredient_id>/', views.delete_ingredient, name='delete_ingredient'),
    path('ingredients/check-name/', views.check_ingredient_name, name='check_ingredient_name'),
    path('deliveries/create/', views.create_delivery, name='create_delivery'),
    path('deliveries/', views.delivery_list_view, name='delivery_list'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
