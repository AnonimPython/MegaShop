#? Order: customer data + store + statuses + payment. OrderItem: products at purchase time / Заказ: данные клиента + магазин + статусы + оплата. OrderItem: товары на момент покупки
from django.conf import settings
from django.db import models


class Order(models.Model):
    #* Statuses: new → confirmed → processing → shipped → delivered | cancelled / Статусы: new → confirmed → processing → shipped → delivered | cancelled
    STATUS_CHOICES = [
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('card', 'Card online'),
        ('cash', 'Cash on delivery'),
        ('card_on_delivery', 'Card on delivery'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        related_name='orders', verbose_name='User',
        blank=True, null=True,
    )
    store = models.ForeignKey(
        'stores.Store', on_delete=models.SET_NULL,
        related_name='orders', verbose_name='Store',
        blank=True, null=True,
    )
    DELIVERY_CHOICES = [
        ('pickup', 'Pickup from store'),
        ('delivery', 'Home delivery'),
    ]
    first_name = models.CharField('First name', max_length=100)
    last_name = models.CharField('Last name', max_length=100)
    email = models.EmailField('Email')
    phone = models.CharField('Phone', max_length=20)
    delivery_type = models.CharField('Delivery type', max_length=20, choices=DELIVERY_CHOICES, default='pickup')
    pickup_store = models.ForeignKey(
        'stores.Store', on_delete=models.SET_NULL,
        related_name='pickup_orders', verbose_name='Pickup store',
        blank=True, null=True,
    )
    address = models.CharField('Address', max_length=300, blank=True)
    city = models.CharField('City', max_length=100, blank=True)
    postal_code = models.CharField('Postal code', max_length=20, blank=True)
    delivery_floor = models.CharField('Floor', max_length=20, blank=True)
    delivery_apartment = models.CharField('Apartment / Office', max_length=50, blank=True)
    backup_phone = models.CharField('Backup phone', max_length=20, blank=True, help_text='Alternative contact number if primary is unreachable')
    comment = models.TextField('Comment', blank=True)
    payment_method = models.CharField('Payment method', max_length=20, choices=PAYMENT_CHOICES, default='card')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='new')
    paid = models.BooleanField('Paid', default=False)
    total_cost = models.DecimalField('Total cost', max_digits=12, decimal_places=2, default=0)
    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created']

    def __str__(self):
        return f'Order #{self.id}'


class OrderItem(models.Model):
    #* Save name and price at order time (product may change later) / Сохраняем название и цену на момент заказа (товар может измениться потом)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items',
        verbose_name='Order',
    )
    product = models.ForeignKey(
        'catalog.Product', on_delete=models.SET_NULL,
        related_name='order_items', verbose_name='Product',
        blank=True, null=True,
    )
    product_name = models.CharField('Product name', max_length=300)
    product_price = models.DecimalField('Price', max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField('Quantity', default=1)

    class Meta:
        verbose_name = 'Order item'
        verbose_name_plural = 'Order items'

    def get_cost(self):
        return self.product_price * self.quantity

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'
