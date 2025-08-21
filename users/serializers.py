from django.contrib.auth.models import User, Group
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'groups']


# Serializer base para as validações simples

class UserBaseSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email']

    def validate_username(self, username):
        user = getattr(self, 'instance', None)
        if user is None:  # create
            if User.objects.filter(username=username).exists():
                raise serializers.ValidationError("Este username não está disponível.")
        else:  # update
            if user.username != username and User.objects.filter(username=username).exists():
                raise serializers.ValidationError("Este username não está disponível.")
        return username



# Serializer para registro de novos clientes

class UserSignUpSerializer(UserBaseSerializer):
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        # Adiciona o grupo Cliente
        cliente_group = Group.objects.filter(name='Cliente').first()
        if cliente_group:
            user.groups.add(cliente_group)
        return user

# Criação de usuários (admin)

class UserCreateSerializer(UserBaseSerializer):
    group = serializers.CharField(write_only=True, required=True)

    def validate_group(self, group_name):
        group = Group.objects.filter(name=group_name).first()
        if not group:
            raise serializers.ValidationError("Este grupo não existe.")
        return group

    def create(self, validated_data):
        group_instance = validated_data.pop('group')
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        # Para dicionar grupo definido
        user.groups.add(group_instance)
        return user

# Atualizar usuários

class UserUpdateSerializer(UserBaseSerializer):
    """Atualização de informações do usuário, incluindo senha."""
    
    class Meta(UserBaseSerializer.Meta):
        read_only_fields = ['username']  # Username não pode ser alterado

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance