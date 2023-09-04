from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .tasks import data_enrichment_task
from .models import *
from .emails_utils import send_email_notifications
from datetime import datetime

class LoginTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(LoginTokenSerializer, cls).get_token(user)
        token['username'] = user.username

        # update the last login date
        user.last_login = datetime.now()
        user.save()
        
        return token

class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, 
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'confirm_password')

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords didn't matched."})
        return attrs

    def create(self, validated_data):
        new_user = User(
            username=validated_data.get("username"),
            first_name=validated_data.get("first_name"),
            last_name=validated_data.get("last_name"),
            email=validated_data.get("email")
        )
        new_user.set_password(validated_data.get("password"))
        new_user.save()
        
        # create empty customer object for newly joined user.
        try:
            customer = Customer(django_user=new_user)
            customer.save()
            # create 4 empty competitor objects for newly joined customer.
            for _ in range(4):
                Competitor.objects.create(customer=customer)
        except: pass

        # create empty cookies object for newly joined user.
        try:
            InstagramCookies.objects.create(django_user=new_user)
        except: pass

        # create empty instagram credentials for newly joined user.
        try:
            InstaCredentials.objects.create(django_user=new_user)
        except: pass

        # create empty tiktok credentials for newly joined user.
        try:
            TiktokCredentials.objects.create(django_user=new_user)
        except: pass

        data_enrichment_task(new_user) # populates the location of user signup
        send_email_notifications(new_user.first_name, new_user.email)

        return new_user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)