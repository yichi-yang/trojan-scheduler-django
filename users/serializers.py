from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Profile


# https://stackoverflow.com/questions/16857450/how-to-register-users-in-django-rest-framework

class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)
    avatar = serializers.URLField(source='profile.avatar')

    @transaction.atomic
    def create(self, validated_data):

        profile_data = validated_data.pop("profile")

        user = self.Meta.model.objects.create(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()

        profile = Profile.objects.create(user=user, **profile_data)
        profile.save()

        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile")
        for key, val in profile_data.items():
            setattr(instance.profile, key, val)
        instance.profile.save()
        return super().update(instance, validated_data)

    class Meta:
        model = get_user_model()
        # Tuple of serialized model fields (see link [2])
        fields = ("id", "username", "password", "first_name",
                  "last_name", "email", "date_joined", "avatar")
        read_only_fields = ['date_joined']
