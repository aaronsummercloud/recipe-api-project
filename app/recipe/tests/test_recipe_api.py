''' Tests for the Recipe API '''
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    ''' create and return a recipe detail url '''
    return reverse('recipe:recipe-detail', args=[recipe_id])

def create_recipe(user, **params):
    ''' create and return a sample recipe '''
    defaults = {
        'title': 'Sample Recipe title',
        'time_minutes': '5',
        'price': Decimal('5.25'),
        'description': 'Sample description of the recipte',
        'link': 'http://example.com/recipe/pdf',
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe

class PublicRecipeApiTests(TestCase):
    ''' test unauthenticated API requests '''

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    ''' test authenticated API requests '''

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        ''' test recipe is limited to authenticated user '''
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'poassword',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_recipe_detail(self):
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe.id)
        response = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(response.data, serializer.data)

    def test_create_recipe(self):
        ''' test creating a recipe '''
        payload = { 
            'title': 'Sample Recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }

        response = self.client.post(RECIPES_URL, payload) # api/v1/recipe

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)

        self.assertEqual(recipe.user, self.user)