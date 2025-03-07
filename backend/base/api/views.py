from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from base.models import Wilaya, Commune
from .serializers import WilayaSerializer, CommuneSerializer
from .permissions import IsAdminOrReadOnly

class WilayaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing Wilayas and getting their Communes.
    """
    permission_classes = [ IsAdminOrReadOnly]
    queryset = Wilaya.objects.all()
    serializer_class = WilayaSerializer

    @action(detail=True, methods=['get'])
    def communes(self, request, pk=None):
        """
        Custom route: List all Communes of a specific Wilaya.
        Example: GET /api/wilayas/1/communes/
        """
        communes = Commune.objects.filter(wilaya_id=pk)
        serializer = CommuneSerializer(communes, many=True)
        return Response(serializer.data)