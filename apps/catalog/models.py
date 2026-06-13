#? Categories (with nesting support), products, image gallery, views, exchange rates / Категории (с поддержкой вложенности), товары, галерея изображений, просмотры, курсы валют
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from decimal import Decimal


class Category(models.Model):
    #* Hierarchical category: parent / subcategory / Иерархическая категория: parent = родительская, children = подкатегории
    name = models.CharField('Name', max_length=200)
    slug = models.SlugField('URL', max_length=250, unique=True, blank=True)
    description = models.TextField('Description', blank=True)
    image = models.ImageField('Image', upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name='children',
        verbose_name='Parent category', blank=True, null=True,
    )
    is_active = models.BooleanField('Active', default=True)
    sort_order = models.IntegerField('Sort order', default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['sort_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_descendants(self, include_self=False):
        #* Simple recursive descendant lookup (no mptt)
        result = []
        if include_self:
            result.append(self)
        for child in self.children.all():
            result.append(child)
            result.extend(child.get_descendants())
        return result


class Product(models.Model):
    #* Main product model. Price, stock, JSON specs, new/popular flags / Основная модель товара. Цена, остаток, характеристики JSON, флаги новинки/популярности
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products',
        verbose_name='Category',
    )
    name = models.CharField('Name', max_length=300)
    slug = models.SlugField('URL', max_length=350, unique=True, blank=True)
    description = models.TextField('Description', blank=True)
    specifications = models.JSONField(
        'Specifications', blank=True, null=True,
        help_text='{"Processor": "Intel i7", "RAM": "16 GB"}',
    )
    price = models.DecimalField('Price', max_digits=12, decimal_places=2)
    old_price = models.DecimalField(
        'Old price', max_digits=12, decimal_places=2, blank=True, null=True,
    )
    image = models.ImageField('Main image', upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField('Stock', default=0)
    is_available = models.BooleanField('In stock', default=True)
    is_popular = models.BooleanField('Popular', default=False)
    is_new = models.BooleanField('New', default=False)
    warranty = models.CharField('Warranty', max_length=100, blank=True)
    sort_order = models.IntegerField('Sort order', default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-sort_order', '-created']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_available', 'is_popular']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[self.slug])

    @property
    def discount_percent(self):
        #* Returns discount percentage if old_price is set / Возвращает процент скидки, если есть old_price
        if self.old_price and self.old_price > self.price:
            return int((1 - self.price / self.old_price) * 100)
        return 0


class ProductImage(models.Model):
    #* Additional product photos (gallery on detail page) / Дополнительные фото товара (галерея на детальной странице)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='images',
        verbose_name='Product',
    )
    image = models.ImageField('Image', upload_to='products/gallery/')
    sort_order = models.IntegerField('Order', default=0)

    class Meta:
        verbose_name = 'Product image'
        verbose_name_plural = 'Product images'
        ordering = ['sort_order']


class ProductView(models.Model):
    #* Logging views for popularity sorting / Логирование просмотров для сортировки по популярности
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField()
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'View'
        verbose_name_plural = 'Views'


class CategorySpecField(models.Model):
    #? Custom specification fields per category / Пользовательские поля характеристик для каждой категории
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('boolean', 'Yes / No'),
    ]
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='spec_fields',
        verbose_name='Category',
    )
    field_name = models.CharField('Field name', max_length=100, help_text='e.g. Screen size, RAM, Joysticks')
    field_type = models.CharField('Field type', max_length=20, choices=FIELD_TYPES, default='text')
    sort_order = models.IntegerField('Sort order', default=0)

    class Meta:
        verbose_name = 'Category spec field'
        verbose_name_plural = 'Category spec fields'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f'{self.category.name} → {self.field_name}'


class ExchangeRate(models.Model):
    #* Exchange rates relative to USD (base currency) / Курсы валют относительно USD (базовая валюта)
    currency = models.CharField('Currency code', max_length=3, unique=True, help_text='e.g. EUR, GBP')
    rate = models.DecimalField('Rate to USD', max_digits=10, decimal_places=6, help_text='How many units of this currency per 1 USD')
    symbol = models.CharField('Symbol', max_length=5, help_text='e.g. €, £')
    is_active = models.BooleanField('Active', default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Exchange rate'
        verbose_name_plural = 'Exchange rates'

    def __str__(self):
        return f'{self.currency} ({self.symbol}) = {self.rate} USD'

    @classmethod
    def get_rates_dict(cls):
        #* Returns {code: {rate: Decimal, symbol: str}} for active rates / Возвращает {code: {rate: Decimal, symbol: str}} для активных курсов
        return {
            r.currency: {'rate': r.rate, 'symbol': r.symbol}
            for r in cls.objects.filter(is_active=True)
        }

    @classmethod
    def convert(cls, amount_usd, target_currency):
        #* Convert USD amount to target currency / Конвертирует сумму из USD в целевую валюту
        try:
            rate_obj = cls.objects.get(currency=target_currency.upper(), is_active=True)
            return amount_usd * rate_obj.rate
        except cls.DoesNotExist:
            return amount_usd
