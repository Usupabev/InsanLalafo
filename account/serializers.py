from django.contrib.auth import authenticate
from rest_framework import serializers

from account.models import MyUser
from account.utils import send_activation_code


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, write_only=True)
    password_confirm = serializers.CharField(min_length=6, write_only=True)

    class Meta:
        model = MyUser
        fields = ('email', 'password', 'password_confirm')

    def validate(self, validated_data): #def validate = def clean, validated_data = cleaned_data
        password = validated_data.get('password')
        password_confirm = validated_data.get('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Пароли не совпадают')
        return validated_data

    def create(self, validated_data):
        email = validated_data.get('email')
        password = validated_data.get('password')
        user = MyUser.objects.create_user(email=email, password=password)
        send_activation_code(email=user.email, activation_code=user.activation_code)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(label='Password', style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            if not user:
                message = 'Неправильно введен логин или пароль'
                raise serializers.ValidationError(message, code='authorization')
        else:
            message = 'Поле должно содержать email или пароль.'
            raise serializers.ValidationError(message, code='authorization')

        attrs['user'] = user
        return attrs

class CreateNewPasswordSerialzier(serializers.Serializer):
    email = serializers.EmailField()
    activation_code = serializers.CharField(max_length=20)
    password = serializers.CharField(min_length=6, required=True)
    password_confirm = serializers.CharField(min_length=6, required=True)

    def validate_activation_code(self, code):
        if not MyUser.objects.filter(activation_code=code, is_active=False).exists():
            raise serializers.ValidationError('Неверный код активации')
        return code

    def validate_email(self, email):
        if not MyUser.objects.filter(email=email).exists():
            raise serializers.ValidationError('Пользователя с таким email не найден')
        return email

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Пароли не совпадают')
        return attrs

    def save(self, **kwargs):
        data = self.validated_data
        email = data.get('email')
        code = data.get('activation_code')
        password = data.get('password')
        try:
            user = MyUser.objects.get(email=email, activation_code=code, is_active=False)
        except:
            raise serializers.ValidationError('User not found')
        user.is_active = True
        user.activation_code = ''
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'first_name', 'email']

