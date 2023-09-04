from django_rest_passwordreset.signals import reset_password_token_created
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.urls import reverse
from django.core.mail import send_mail, EmailMessage
from django.conf import settings


class User(AbstractUser):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )

    profile_image = models.FileField(null=True, blank=True, upload_to='profiles/')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    bio = models.TextField(default="")

    # location information, populated during signup process...
    region = models.CharField(max_length=200, default="n/a")
    country = models.CharField(max_length=200, default="n/a")
    country_code = models.CharField(max_length=10, default="n/a")
    city = models.CharField(max_length=200, default="n/a")
    continent = models.CharField(max_length=100, default="n/a")
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    def __str__(self):
        return self.username


class Customer(models.Model):
    django_user = models.OneToOneField(User, related_name='customer_profile', on_delete=models.CASCADE)
    tiktok_user_handle = models.CharField(max_length=1000, null=True, blank=True)
    insta_user_handle = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return f"Customer {self.django_user.username}"

    class Meta:
        verbose_name_plural = 'Customers List'


class Competitor(models.Model):
    customer = models.ForeignKey(Customer, related_name='competitors', on_delete=models.CASCADE)
    tiktok_user_handle = models.CharField(max_length=1000, default="")
    insta_user_handle = models.CharField(max_length=1000, default="")

    def __str__(self):
        return f"Competitor of {self.customer.django_user.username}"

    class Meta:
        verbose_name_plural = 'Competitors List'


class UserActivity(models.Model):
    customer = models.ForeignKey(Customer, related_name='activities', on_delete=models.CASCADE)
    django_user = models.CharField(max_length=1000)
    customer_handle = models.CharField(max_length=1000)
    competitors = models.CharField(max_length=5000)
    common_profiles = models.CharField(max_length=5000, default='')
    flow_name = models.CharField(max_length=100, default="Instagram")
    status = models.BooleanField(default=False)
    created = models.CharField(max_length=200)

    def __str__(self):
        return f"Activity of {self.customer.django_user.username}"

    class Meta:
        verbose_name_plural = 'User Activities'


class InstaCredentials(models.Model):
    django_user = models.OneToOneField(User, related_name='insta_credentials', on_delete=models.CASCADE)
    username = models.CharField(max_length=500, null=True)
    password = models.CharField(max_length=500, null=True)

    def __str__(self):
        return f"Insta Credentials of {self.django_user.username}"


class InstagramCookies(models.Model):
    django_user = models.OneToOneField(User, related_name='insta_cookies', on_delete=models.CASCADE)
    csrftoken = models.CharField(max_length=200, default='')
    ds_user_id = models.CharField(max_length=200, default='')
    ig_did = models.CharField(max_length=200, default='')
    ig_nrcb = models.CharField(max_length=200, default='')
    mid = models.CharField(max_length=200, default='')
    rur = models.CharField(max_length=200, default='')
    sessionid = models.CharField(max_length=200, default='')

    def __str__(self):
        return f"Insta Cookies of {self.django_user.username}"


class TiktokCredentials(models.Model):
    django_user = models.OneToOneField(User, related_name='tiktok_credentials', on_delete=models.CASCADE)
    username = models.CharField(max_length=500, null=True)
    password = models.CharField(max_length=500, null=True)

    def __str__(self):
        return f"Tiktok Credentials of {self.django_user.username}"


# PASSWORD RESET SIGNALS FOR DJANGO REST FRAMEWORK
@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    # token_url = f"http://3.139.124.188{reverse('password_reset:reset-password-request')}?token={
    # reset_password_token.key}"

    # token_url = f"http://3.139.124.188/customers/validate_token/{reset_password_token.key}/"
    token_url = f"http://localhost:3000/auth/confirmpassword/{reset_password_token.key}/"
    email_plaintext_message = f"""
    Hi {reset_password_token.user.username},

    Forgot your password?
    We received a request to reset the password for your account.

    To reset your password, follow the below link:
    {token_url}
    """

    email_msg = EmailMessage(
        subject="Password Reset for CrazeSocial",
        body=email_plaintext_message,
        from_email=settings.EMAIL_HOST_USER,
        to=[reset_password_token.user.email, ]
    )
    email_msg.send()


# teams specific model

class Teams_data(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="User")
    link = models.CharField(max_length=2000, null=True, blank=True, verbose_name="Teams Uri")
    # update = models.CharField(max_length=10, null=True, blank=True, verbose_name="Update Schedule (d/w/m)")

    def __str__(self):
        return self.user

    class Meta:
        verbose_name_plural = 'Microsoft Teams Data'
