from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile, SubscriptionPlan

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "phone", "ui_language", "is_premium",
                  "is_staff", "is_active", "auth_provider", "date_joined"]
        read_only_fields = ["id", "is_premium", "is_staff", "is_active", "auth_provider", "date_joined"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=False, allow_blank=True, max_length=150)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)

    class Meta:
        model = User
        fields = ["username", "first_name", "email", "phone", "password", "ui_language"]

    def validate_username(self, value):
        value = (value or "").strip()
        if value and User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Bu login band.")
        return value

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Bu email allaqachon ro'yxatdan o'tgan.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        if not validated_data.get("username"):
            from .services import unique_username
            validated_data["username"] = unique_username(validated_data["email"])
        # Email tasdiqlanguncha hisob faol emas (haqiqiy pochta ekanini tekshirish uchun) —
        # RegisterView.perform_create tasdiqlash kodini pochtaga yuboradi.
        user = User(**validated_data, is_active=False)
        user.set_password(password)
        user.save()
        return user


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)


class ResendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class SocialAuthSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=["google", "facebook"])
    token = serializers.CharField()  # Google uchun id_token, Facebook uchun access_token


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "user", "avatar_preference", "daily_goal_minutes", "timezone",
            "onboarding_goal", "onboarding_role", "onboarding_completed",
        ]


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """Admin panel orqali foydalanuvchini tahrirlash (premium/staff/faol holat)."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "is_premium", "is_staff", "is_active"]


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ["id", "name", "price_usd", "voice_cloning_enabled", "max_sessions_per_day"]
