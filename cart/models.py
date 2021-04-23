from django.contrib.auth import get_user_model
from django.db import models

from general.models import Post

User = get_user_model()


class CartManager(models.Manager):
    def get_existing_or_new(self, request):
        created = False
        cart_id = request.session.get('cart_id')
        if self.get_queryset().filter(id=cart_id, used=False).count() == 1:
            obj = self.model.objects.get(id=cart_id)
        elif self.get_queryset().filter(user=request.user, used=False).count() == 1:
            obj = self.model.objects.get(user=request.user, used=False)
            request.session['cart_id'] = obj.id
        else:
            obj = self.model.objects.create(user=request.user)
            request.session['cart_id'] = obj.id
            created = True
        return obj, created


class Cart(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = CartManager()

    def __str__(self):
        return str(self.id)

    @property
    def total(self):
        total = 0
        for item in self.post.all():
            total += int(item.quantity) * float(item.post.price)
        return total

    @property
    def tax_total(self):
        total = 0
        for item in self.post.all():
            total += int(item.quantity) * float(item.post.price) * \
                float(item.post.tax) / 100
        return total

    @property
    def total_cart_post(self):
        return sum(item.quantity for item in self.post.all())


class CartItem(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="post")

    class Meta:
        unique_together = (
            ('post', 'cart')
        )