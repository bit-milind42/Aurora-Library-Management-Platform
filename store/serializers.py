from rest_framework import serializers
from .models import CustomUser, Category, Author, Book, Issue, Fine


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'bio']


class BookSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(source='category', queryset=Category.objects.all(), write_only=True)
    author = AuthorSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(source='author', queryset=Author.objects.all(), write_only=True, required=False, allow_null=True)

    class Meta:
        model = Book
        fields = ['id', 'name', 'author', 'author_id', 'category', 'category_id', 'image']


class IssueSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(source='book', queryset=Book.objects.all(), write_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Issue
        fields = ['id', 'book', 'book_id', 'issued', 'issued_at', 'returned', 'return_date', 'created_at', 'status']
        read_only_fields = ['issued', 'issued_at', 'returned', 'return_date', 'created_at']

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError('Authentication required')
        student = getattr(user, 'student', None)
        if student is None:
            raise serializers.ValidationError('Only students can request issues')
        book = attrs['book']
        if Issue.objects.filter(student=student, book=book, returned=False).exists():
            raise serializers.ValidationError('You already have an active request/issue for this book')
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        student = user.student
        book = validated_data['book']
        issue = Issue.objects.create(student=student, book=book)
        return issue


class FineSerializer(serializers.ModelSerializer):
    issue = IssueSerializer(read_only=True)

    class Meta:
        model = Fine
        fields = ['id', 'issue', 'amount', 'paid', 'datetime_of_payment']