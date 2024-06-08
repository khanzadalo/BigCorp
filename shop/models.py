import random
import string

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def rand_slug():
    """Generate random slug consisting of lowercase letters and digits.
    Returns: 
        str: Random slug.
        
    Example:
        >>> rand_slug()
        'yj3j'
    """
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(3))


class Category(models.Model):
    """
    Represents a category in the shop.
    """
    name = models.CharField("Категория", max_length=250, db_index=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)
    slug = models.SlugField('URL', max_length=250, db_index=True, unique=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)


    class Meta:
        unique_together = ('slug', 'parent')
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
    

    def __str__(self):
        """
        Returns a string representation of the Category object.

        This method constructs a string representation of the Category object by traversing
        up the parent hierarchy and joining the names of each parent and the current object
        with ' -> '. The resulting string is returned.
        """
        full_path = [self.name]
        k = self.parent
        
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])
    

    def save(self, *args, **kwargs):
        """
        Save the current instance to the database.
        """
        if not self.slug:
            self.slug = slugify(rand_slug() + '-pickBetter' + self.name)
        super(Category, self).save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('shop:category-list', args=[str(self.slug)])

class Product(models.Model):
    """
    Represents a product in the shop.
    """

    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE, related_name='products')
    title = models.CharField("Название", max_length=250, db_index=True)
    slug = models.SlugField('URL', max_length=250, db_index=True)
    description = models.TextField("Описание", blank=True)
    brand = models.CharField("Бренд", max_length=250)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2, default=99.99)
    image = models.ImageField("Изображение", upload_to='products/products/%Y/%m/%d')
    available = models.BooleanField("Доступен", default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)


    class Meta:
        ordering = ['title']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        index_together = [
            ['id', 'slug']
        ]

    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('shop:product-detail', args=[str(self.slug)])

class ProductManager(models.Manager):
    def get_queryset(self):
        """
        Returns a queryset of available products.
 
        This method overrides the get_queryset method of the ProductManager class. It
        calls the get_queryset method of the superclass and filters the resulting
        queryset to only include products that are marked as available.

        Returns:
            QuerySet: A queryset of available products.
        """
        return super().get_queryset().filter(available=True)


class ProductProxy(Product):

    objects = ProductManager()

    class Meta:
        proxy = True