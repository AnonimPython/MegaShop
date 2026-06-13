from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from loguru import logger
from .models import Review
from apps.catalog.models import Product


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_slug = review.product.slug
    logger.info('Review deleted: user={}, product={}', request.user.username, review.product.name)
    review.delete()
    return redirect('catalog:product_detail', slug=product_slug)
