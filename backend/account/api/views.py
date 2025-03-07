from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken


from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.conf import settings

from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()

class AuthViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])  # POST /api/v1/auth/register
    def register(self, request):
        serializer = RegisterSerializer(data=request.data, context = {'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {"message": "User registered successfully. Check your email to activate your account."},
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["get"])  # GET /api/v1/auth/activate
    def activate(self, request):
        uidb64 = request.query_params.get('uid')
        token = request.query_params.get('token')

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid activation link"}, status=status.HTTP_400_BAD_REQUEST)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"message": "Account activated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])  # POST /api/v1/auth/resend-activation
    def resend_activation(self, request):
        """Resends an activation email with a new token."""
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.is_active:
            return Response({"message": "Account is already activated"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a new activation token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Construct activation URL
        current_site = get_current_site(request).domain
        activation_url = f"http://{current_site}/v1/api/auth/activate/?uid={uid}&token={token}"

        # Send activation email
        subject = "Resend Activation - Activate Your Account"
        message = render_to_string('email/activation_email.html', {
            'user': user,
            'activation_url': activation_url,
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        return Response({"message": "A new activation email has been sent"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])  # POST /api/v1/auth/password/reset-request
    def password_reset_request(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Generate a password reset token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Construct password reset URL
        current_site = get_current_site(request).domain
        reset_url = f"http://{current_site}/api/v1/auth/password-reset/?uid={uid}&token={token}"

        # Send password reset email
        subject = "Password Reset - Reset Your Password"
        message = render_to_string('email/password_reset_email.html', {
            'user': user,
            'reset_url': reset_url,
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        return Response({"message": "A password reset email has been sent"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])  # POST /api/v1/auth/password/reset
    def password_reset(self, request):
        uidb64 = request.query_params.get('uid')
        token = request.query_params.get('token')
        new_password = request.data.get('new_password')
        
        if not new_password:
            return Response({"error": "New password is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid password reset link"}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        
        return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])  # POST /api/v1/auth/token
    def t_token(self, request): pass

    @action(detail=False, methods=["post"])  # POST /api/v1/auth/token/refresh
    def t_refresh_token(self, request): pass

    @action(detail=False, methods=["post"])  # POST /api/v1/auth/logout
    def t_logout(self, request): pass
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def password_update(self, request):
        user = request.user
        password = request.data.get('password')
        new_password = request.data.get('new_password')
        
        if not new_password:
            return Response({"error": "New password is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.check_password(password):
            return Response({"error": "Incorrect password"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response({"error": e.messages}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)

    
class UserViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        print("#"*100)
        print(serializer.data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='me', permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)