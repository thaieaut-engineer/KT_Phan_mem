from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

try:
    driver.get("http://127.0.0.1:5000")

    print("Tiêu đề website:", driver.title)

    assert "PetShop" in driver.title

finally:
    driver.quit()