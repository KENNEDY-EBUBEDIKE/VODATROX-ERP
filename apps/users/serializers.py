from rest_framework.serializers import ModelSerializer
from .models import User
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
import os


class MyAuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label=_("email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        password = attrs.get('password')
        email = attrs.get('email')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)

            # The authenticate call simply returns ...
            # None for is_active=False
            # users. (Assuming the default ModelBackend authentication backend.)
            if not user:
                msg = _('Email or password is incorrect')
                raise serializers.ValidationError(detail=msg)
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(detail=msg)
        attrs['user'] = user
        return attrs


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.surname = validated_data.get('surname', instance.surname)
        instance.appointment = validated_data.get('appointment', instance.appointment)

        if validated_data.get('photo',):
            if instance.photo:
                os.remove(instance.photo.path)
            instance.photo = validated_data.get('photo', instance.photo)

        instance.save()
        return instance
