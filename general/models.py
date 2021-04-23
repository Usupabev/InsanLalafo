from django.db import models

from account.models import MyUser


class Category(models.Model):
    slug = models.SlugField(max_length=100, primary_key=True)
    name = models.CharField(max_length=150, unique=True)
    parent = models.ForeignKey('self', related_name='children', null=True, blank=True, on_delete=models.CASCADE)
    def __str__(self):
        if self.parent:
            return f'{self.parent} --> {self.name}'
        else:
            return self.name

    @property
    def get_children(self):
        if self.children:
            return self.children.all()
        else:
            return False



class Post(models.Model):
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=20, decimal_places=2)
    image = models.ImageField(upload_to='posts', default='default.jpg')
    created = models.DateTimeField(auto_now_add=True)
    adress = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('-created', )

# class PostImage(models.Model):
#     image = models.ImageField(upload_to='images', blank=True, null=True)
#     post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    author = models.ForeignKey(MyUser, on_delete=models.DO_NOTHING, related_name='comments')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment

    class Meta:
        ordering = ('created', )


class Like(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    like = models.BooleanField(default=False)

