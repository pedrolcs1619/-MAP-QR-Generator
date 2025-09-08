# myapp/api/v1/viewsets.py

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserProfileSerializer,
    ChangePasswordSerializer
)


class AuthViewSet(viewsets.GenericViewSet):
    """
    ViewSet para autenticação de usuários
    """
    serializer_class = UserRegistrationSerializer
    
    def get_permissions(self):
        """
        Define permissões específicas para cada action
        """
        if self.action in ['create', 'login']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """
        Define o serializer apropriado para cada action
        """
        if self.action == 'create':
            return UserRegistrationSerializer
        elif self.action == 'login':
            return UserLoginSerializer
        elif self.action == 'profile':
            return UserProfileSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        return UserRegistrationSerializer
    
    def create(self, request):
        """
        Registra um novo usuário
        POST /api/v1/auth/
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Gera tokens JWT para o usuário recém-criado
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Usuário criado com sucesso',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        Autentica o usuário e retorna tokens JWT
        POST /api/v1/auth/login/
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            
            if user:
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'message': 'Login realizado com sucesso',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                    },
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Credenciais inválidas'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """
        Faz logout do usuário invalidando o refresh token
        POST /api/v1/auth/logout/
        """
        try:
            refresh_token = request.data.get("refresh_token")
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'message': 'Logout realizado com sucesso'
            }, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({
                'error': 'Token inválido'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """
        Retorna o perfil do usuário autenticado
        GET /api/v1/auth/profile/
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """
        Atualiza o perfil do usuário autenticado
        PUT/PATCH /api/v1/auth/update_profile/
        """
        serializer = self.get_serializer(
            request.user, 
            data=request.data, 
            partial=request.method == 'PATCH'
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Perfil atualizado com sucesso',
                'user': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Permite ao usuário alterar sua senha
        POST /api/v1/auth/change_password/
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            # Verifica a senha atual
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({
                    'error': 'Senha atual incorreta'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Define a nova senha
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({
                'message': 'Senha alterada com sucesso'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)