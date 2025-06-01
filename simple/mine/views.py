# mine/views.py

from django.shortcuts import render, redirect
from .models import Meal, Ingredient, MealIngredient, Delivery, MealServe
from .forms import MealForm, IngredientForm, DeliveryForm
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from django.db.models import Sum, Max, F, Count
from datetime import datetime
import logging
from django.utils.timezone import now
from django.db.models.functions import TruncDate


serve_logger = logging.getLogger('meal_serve')
delivery_logger = logging.getLogger('delivery')

def meal_list(request):
    meals = Meal.objects.all()
    return render(request, 'meal_list.html', {'meals': meals})

def create_meal(request):
    ingredients = Ingredient.objects.all()
    if request.method == 'POST':
        form = MealForm(request.POST)
        if form.is_valid():
            meal = form.save()
            
            # Get lists of ingredient ids and quantities from POST data
            ingredient_ids = request.POST.getlist('ingredients')
            quantities = request.POST.getlist('quantities')
            
            for ing_id, qty in zip(ingredient_ids, quantities):
                if ing_id and qty:
                    MealIngredient.objects.create(
                        meal=meal,
                        ingredient_id=int(ing_id),
                        quantity=float(qty)
                    )
            
            return redirect('meal_list')
    else:
        form = MealForm()

    return render(request, 'create_meal.html', {
        'form': form,
        'ingredients': ingredients
    })


def delete_meal(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id)
    
    if request.method == 'POST':
        meal.delete()
        return redirect('meal_list')
    
    # Optional: Confirm delete page
    return render(request, 'confirm_delete_meal.html', {
        'meal': meal
    })

def update_meal(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id)
    ingredients = Ingredient.objects.all()
    
    if request.method == 'POST':
        form = MealForm(request.POST, instance=meal)
        if form.is_valid():
            meal = form.save()
            
            # Clear existing related MealIngredients
            MealIngredient.objects.filter(meal=meal).delete()
            
            # Update with new ingredient data
            ingredient_ids = request.POST.getlist('ingredients')
            quantities = request.POST.getlist('quantities')
            
            for ing_id, qty in zip(ingredient_ids, quantities):
                if ing_id and qty:
                    MealIngredient.objects.create(
                        meal=meal,
                        ingredient_id=int(ing_id),
                        quantity=float(qty)
                    )
            
            return redirect('meal_list')
    else:
        form = MealForm(instance=meal)
        
        # Prepare existing ingredients and quantities for the form template
        existing_ingredients = MealIngredient.objects.filter(meal=meal)
    
    return render(request, 'update_meal.html', {
        'form': form,
        'ingredients': ingredients,
        'meal': meal,
        'existing_ingredients': existing_ingredients
    })

def serve_meal(request, meal_id):
    meal = get_object_or_404(Meal, id=meal_id)
    meal_ingredients = MealIngredient.objects.filter(meal=meal)

    # Calculate max portions possible
    portions = 0
    if meal_ingredients.exists():
        portions_list = []
        for mi in meal_ingredients:
            if mi.quantity > 0:
                portions_count = mi.ingredient.stock_quantity / mi.quantity
                portions_list.append(portions_count)
        portions = int(min(portions_list)) if portions_list else 0

    if request.method == "POST":
        try:
            serve_quantity = int(request.POST.get("serve_quantity"))
        except (TypeError, ValueError):
            messages.error(request, "Please enter a valid number")
            return redirect('serve_meal', meal_id=meal_id)

        if serve_quantity <= 0:
            messages.error(request, "Quantity must be greater than zero")
            return redirect('serve_meal', meal_id=meal_id)

        if serve_quantity > portions:
            messages.error(request, f"Not enough stock to serve {serve_quantity} portions.")
            return redirect('serve_meal', meal_id=meal_id)

        # Reduce stock
        for mi in meal_ingredients:
            mi.ingredient.stock_quantity -= mi.quantity * serve_quantity
            mi.ingredient.save()

        # ✅ Optional: Save to MealServe model (if you have it)
        # MealServe.objects.create(meal=meal, served_by=request.user, portions=serve_quantity)

        # ✅ Log this action
        serve_logger.info(f"{request.user.username} served {serve_quantity} portion(s) of {meal.name}")

        messages.success(request, f"Successfully served {serve_quantity} portions of {meal.name}!")
        return redirect('meal_list')


    return render(request, 'serve_meal.html', {
        'meal': meal,
        'portions': portions,
    })


@login_required
def ingredient_list(request):
    query = request.GET.get('q', '').strip()
    ingredients = Ingredient.objects.all()

    if query:
        ingredients = ingredients.filter(Q(name__icontains=query))

    return render(request, 'ingredient_list.html', {
        'ingredients': ingredients,
        'query': query,
    })

@login_required
def create_ingredient(request):
    if request.method == 'POST':
        form = IngredientForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name'].strip()
            stock = form.cleaned_data.get('stock_quantity')

            if Ingredient.objects.filter(name__iexact=name).exists():
                messages.error(request, f"Ingredient '{name}' already exists.")
            elif stock <= 0:
                messages.error(request, "Stock quantity must be greater than zero.")
            else:
                ingredient = form.save(commit=False)
                ingredient.created_by = request.user  # track who created it
                ingredient.save()
                messages.success(request, f"Ingredient '{name}' created successfully!")
                return redirect('ingredient_list')
    else:
        form = IngredientForm()

    return render(request, 'create_ingredient.html', {'form': form})

@login_required
def check_ingredient_name(request):
    name = request.GET.get('name', '').strip()
    exists = Ingredient.objects.filter(name__iexact=name).exists()
    return JsonResponse({'exists': exists})


@login_required
def create_delivery(request):
    ingredients = Ingredient.objects.all()

    if request.method == 'POST':
        total_forms = int(request.POST.get('form-TOTAL_FORMS', 0))

        for i in range(total_forms):
            ing_id = request.POST.get(f'ingredient_{i}')
            qty = request.POST.get(f'quantity_{i}')

            if ing_id and qty:
                try:
                    ingredient = Ingredient.objects.get(id=ing_id)
                    qty_float = float(qty)

                    # ✅ This saves delivery and updates stock (via model logic)
                    Delivery.objects.create(
                        ingredient=ingredient,
                        quantity=qty_float,
                        delivered_by=request.user
                    )

                    # ✅ Log it
                    delivery_logger.info(f"{request.user.username} delivered {qty_float}g of {ingredient.name}")

                except (Ingredient.DoesNotExist, ValueError):
                    continue

        return redirect('ingredient_list')

    return render(request, 'create_delivery.html', {'ingredients': ingredients})


@login_required
def delivery_list_view(request):
    deliveries = Delivery.objects.select_related('ingredient', 'delivered_by').order_by('-delivered_at')
    return render(request, 'delivery_list.html', {'deliveries': deliveries})

@login_required
def update_ingredient(request, ingredient_id):
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)

    if request.method == 'POST':
        form = IngredientForm(request.POST, instance=ingredient)
        if form.is_valid():
            form.save()
            return redirect('ingredient_list')
    else:
        form = IngredientForm(instance=ingredient)

    return render(request, 'update_ingredient.html', {
        'form': form,
        'ingredient': ingredient
    })

def delete_ingredient(request, ingredient_id):
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)
    
    if request.method == 'POST':
        ingredient.delete()
        return redirect('ingredient_list')
    
    # Optional: Confirm delete page
    return render(request, 'confirm_delete_ingredient.html', {
        'ingredient': ingredient
    })

@login_required
def dashboard_view(request):
    today = now()
    start_of_month = datetime(today.year, today.month, 1)

    # Meals served per day
    meal_data = (
        MealServe.objects
        .filter(date__gte=start_of_month)
        .annotate(day=TruncDate('date'))
        .values('day')
        .annotate(total=Count('id'))
        .order_by('day')
    )

    # Deliveries grouped by ingredient
    delivery_data = (
        Delivery.objects
        .filter(delivered_at__gte=start_of_month)
        .values('ingredient__name')
        .annotate(total=Sum('quantity'))
        .order_by('-total')
    )

    # Top stock ingredient
    max_ingredient = Ingredient.objects.order_by('-stock_quantity').first()

    # Monthly total delivery quantity
    total_delivered = Delivery.objects.filter(delivered_at__gte=start_of_month).aggregate(Sum('quantity'))['quantity__sum'] or 0

    # Meals served this month
    meals_served = MealServe.objects.filter(date__gte=start_of_month).count()

    return render(request, 'dashboard.html', {
        'meal_chart': list(meal_data),
        'delivery_chart': list(delivery_data),
        'meals_served': meals_served,
        'total_delivered': total_delivered,
        'max_ingredient': max_ingredient,
    })
