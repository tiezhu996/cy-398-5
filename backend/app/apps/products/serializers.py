from django.db.models import Count
from rest_framework import serializers
from app.apps.products.models import Product, Favorite

class ProductSerializer(serializers.ModelSerializer):
    favorite_count = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_favorite_count(self, obj):
        return obj.favorites.count()

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request:
            return False
        user_id = request.query_params.get("user_id") if hasattr(request, "query_params") else request.GET.get("user_id")
        if not user_id:
            return False
        return obj.favorites.filter(user_id=user_id).exists()

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = "__all__"
