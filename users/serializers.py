from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now

User = get_user_model()

# https://stackoverflow.com/questions/16857450/how-to-register-users-in-django-rest-framework


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    old_password = serializers.CharField(write_only=True, required=False)
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "username", "password", "old_password", "first_name",
                  "last_name", "email", "date_joined", "avatar", "email_verified",
                  "display_name_choice", "show_name", "show_email", "show_date_joined", "display_name")
        read_only_fields = ["id", "date_joined",
                            "email_verified", "display_name"]

    def get_display_name(self, obj):
        if obj.display_name_choice == User.USERNAME:
            return obj.username
        if obj.display_name_choice == User.FIRSTNAME:
            return obj.first_name
        if obj.display_name_choice == User.LASTNAME:
            return obj.last_name
        if obj.display_name_choice == User.FULLNAME:
            return obj.first_name + " " + obj.last_name
        if obj.display_name_choice == User.NICKNAME:
            return obj.nickname
        return obj.username

    def create(self, validated_data):

        user = self.Meta.model.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):

        account_change = False

        if "password" in validated_data:
            old_password = validated_data.pop("old_password", None)
            if old_password is None:
                raise AuthenticationFailed(
                    _("Old password needed for password reset"), "no_old_password")
            if not instance.check_password(old_password):
                raise AuthenticationFailed(
                    _("Old password does not match username"), "wrong_old_password")
            password = validated_data.pop("password")
            instance.set_password(password)
            account_change = True

        if "username" in validated_data and validated_data["username"] != instance.username:
            account_change = True

        email_field_name = self.Meta.model.get_email_field_name()
        if email_field_name in validated_data and validated_data[email_field_name] != getattr(instance, email_field_name):
            validated_data["email_verified"] = False

        if account_change:
            validated_data["invalidate_token_before"] = now()

        return super().update(instance, validated_data)

    def validate(self, data):
        if 'display_name_choice' in data:
            if data['display_name_choice'] == User.FIRSTNAME and not data.get('first_name'):
                raise serializers.ValidationError(
                    "cannot use empty first_name as display name")
            if data['display_name_choice'] == User.LASTNAME and not data.get('last_name'):
                raise serializers.ValidationError(
                    "cannot use empty last_name as display name")
            if data['display_name_choice'] == User.FULLNAME and not (data.get('first_name') and data.get('last_name')):
                raise serializers.ValidationError(
                    "cannot use full name as display name when either first_name or last_name is empty")
            if data['display_name_choice'] == User.NICKNAME and data.get('last_name'):
                raise serializers.ValidationError(
                    "cannot use empty nickname as display name")
        return data

    def to_representation(self, obj):
        # get the original representation
        representation = super().to_representation(obj)

        # check if request user is owner of the user object
        request = self.context.get('request', None)
        user = request.user if request else None
        is_owner = user and user.is_authenticated and user.pk == obj.pk

        # if not owner, filter representation based on user settings
        if not is_owner:
            allowed_fields = ["id", "display_name", "avatar"]
            if obj.show_name:
                allowed_fields.extend(("first_name", "last_name"))
            if obj.show_email and obj.email_verified:
                allowed_fields.append(User.get_email_field_name())
            if obj.show_date_joined:
                allowed_fields.append("date_joined")

            representation = {k: v for(k, v)in representation.items()
                              if k in allowed_fields}

        # return the modified representation
        return representation
