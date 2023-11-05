from rest_framework import serializers

class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(required=True, max_length=100)
    password = serializers.CharField(max_length=100, required=True, min_length=8)
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)

    def validate(self, data):
        errors = {}

        # Check if email and password are required
        if not data.get('email', '') or not data.get('password', ''):
            if not data.get('email', ''):
                errors['email'] = ["Email is required."]
            if not data.get('password', ''):
                errors['password'] = ["Password is required."]

        # Check password length
        if len(data.get('password', '')) < 8:
            errors['password'] = ["This password is too short. It must contain at least 8 characters."]

        # Check field length for all fields
        for field_name in ['email', 'username', 'first_name', 'last_name']:
            if len(data.get(field_name, '')) > 100:
                errors[field_name] = [f"Only 100 characters are allowed for the {field_name} field."]

        if errors:
            raise serializers.ValidationError(errors)

        return data
