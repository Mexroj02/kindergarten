from django.db import models
import math
from django.contrib.auth.models import User

class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    stock_quantity = models.FloatField(default=0)  # current stock in grams (or your unit)
    treshold_quantity = models.PositiveBigIntegerField(default=1000)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Meal(models.Model):
    name = models.CharField(max_length=100)
    ingredients = models.ManyToManyField(
        Ingredient,
        through='MealIngredient',
        related_name='meals'
    )

    def __str__(self):
        return self.name

    def total_ingredients(self):
        return self.mealingredient_set.all()
    
    def get_max_portions(self):
        portions_list = []
        for mi in self.mealingredient_set.all():
            stock = mi.ingredient.stock_quantity
            required = mi.quantity
            if required == 0:
                continue
            portions = stock / required
            portions_list.append(portions)
        if not portions_list:
            return 0
        return math.floor(min(portions_list))

class MealIngredient(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()  # quantity required for this ingredient in this meal

    def __str__(self):
        return f"{self.quantity} units of {self.ingredient.name} for {self.meal.name}"
    
class Delivery(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(help_text="Quantity delivered (in grams or your unit)")
    delivered_at = models.DateTimeField(auto_now_add=True)
    delivered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        # Automatically update stock_quantity of the ingredient
        self.ingredient.stock_quantity += self.quantity
        self.ingredient.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} units of {self.ingredient.name} delivered on {self.delivered_at}"

class MealServe(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    served_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.meal.name} served on {self.date.date()}"