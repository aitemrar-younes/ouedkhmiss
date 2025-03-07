from rest_framework import viewsets, permissions, status
from product.models import Category, Product, SavedProduct
from .serializers import CategorySerializer
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import ProductSerializer, SavedProductSerializer
from rest_framework.response import Response
from base.api.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from rest_framework.decorators import action
from .filters import ProductFilter

class CategoryViewSet(viewsets.ModelViewSet):  
    """
    ViewSet for listing all categories.
    """
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Products: Create, Retrieve, Update, Delete, and Upload Images.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    queryset = Product.objects.prefetch_related('images', 'category', 'commune', 'user')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductFilter
    filterset_fields = ['category', 'commune']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """Set the user from request before saving."""
        user = self.request.user
        serializer.save(user=user)
        
    @action(detail=True, methods=["get"], permission_classes=[permissions.AllowAny])
    def user(self, request, pk=None):
        """List all products for the authenticated user."""
        products = Product.objects.filter(user=pk)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def user_saved(self, request):
        """List all saved products for the authenticated user."""
        saved_products = SavedProduct.objects.filter(user=request.user)
        serializer = SavedProductSerializer(saved_products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def save(self, request, pk=None):
        """Save a product (if not already saved)."""
        # Ensure product exists
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if product is already saved
        saved_product, created = SavedProduct.objects.get_or_create(user=request.user, product=product)

        if not created:
            return Response({"message": "Product already saved"}, status=status.HTTP_409_CONFLICT)

        return Response(SavedProductSerializer(saved_product).data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=["delete"], permission_classes=[permissions.IsAuthenticated])
    def unsave(self, request, pk=None):
        """Remove a saved product (unsave)."""
        try:
            saved_product = SavedProduct.objects.get(user=request.user, product_id=pk)
            saved_product.delete()
            return Response({"message": "Product removed from saved list"}, status=status.HTTP_204_NO_CONTENT)
        except SavedProduct.DoesNotExist:
            return Response({"error": "Product not saved"}, status=status.HTTP_404_NOT_FOUND)
