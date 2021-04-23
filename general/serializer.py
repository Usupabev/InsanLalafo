from rest_framework import serializers
from .models import Post, Comment, Category, Like


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class PostSerializer(serializers.ModelSerializer):
    created = serializers.DateTimeField(format="%d %B %Y %H:%M",
                                        read_only=True)
    author = serializers.ReadOnlyField(source='author.email')

    class Meta:
        model = Post
        fields = ('id', 'title', 'description', 'image',
                  'created', 'author', 'price', 'category', 'adress')

    def create(self, validated_data):
        request = self.context.get('request')
        images_data = request.FILES
        author = request.user
        post = Post.objects.create(author=author, **validated_data)
        return post

    def update(self, instance, validated_data):
        request = self.context.get('request')
        for key, value in validated_data.items():
            setattr(instance, key, value)
        return instance


    def to_representation(self, instance):
        representation = super(PostSerializer, self).to_representation(instance)
        representation['category'] = CategorySerializer(instance.category).data
        representation['comments'] = CommentSerializer(instance.comments.all(), many=True).data
        representation['like'] = len(LikeSerializer(instance.likes.filter(like=True), many=True, context=self.context).data)
        return representation


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.email')

    class Meta:
        model = Comment
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        author = request.user
        comment = Comment.objects.create(author=author, **validated_data)
        return comment

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

    def get_fields(self):
        action = self.context.get('action')
        fields = super().get_fields()
        if action == 'create':
            fields.pop('user')
            fields.pop('like')
        return fields

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        post = validated_data.get('post')
        like = Like.objects.get_or_create(user=user, post=post)[0]
        like.like = True if like.like is False else False
        like.save()
        return like


class ParsSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    photo = serializers.CharField(max_length=255)
    price = serializers.CharField(max_length=100)