from rest_framework import serializers
from .models import Author, Book,Borrower
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")       
        
        return {"user": user}

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'bio']

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'isbn', 'author', 'published_date', 'available','last_borrowed_date']
    
    def validate_isbn(self, value):
        if len(value) != 13 or not value.isdigit():
            raise serializers.ValidationError("ISBN must be 13 digits.")
        if Book.objects.filter(isbn=value).exists():
            raise serializers.ValidationError("This ISBN already exists.")
        return value

class BorrowerSerializer(serializers.ModelSerializer):      
    user = UserSerializer(read_only=True)  
    books_borrowed = BookSerializer(many=True, read_only=True)
    class Meta:
        model = Borrower
        fields = ['user', 'books_borrowed']
        
    def create(self, validated_data):        
        user = self.context['request'].user 
        validated_data['user'] = user          
        borrower = Borrower.objects.create(**validated_data)
        return borrower