from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _


# https://stackoverflow.com/questions/16857450/how-to-register-users-in-django-rest-framework

class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    old_password = serializers.CharField(write_only=True)

    def create(self, validated_data):

        user = self.Meta.model.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):

        if "password" in validated_data:
            old_password = validated_data.pop("old_password", None)
            if old_password is None:
                raise AuthenticationFailed(_("Old password needed for password reset"), "no_old_password")
            if not instance.check_password(old_password):
                raise AuthenticationFailed(_("Old password does not match username"), "wrong_old_password")
            password = validated_data.pop("password")
            instance.set_password(password)

        email_field_name = self.Meta.model.get_email_field_name()
        if email_field_name in validated_data and validated_data[email_field_name] != getattr(instance, email_field_name):
            validated_data["email_verified"] = False

        return super().update(instance, validated_data)

    class Meta:
        model = get_user_model()
        # Tuple of serialized model fields (see link [2])
        fields = ("id", "username", "password", "old_password", "first_name",
                  "last_name", "email", "date_joined", "avatar", "email_verified")
        read_only_fields = ["date_joined", "email_verified"]
