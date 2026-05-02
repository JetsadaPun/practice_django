from django.http import HttpResponseForbidden
from django.core.cache import cache # นำเข้าระบบ Cache
from django.http import HttpResponse 
import time

class SimpleIPFirewallMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_ips = ['127.0.0.1', '192.168.2.200', '::1']

    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        
        # 1. เช็คใน "ความจำ" (Cache) ก่อนว่า IP นี้เคยผ่านด่านมาหรือยัง
        is_authorized = cache.get(f'auth_ip_{ip}')
        
        if is_authorized:
            # ถ้าเคยผ่านแล้ว (Stateful) ให้ผ่านไปได้เลย ไม่ต้องเช็คลิสต์
            return self.get_response(request)

        # 2. ถ้ายังไม่มีในความจำ (หรือความจำเสื่อม/หมดเวลา) ให้เช็คตามปกติ
        if ip in self.allowed_ips:
            # ถ้าเช็คผ่าน ให้ "จดจำ" ไว้ใน Cache เป็นเวลา 300 วินาที (5 นาที)
            cache.set(f'auth_ip_{ip}', True, 300)
            return self.get_response(request)
        
        # 3. ถ้าไม่อยู่ในลิสต์ บล็อกเหมือนเดิม
        return HttpResponseForbidden("Access Denied: Your IP is not authorized.")

class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.limit = 5          # จำนวนครั้งสูงสุดที่ยอมให้เข้า
        self.duration = 60      # ภายในกี่วินาที (ในที่นี้คือ 1 นาที)
    def __call__(self, request):
        ip = request.META.get('REMOTE_ADDR')
        cache_key = f'ratelimit_{ip}'
        
        # 1. ดึงจำนวนครั้งที่ IP นี้เคยกดเข้ามาจาก Cache
        request_count = cache.get(cache_key, 0)
        # 2. ถ้ากดเกินจำนวนที่กำหนด (Limit)
        if request_count >= self.limit:
            return HttpResponse("Too Many Requests: ใจเย็นๆ ครับ คุณกดเร็วเกินไป!", status=429)
        # 3. ถ้ายังไม่เกิน ให้เพิ่มจำนวนนับไปอีก 1
        cache.set(cache_key, request_count + 1, self.duration)
        return self.get_response(request)