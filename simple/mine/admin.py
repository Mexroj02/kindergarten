from django.contrib import admin
from .models import Ingredient, Meal, MealIngredient

class MealIngredientInline(admin.TabularInline):
    model = MealIngredient
    extra = 1

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    inlines = [MealIngredientInline]

admin.site.register(Ingredient)
