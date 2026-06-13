#? Store models: points of sale, stock by store, store staff / Модели магазинов: точки продаж, остатки по магазинам, сотрудники магазина
from django.conf import settings
from django.db import models


class Store(models.Model):
    #* MegaShop branch/outlet. Address, contacts, status. / Филиал/точка продаж MegaShop. Адрес, контакты, статус.
    name = models.CharField('Name', max_length=200)
    slug = models.SlugField('URL', max_length=250, unique=True, blank=True)
    address = models.TextField('Address')
    phone = models.CharField('Phone', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    city = models.CharField('City', max_length=100)
    work_hours = models.CharField('Working hours', max_length=200, blank=True, default='09:00–21:00')
    is_active = models.BooleanField('Active', default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Store'
        verbose_name_plural = 'Stores'
        ordering = ['city', 'name']

    def save(self, *args, **kwargs):
        from django.utils.text import slugify
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.city})'


class StoreStaff(models.Model):
    #* Link employee to store. One employee can work in multiple stores. / Привязка сотрудника к магазину. Один сотрудник может работать в нескольких магазинах.
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('senior', 'Senior seller'),
        ('seller', 'Seller'),
    ]
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name='staff',
        verbose_name='Store',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='store_workships', verbose_name='Employee',
    )
    role = models.CharField('Role', max_length=20, choices=ROLE_CHOICES, default='seller')
    is_active = models.BooleanField('Active', default=True)

    class Meta:
        verbose_name = 'Store employee'
        verbose_name_plural = 'Store employees'
        unique_together = ['store', 'user']

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} — {self.store.name}'


class StoreProduct(models.Model):
    #* Stock of a specific product in a specific store / Остатки конкретного товара в конкретном магазине
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name='products',
        verbose_name='Store',
    )
    product = models.ForeignKey(
        'catalog.Product', on_delete=models.CASCADE,
        related_name='store_stocks', verbose_name='Product',
    )
    stock = models.PositiveIntegerField('Stock', default=0)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Store stock'
        verbose_name_plural = 'Stock by stores'
        unique_together = ['store', 'product']

    def __str__(self):
        return f'{self.product.name} — {self.store.name}: {self.stock} pcs.'
