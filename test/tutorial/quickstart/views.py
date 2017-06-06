from django.contrib.auth.models import User, Group

from rest_framework import viewsets
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser

from tutorial.quickstart.serializers import SignUpSerializer, GroupSerializer


@permission_classes([IsAdminUser])
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = GroupSerializer


@permission_classes([AllowAny])
class SignUpViewSet(viewsets.ModelViewSet):
    queryset = User.objects.none()
    serializer_class = SignUpSerializer