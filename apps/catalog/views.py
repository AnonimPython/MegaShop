#? Product list, detail page, search, sort, category filter / Список товаров, детальная страница, поиск, сортировка, фильтрация по категории
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Avg, Q
from django.contrib import messages
from loguru import logger
from .models import Category, Product
from apps.reviews.models import Review
from apps.reviews.forms import ReviewForm


def product_list(request, category_slug=None):
    #* Filter by category, search by name, sorting / Фильтрация по категории, поиск по названию, сортировка
    category = None
    categories = Category.objects.filter(is_active=True, parent=None)
    products = Product.objects.filter(is_available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category__in=category.get_descendants(include_self=True))

    search_query = request.GET.get('q', '')
    if search_query:
        products = products.filter(name__icontains=search_query)

    sort = request.GET.get('sort', '-created')
    allowed_sorts = {
        'price': 'price',
        '-price': '-price',
        'name': 'name',
        '-name': '-name',
        'created': '-created',
        'popular': '-view_count',
    }
    if sort in allowed_sorts:
        if sort == 'popular':
            products = products.annotate(view_count=Count('views')).order_by('-view_count')
        else:
            products = products.order_by(allowed_sorts[sort])

    logger.debug('Catalog list: category={}, search={}, sort={}', category_slug, search_query, sort)
    return render(request, 'catalog/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'search_query': search_query,
    })


def product_detail(request, slug):
    #* Detail page: description, specs, reviews, related products / Детальная страница: описание, характеристики, отзывы, похожие товары
    product = get_object_or_404(Product, slug=slug, is_available=True)
    # Show moderated reviews + current user's own unmoderated review
    if request.user.is_authenticated:
        reviews = Review.objects.filter(
            Q(is_moderated=True) | Q(user=request.user),
            product=product,
        )
    else:
        reviews = Review.objects.filter(product=product, is_moderated=True)
    avg_rating = Review.objects.filter(product=product, is_moderated=True).aggregate(
        Avg('rating')
    )['rating__avg'] or 0

    if request.method == 'POST' and request.user.is_authenticated:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review, created = Review.objects.update_or_create(
                product=product, user=request.user,
                defaults={
                    'pros': review_form.cleaned_data['pros'],
                    'cons': review_form.cleaned_data['cons'],
                    'text': review_form.cleaned_data['text'],
                    'rating': review_form.cleaned_data['rating'],
                    'is_moderated': False,
                },
            )
            logger.info('Review {}: user={}, product={}, rating={}',
                         'created' if created else 'updated',
                         request.user.username, product.name,
                         review_form.cleaned_data['rating'])
            if created:
                messages.success(request, 'Review submitted for moderation.')
            else:
                messages.success(request, 'Review updated and re-submitted for moderation.')
            review_form = ReviewForm(instance=review)
    elif request.user.is_authenticated:
        existing_review = Review.objects.filter(product=product, user=request.user).first()
        review_form = ReviewForm(instance=existing_review) if existing_review else ReviewForm()
    else:
        review_form = None

    related_products = Product.objects.filter(
        category=product.category, is_available=True
    ).exclude(id=product.id)[:4]

    return render(request, 'catalog/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_form': review_form,
        'related_products': related_products,
    })
