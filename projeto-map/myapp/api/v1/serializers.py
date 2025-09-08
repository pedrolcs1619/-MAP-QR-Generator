# myapp/api/v1/serializers.py

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.core.exceptions import ValidationError


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer para registro de novos usuários
    """
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        style={'input_type': 'password'},
        help_text="Senha deve ter pelo menos 8 caracteres"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirme sua senha"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password_confirm')
        extra_kwargs = {
            'email': {'required': True},
            'username': {'help_text': 'Nome de usuário único'},
            'email': {'help_text': 'Email válido'},
        }
    
    def validate_email(self, value):
        """
        Verifica se o email já está em uso
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email já está sendo usado.")
        return value
    
    def validate_username(self, value):
        """
        Verifica se o username já está em uso
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nome de usuário já está sendo usado.")
        return value
    
    def validate(self, attrs):
        """
        Validações personalizadas
        """
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        
        # Verifica se as senhas coincidem
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'As senhas não coincidem.'
            })
        
        # Validação da senha usando validadores do Django
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError({
                'password': list(e.messages)
            })
        
        return attrs
    
    def create(self, validated_data):
        """
        Cria um novo usuário
        """
        # Remove password_confirm dos dados validados
        validated_data.pop('password_confirm', None)
        
        # Cria o usuário com senha criptografada
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer para login de usuários
    """
    username = serializers.CharField(
        max_length=150,
        help_text="Nome de usuário ou email"
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Sua senha"
    )


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para perfil do usuário
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'is_active')
        read_only_fields = ('id', 'username', 'date_joined', 'is_active')
    
    def validate_email(self, value):
        """
        Verifica se o email já está em uso por outro usuário
        """
        user = self.context['request'].user
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("Este email já está sendo usado por outro usuário.")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para mudança de senha
    """
    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Sua senha atual"
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Nova senha (mínimo 8 caracteres)"
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirme a nova senha"
    )
    
    def validate(self, attrs):
        """
        Valida se as novas senhas coincidem
        """
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': 'As novas senhas não coincidem.'
            })
        
        # Validação da nova senha
        try:
            validate_password(new_password)
        except ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        
        return attrs