"""
Model for product reviews.

A user can leave one review per product (unique_together).
Reviews must be moderated before publication.
"""
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Review(models.Model):
    """
    User review of a product.

    Fields:
    - product — the product being reviewed
    - user — the review author (linked to User)
    - text — review content
    - rating — score from 1 to 5
    - is_moderated — moderation flag (hidden until approved)

    Constraints:
    - One user can leave exactly one review per product
      (unique_together = ['product', 'user'])
    - Review is hidden until is_moderated=True
    """
    product = models.ForeignKey(
        'catalog.Product', on_delete=models.CASCADE,
        related_name='reviews', verbose_name='Product',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='reviews', verbose_name='User',
    )
    pros = models.TextField('What I liked', blank=True, help_text='What did you like about the product?')
    cons = models.TextField('What I did not like', blank=True, help_text='What could be improved?')
    text = models.TextField('Overall review', blank=True)
    rating = models.PositiveSmallIntegerField(
        'Rating', default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5 stars',
    )
    is_moderated = models.BooleanField(
        'Moderated', default=False,
        help_text='True — review is published, False — awaiting moderation',
    )
    created = models.DateTimeField('Created', auto_now_add=True)
    updated = models.DateTimeField('Updated', auto_now=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created']
        unique_together = ['product', 'user']

    def __str__(self):
        return f'{self.user} — {self.product} ({self.rating}★)'
