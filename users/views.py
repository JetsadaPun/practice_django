from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import UserRegisterForm
from .models import Profile


"""
จัดการการสมัครสมาชิกใหม่ โดยสร้างข้อมูลใน User (auth) 
และสร้าง Profile คู่กันโดยอัตโนมัติ
"""
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # บันทึก User หลัก
            user = form.save()
            
            # ดึงข้อมูลที่เพิ่มเข้ามาในฟอร์มเพื่อบันทึกลง Profile
            full_name = form.cleaned_data.get('full_name')
            phone = form.cleaned_data.get('phone')
            
            # สร้าง Profile และเชื่อมกับ User
            Profile.objects.create(user=user, full_name=full_name, phone=phone)
            
            messages.success(request, f'Account created for {user.username}!')
            login(request, user)
            return redirect('book_list')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})
