from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from loguru import logger
from .models import Order, OrderItem
from .forms import OrderCreateForm
from .tasks import send_order_confirmation
from apps.cart.cart import Cart
from apps.stores.models import Store


def order_create(request):
    cart = Cart(request)
    if not cart:
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user

            delivery_type = form.cleaned_data.get('delivery_type', 'pickup')
            if delivery_type == 'pickup':
                pickup_store = form.cleaned_data.get('pickup_store')
                if pickup_store:
                    order.store = pickup_store
                    order.pickup_store = pickup_store
            else:
                store_id = request.session.get('store_id')
                if store_id:
                    try:
                        order.store = Store.objects.get(id=store_id)
                    except Store.DoesNotExist:
                        pass

            order.total_cost = cart.get_total_price()
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    product_name=item['product'].name,
                    product_price=item['price'],
                    quantity=item['quantity'],
                )

            logger.info('Order created: #{} by {} (delivery: {}, total: £{})',
                         order.id, order.email, delivery_type, order.total_cost)
            cart.clear()
            send_order_confirmation.delay(order.id, order.email)
            return redirect('orders:order_detail', order_id=order.id)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'phone': request.user.phone,
            }
        current_store_id = request.session.get('store_id')
        if current_store_id:
            try:
                store = Store.objects.get(id=current_store_id)
                initial['pickup_store'] = store
            except Store.DoesNotExist:
                pass
        form = OrderCreateForm(initial=initial)

    return render(request, 'orders/order_create.html', {
        'form': form,
        'cart': cart,
        'stores': Store.objects.filter(is_active=True),
    })


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_list.html', {'orders': orders})
