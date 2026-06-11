from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from app.apps.products.models import Product, Favorite
from app.apps.products.serializers import ProductSerializer, FavoriteSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if category := params.get("category"):
            qs = qs.filter(category=category)
        if condition := params.get("condition"):
            qs = qs.filter(condition=condition)
        if min_price := params.get("min_price"):
            qs = qs.filter(sale_price__gte=min_price)
        if max_price := params.get("max_price"):
            qs = qs.filter(sale_price__lte=max_price)
        if keyword := params.get("keyword"):
            vector = SearchVector("name", weight="A") + SearchVector("description", weight="B")
            query = SearchQuery(keyword)
            qs = qs.annotate(rank=SearchRank(vector, query)).filter(rank__gt=0).order_by("-rank")
        sort = params.get("sort")
        if sort == "price":
            qs = qs.order_by("sale_price")
        elif sort == "newest":
            qs = qs.order_by("-created_at")
        elif sort == "favorite":
            qs = qs.annotate(fav_count=Count("favorites")).order_by("-fav_count", "-created_at")
        return qs

    @action(detail=True, methods=["post"])
    def favorite(self, request, pk=None):
        product = self.get_object()
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"success": False, "code": "VALIDATION_FAILED", "message": "参数不合法"}, status=status.HTTP_400_BAD_REQUEST)
        fav, created = Favorite.objects.get_or_create(user_id=user_id, product=product)
        return Response({"success": True, "favorited": created})

    @action(detail=True, methods=["post"])
    def unfavorite(self, request, pk=None):
        product = self.get_object()
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"success": False, "code": "VALIDATION_FAILED", "message": "参数不合法"}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = Favorite.objects.filter(user_id=user_id, product=product).delete()
        return Response({"success": True, "unfavorited": deleted > 0})

    @action(detail=False, methods=["get"])
    def my_favorites(self, request):
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response({"success": False, "code": "VALIDATION_FAILED", "message": "参数不合法"}, status=status.HTTP_400_BAD_REQUEST)
        fav_product_ids = Favorite.objects.filter(user_id=user_id).order_by("-created_at").values_list("product_id", flat=True)
        products = Product.objects.filter(id__in=fav_product_ids)
        product_map = {p.id: p for p in products}
        ordered_products = [product_map[pid] for pid in fav_product_ids if pid in product_map]
        serializer = self.get_serializer(ordered_products, many=True)
        return Response(serializer.data)

class StatsViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"])
    def trades(self, request):
        return Response({"range": request.query_params.get("range", "day"), "trade_count": 38, "trade_amount": 12680, "hot_categories": [{"category": "books", "count": 16}], "active_users": 72})
