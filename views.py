import json

from .models import Item, Review
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django import forms
import json
from .models import Item, Review


class ItemForm(forms.Form):
    """Форма для валидации информации о товаре"""
    title = forms.CharField(min_length=1, max_length=64)
    description = forms.CharField(min_length=1, max_length=1024)
    price = forms.IntegerField(min_value=1, max_value=1000000)


class ReviewForm(forms.Form):
    """Форма для валидации отзыва о товаре"""
    text = forms.CharField(max_length=1024)
    grade = forms.IntegerField(min_value=1, max_value=10)


@method_decorator(csrf_exempt, name='dispatch')
class AddItemView(View):
    """View для создания товара."""
    def post(self, request):
        data = json.loads(request.body)
        data = ItemForm(data)
        if data.is_valid():
            rows = data.cleaned_data
            result = Item(**rows)
            result.save()
            return JsonResponse(data={"id": result.id}, status=201)
        else:
            return HttpResponse('запрос не прошел валидацию', status=500)


@method_decorator(csrf_exempt, name='dispatch')
class PostReviewView(View):
    """View для создания отзыва о товаре."""
    def post(self, request, item_id):
        # Здесь должен быть ваш код
        if not Item.objects.filter(id=item_id).exists():
            return HttpResponse("товара с таким id не существует.", status=404)
        data = json.loads(request.body)
        data = ReviewForm(data)
        if data.is_valid():
            rows = data.cleaned_data
            item_instance = Item.objects.get(id=item_id)
            rows.update({"item": item_instance})
            result = Review(**rows)
            result.save()
            return JsonResponse(data={"id": result.id}, status=201)
        else:
            return HttpResponse("запрос не прошел валидацию", status=200)


class GetItemView(View):
    """View для получения информации о товаре.

    Помимо основной информации выдает последние отзывы о товаре, не более 5
    штук.
    """

    def get(self, request, item_id):
        item = Item.objects.filter(id=item_id)
        if not item:
            return HttpResponse("товара с таким id не существует.", status=404)
        item = item[0]
        result = dict(zip(["id", "title", "description", "price"], [item.id, item.title, item.description, item.price]))
        review = Review.objects.filter(item_id=item_id).order_by("id")[:5]
        review_list = [{"id": row.id, "text": row.text, "grade": row.grade} for row in review]
        result.update({"reviews": review_list})
        return JsonResponse(result, status=200)
