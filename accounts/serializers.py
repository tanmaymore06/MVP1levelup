from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8) # 'write_only' means the field is accepted as input but will not be included in the serialized output.
# Which means, when a user registers, they will provide a password, but the password will not be included in the response sent back to the frontend for security reasons. 

    class Meta: # the frontend will only receive the id, username, email, and password fields when a user registers
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        '''Create a new user with the provided validated data.'''
        
        return User.objects.create_user(    # 'create_user' is a method provided by Django's User model that handles the creation of a new user, including hashing the password and saving the user to the database.
            username=validated_data["username"],
            email=validated_data.get("email", ""),  # Why only in the case of email, the 'get' method is used? Because the email field is optional, and using 'get' allows us to provide a default value (an empty string) if the email is not included in the validated data. For username and password, we expect them to be provided, so we access them directly without 'get'.
            password=validated_data["password"]
        )