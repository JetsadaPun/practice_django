from django.test import TestCase

from django.urls import reverse
from django.contrib.auth.models import User

class LoginTests(TestCase):

    def setUp(self):
        # สร้าง User จำลองขึ้นมาในฐานข้อมูลสำหรับการทดสอบ
        self.username = 'testuser'
        self.password = 'password123'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        self.login_url = reverse('login')

    def test_login_page_loads(self):
        """ทดสอบกรณี: หน้า Login เข้าถึงได้ปกติ (GET)"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_success(self):
        """ทดสอบกรณี: กรอก Username และ Password ถูกต้อง"""
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password
        })
        # เช็คว่าระบบ Redirect (302) ไปหน้าหลักสำเร็จหรือไม่
        self.assertEqual(response.status_code, 302)
        # เช็คว่าหลังล็อกอินแล้ว ผู้ใช้ถูกระบุตัวตนถูกต้องหรือไม่
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_wrong_password(self):
        """ทดสอบกรณี: รหัสผ่านผิด"""
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': 'wrongpassword'
        })
        # ระบบไม่ควร Redirect (ยังอยู่ที่หน้าเดิม)
        self.assertEqual(response.status_code, 200)
        # ผู้ใช้ต้องไม่ล็อกอิน
        self.assertFalse('_auth_user_id' in self.client.session)
