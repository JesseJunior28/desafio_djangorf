from django.contrib.auth.models import User
from rest_framework import serializers

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ["username", "password", "first_name", "email"]

    def create(self, validated_data):
        user = User(username=validated_data["username"], email=validated_data.get("email",""),
                    first_name=validated_data.get("first_name",""))
        user.set_password(validated_data["password"])
        user.save()
        return user

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "email"]
        read_only_fields = ["username"]