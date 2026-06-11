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
        user_id = self.context.get("request").query_params.get("user_id") if self.context.get("request") else None
        if not user_id:
            return False
        return obj.favorites.filter(user_id=user_id).exists()

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = "__all__"
