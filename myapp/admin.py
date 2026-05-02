from django.contrib import admin
from .models import Book, Category, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('book', 'quantity', 'price')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'price', 'category', 'stock', 'view_count')
    list_filter = ('category',)
    search_fields = ('title', 'author')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'total_quantity', 'created_at') # แสดงหัวข้อในหน้าตาราง
    list_filter = ('created_at', 'user') # ตัวกรองด้านข้าง
    inlines = [OrderItemInline]