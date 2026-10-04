import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestLogin(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)

    def test_login_valid_account(self):
        driver = self.driver

        # 1. Mở trang đăng nhập
        driver.get("http://127.0.0.1:5000/auth/login")

        # 2. Nhập email
        username = self.wait.until(
            EC.visibility_of_element_located((By.NAME, "email"))
        )
        username.clear()
        username.send_keys("qthai4028@gmail.com")

        # 3. Nhập mật khẩu
        password = driver.find_element(By.NAME, "password")
        password.clear()
        password.send_keys("123456")

        # 4. Thực hiện Đăng nhập (Thử lần lượt các phương pháp)
        try:
            # Phương pháp 1: Bấm phím ENTER ngay tại ô password (Rất ổn định)
            password.send_keys(Keys.ENTER)
        except Exception:
            # Phương pháp 2: Tìm nút submit bằng XPATH bao quát hơn
            submit_btn = self.wait.until(
                EC.presence_of_element_located((
                    By.XPATH, 
                    "//button[@type='submit'] | //input[@type='submit'] | //button[contains(text(),'Đăng nhập')]"
                ))
            )
            driver.execute_script("arguments[0].click();", submit_btn)

        # 5. Kiểm tra kết quả sau khi đăng nhập
        self.wait.until(
            EC.url_changes("http://127.0.0.1:5000/auth/login")
        )

        self.assertNotIn(
            "/login",
            driver.current_url
        )

    def tearDown(self):
        self.driver.quit()


if __name__ == "__main__":
    unittest.main(verbosity=2)