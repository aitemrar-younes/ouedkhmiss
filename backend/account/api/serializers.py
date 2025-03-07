from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password2 = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'birth_date', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords must match"})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')  # Remove password2 field
        user = User.objects.create_user(**validated_data)  # User is inactive

        # Generate activation token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Construct activation URL
        current_site = get_current_site(self.context['request']).domain
        activation_url = f"http://{current_site}/api/v1/auth/activate/?uid={uid}&token={token}"

        # Send activation email
        subject = "Activate Your Account"
        message = render_to_string('email/activation_email.html', {
            'user': user,
            'activation_url': activation_url,
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        return user



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom login serializer to check if the user is activated.
    """

    def validate(self, attrs):
        # Authenticate user with provided credentials
        """ user = authenticate(username=attrs['email'], password=attrs['password'])
        print(user)

        if user:
            if not user.is_active:
                raise serializers.ValidationError("Account not activated. Please check your email.")
        """
        email = attrs.get("email")
        password = attrs.get("password")

        # Manually fetch user from database (ignores `is_active`)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("No active account found with the given credentials")

        # Check password manually
        if not check_password(password, user.password):
            raise serializers.ValidationError("No active account found with the given credentials")

        # If user is inactive, return custom message
        if not user.is_active:
            raise serializers.ValidationError("Account not activated. Please check your email.")

        return super().validate(attrs)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number', 'birth_date', 'is_active']
        read_only_fields = ['email', 'phone_number', 'is_active']
        