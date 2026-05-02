from django.http import JsonResponse
from myapp.models import Order
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Book, Cart, CartItem, Wishlist
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.db.models import Q
from .models import Book

def book_list(request):
    books = Book.objects.all()
    return render(request, 'myapp/book_list.html', {'books': books})

@login_required
def add_to_cart(request, pk):
    book = get_object_or_404(Book, pk=pk)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total = sum(item.total_price() for item in items)
    return render(request, 'myapp/cart.html', {'items': items, 'total': total})

@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    cart_item.delete()
    return redirect('view_cart')

@login_required
def add_to_wishlist(request, pk):
    book = get_object_or_404(Book, pk=pk)
    Wishlist.objects.get_or_create(user=request.user, book=book)
    return redirect('view_wishlist')

@login_required
def view_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'myapp/wishlist.html', {'items': wishlist_items})

@login_required
def remove_from_wishlist(request, pk):
    wishlist_item = get_object_or_404(Wishlist, pk=pk, user=request.user)
    wishlist_item.delete()
    return redirect('view_wishlist')

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.view_count += 1 # บวกยอดวิว
    book.save()
    return render(request, 'myapp/book_detail.html', {'book': book})

@staff_member_required # เฉพาะแอดมินหรือทีมงานเท่านั้นที่เข้าได้
def admin_dashboard(request):
    total_sales = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_orders = Order.objects.count()
    total_views = Book.objects.aggregate(Sum('view_count'))['view_count__sum'] or 0
    top_books = Book.objects.order_by('-view_count')[:5] # หนังสือที่ยอดวิวสูงสุด 5 อันดับ
    
    # ดึงยอดขายแยกตามหมวดหมู่
    from .models import OrderItem
    category_data = OrderItem.objects.values('book__category__name').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')
    
    category_labels = [item['book__category__name'] or 'Uncategorized' for item in category_data]
    category_values = [item['total_sold'] for item in category_data]
    
    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'total_views': total_views,
        'top_books': top_books,
        'category_labels': category_labels,
        'category_values': category_values,
    }
    return render(request, 'myapp/dashboard.html', context)

def complex_search_api(request):
    query_text = request.GET.get('q', '')
    
    if query_text:
        # 1. กำหนดความสำคัญ (Weight)
        vector = SearchVector('title', weight='A') + SearchVector('description', weight='B')
        query = SearchQuery(query_text)
        
        # 2. ค้นหาและจัดอันดับ
        results = Book.objects.annotate(
            rank=SearchRank(vector, query),
            similarity=TrigramSimilarity('title', query_text)
        ).filter(
            Q(rank__gte=0.1) | Q(similarity__gt=0.2)
        ).order_by('-rank', '-similarity')
    else:
        results = Book.objects.none() # ถ้าไม่มีคำค้นหา ไม่ต้องโชว์อะไร

    # เปลี่ยนจาก JsonResponse เป็น render
    return render(request, 'myapp/search_results.html', {
        'results': results,
        'query': query_text
    })
