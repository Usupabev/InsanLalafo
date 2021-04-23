from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, viewsets, status, mixins
from .models import Post, Category, Comment, Like
from .parsing import parsing
from .permissions import IsAuthorPermission
from .serializer import PostSerializer, CategorySerializer, CommentSerializer, LikeSerializer, ParsSerializer
from rest_framework.response import Response
from rest_framework.views import APIView

class PostPaginatonClass(PageNumberPagination):
    page_size = 4

class CommentPagination(PageNumberPagination):
    page_size = 1



class PermissionMixin:
    def get_permissions(self):
        if self.action == 'create':
            permissions = [IsAuthenticated, ]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permissions = [IsAuthorPermission, ]
        else:
            permissions = []
        return [permission() for permission in permissions]


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny, ]


class PostViewSet(PermissionMixin, viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostPaginatonClass
    permission_classes = [IsAuthenticated, ]

    @action(detail=False, methods=['GET'])
    def search(self, request, pk=None):
        q = request.query_params.get('q')
        queryset = self.get_queryset()
        queryset = queryset.filter(Q(title__icontains=q) | Q(description__icontains=q))
        serializer = PostSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def sort(self, request):
        filter = request.query_params.get('filter')
        if filter == 'A-Z':
            queryset = self.get_queryset().order_by('title')
        elif filter == 'Z-A':
            queryset = self.get_queryset().order_by('-title')
        elif filter == 'replies':
            maximum = 0
            for problem in self.get_queryset():
                if maximum < problem.replies.count():
                    maximum = problem.replies.count()
                    queryset = self.get_queryset().filter(id=problem.id)
        else:
            queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(PermissionMixin, viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    pagination_class = CommentPagination
    serializer_class = CommentSerializer


class LikeViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated, ]

    def get_serializer_context(self):
        return {'request': self.request, 'action': self.action}

class ParsingIstoreView(APIView):
    def get(self, request):
        dict_ = parsing()
        serializer = ParsSerializer(instance=dict_, many=True)
        return Response(serializer.data)