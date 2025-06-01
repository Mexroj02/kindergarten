from django import forms
from django.forms import inlineformset_factory
from .models import Meal, MealIngredient, Ingredient, Delivery

class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['name']

# Inline formset for ingredients in a meal
MealIngredientFormSet = inlineformset_factory(
    Meal,
    MealIngredient,
    fields=('ingredient', 'quantity'),
    extra=1,
    can_delete=True,
)


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'stock_quantity', 'treshold_quantity']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Tomato'}),
            'stock_quantity': forms.NumberInput(attrs={'step': 0.01}),
            'treshold_quantity': forms.NumberInput(attrs={'default': 1000}),
        }
        def clean_stock_quantity(self):
            qty = self.cleaned_data.get('stock_quantity')
            if qty is None or qty <= 0:
                raise forms.ValidationError("Stock quantity must be greater than zero.")
            return qty


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['ingredient', 'quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'step': 0.01}),
        }