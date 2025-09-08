
from rest_framework import serializers


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