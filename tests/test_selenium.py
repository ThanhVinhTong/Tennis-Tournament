import unittest, time, os
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from flask import Flask
from flask_testing import TestCase
from app import create_app, db
from app.models import User

class TestBase(TestCase):
    def create_app(self):
        """Create a Flask app for testing"""
        app = create_app()
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',  # Use in-memory database
            WTF_CSRF_ENABLED=False,
            SERVER_NAME='http://127.0.0.1:5001/'
        )
        return app
    
    @contextmanager
    def get_driver(self):
        """Context manager for webdriver"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("enable-automation")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Edge(options=options)
        try:
            yield driver
        finally:
            driver.quit()

class TestWebApp(TestBase):
    def setUp(self):
        """Set up test database"""
        # Create test user
        self.test_user = User(username='testuser123', email='test123@example.com')
        self.test_user.set_password('Test123!')
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        """Clean up test user after each test"""
        # Remove only the test user
        test_user = User.query.filter_by(username='testuser123').first()
        if test_user:
            db.session.delete(test_user)
            db.session.commit()
        db.session.remove()

    def test_homepage_loads(self):
        """Test if homepage loads with navbar and footer"""
        try:
            with self.get_driver() as driver:
                driver.get("http://127.0.0.1:5001/")
                
                try:
                    # Check navbar exists
                    navbar = driver.find_element(By.CLASS_NAME, "navbar")
                    self.assertTrue(navbar.is_displayed())
                    print("PASSED: Navbar check passed")
                except:
                    print("FAIL: Navbar check failed")
                    raise
                
                try:
                    # Check footer exists
                    footer = driver.find_element(By.TAG_NAME, "footer")
                    self.assertTrue(footer.is_displayed())
                    print("PASSED: Footer check passed")
                except:
                    print("FAIL: Footer check failed")
                    raise
            print("PASSED: Homepage load test passed")
        except Exception as e:
            print("FAIL: Homepage load test failed")
            raise

    def test_user_registration(self):
        try:
            with self.get_driver() as driver:
                try:
                    # Start at registration page
                    driver.get("http://127.0.0.1:5001/auth/register")
                    
                    # Fill in registration form
                    driver.find_element(By.ID, "username").send_keys("newuser")
                    driver.find_element(By.ID, "email").send_keys("newuser@example.com")
                    driver.find_element(By.ID, "password").send_keys("NewPass123!")
                    driver.find_element(By.ID, "country").send_keys("AUSTRALIA")
                    print("PASSED: Registration form fill passed")
                except:
                    print("FAIL: Registration form fill failed")
                    raise
                
                try:
                    # Submit form
                    driver.find_element(By.CLASS_NAME, "btn.btn-primary").click()
                    print("PASSED: Registration form submission passed")
                except:
                    print("FAIL: Registration form submission failed")
                    raise
                
                try:
                    # Check redirect
                    time.sleep(2)  # Wait for redirect
                    self.assertIn("login", driver.current_url)
                    print("PASSED: Registration redirect check passed")
                except:
                    print("FAIL: Registration redirect check failed")
                    raise
            print("PASSED: User registration test passed")
        except Exception as e:
            print("FAIL: User registration test failed")
            raise

    def test_login_fail(self):
        """Test login with invalid credentials"""
        try:
            with self.get_driver() as driver:
                try:
                    # Start at login page
                    driver.get("http://127.0.0.1:5001/auth/login")
                    
                    # Attempt login with wrong credentials
                    driver.find_element(By.ID, "username").send_keys("wronguser")
                    driver.find_element(By.ID, "password").send_keys("wrongpass")
                    print("PASSED: Login form fill passed")
                except:
                    print("FAIL: Login form fill failed")
                    raise
                
                try:
                    # Submit form
                    driver.find_element(By.CLASS_NAME, "btn.btn-primary").click()
                    print("PASSED: Login form submission passed")
                except:
                    print("FAIL: Login form submission failed")
                    raise
                
                try:
                    # Check if still on login page
                    time.sleep(2)  # Wait for page to process
                    self.assertIn("login", driver.current_url)
                    
                    # Verify login form is still present
                    self.assertTrue(driver.find_element(By.ID, "username").is_displayed())
                    self.assertTrue(driver.find_element(By.ID, "password").is_displayed())
                    print("PASSED: Failed login state check passed")
                except:
                    print("FAIL: Failed login state check failed")
                    raise
            print("PASSED: Login failure test passed")
        except Exception as e:
            print("FAIL: Login failure test failed")
            raise

    def test_login_success(self):
        """Test login with valid credentials"""
        try:
            with self.get_driver() as driver:
                # Go to login page
                driver.get("http://127.0.0.1:5001/auth/login")

                # Fill out login form
                try:
                    driver.find_element(By.NAME, "username").send_keys("tester")
                    driver.find_element(By.NAME, "password").send_keys("123456")
                    print("PASSED: Login form fill passed")
                except Exception as e:
                    print("FAIL: Login form fill failed")
                    raise

                # Submit the form
                try:
                    driver.find_element(By.XPATH, "//button[text()='Log In']").click()
                    print("PASSED: Login form submission passed")
                except Exception as e:
                    print("FAIL: Login form submission failed")
                    raise

                # Wait for URL to change from /login
                try:
                    WebDriverWait(driver, 5).until_not(
                        EC.url_contains("/login")
                    )
                    current_url = driver.current_url
                    print("Redirected URL:", current_url)

                    # Custom logic: check for something meaningful on the home page
                    self.assertIn("home", current_url)
                    print("PASSED: Redirect to \'home\' page confirmed")
                except Exception as e:
                    print("FAIL: Login may have failed, still on login page")
                    print("Page source snippet:", driver.page_source[:300])
                    raise

            print("PASSED: Login success test passed")
        except Exception as e:
            print("FAIL: Login success test failed")
            raise

    def test_protected_route_redirects(self):
        """Test if protected routes redirect to login"""
        try:
            with self.get_driver() as driver:
                try:
                    # Try accessing protected route
                    driver.get("http://127.0.0.1:5001/view_stats")
                    print("PASSED: Protected route access passed")
                except:
                    print("FAIL: Protected route access failed")
                    raise
                
                try:
                    # Check redirect to login
                    time.sleep(2)  # Wait for redirect
                    self.assertIn("login", driver.current_url)
                    print("PASSED: Protected route redirect check passed")
                except:
                    print("FAIL: Protected route redirect check failed")
                    raise
            print("PASSED: Protected route test passed")
        except Exception as e:
            print("FAIL: Protected route test failed")
            raise

    def test_navigation_menu(self):
        """Test if navigation menu items are present and clickable"""
        try:
            with self.get_driver() as driver:
                try:
                    # Load homepage
                    driver.get("http://127.0.0.1:5001/")
                    print("PASSED: Homepage load passed")
                except:
                    print("FAIL: Homepage load failed")
                    raise
                
                try:
                    # Check navigation items
                    nav_items = ['Home', 'Login', 'Register']
                    for item in nav_items:
                        self.assertIn(item, driver.page_source)
                    print("PASSED: Navigation menu check passed")
                except:
                    print("FAIL: Navigation menu check failed")
                    raise
            print("PASSED: Navigation menu test passed")
        except Exception as e:
            print("FAIL: Navigation menu test failed")
            raise

    def test_responsive_design(self):
        """Test responsive design elements"""
        try:
            with self.get_driver() as driver:
                # Step 1: Go to login page
                driver.get("http://127.0.0.1:5001/auth/login")

                # Fill out login form
                driver.find_element(By.NAME, "username").send_keys("tester")
                driver.find_element(By.NAME, "password").send_keys("123456")
                driver.find_element(By.XPATH, "//button[text()='Log In']").click()
                
                WebDriverWait(driver, 5).until_not(
                    EC.url_contains("/login")
                )
                    
                # Step 2: Mobile viewport
                try:
                    driver.set_window_size(375, 812)  # iPhone X
                    driver.get("http://127.0.0.1:5001/")
                    time.sleep(2)

                    menu_button = driver.find_element(By.CLASS_NAME, "navbar-toggler")
                    assert menu_button.is_displayed()
                    print("PASSED: Mobile navbar toggle is visible")
                except Exception as e:
                    print("FAIL: Mobile responsive menu button not visible or missing")
                    raise

                # Step 3: Set desktop viewport and check nav
                try:
                    driver.set_window_size(1920, 1080)
                    driver.get("http://127.0.0.1:5001/")
                    menu_button = driver.find_element(By.CLASS_NAME, "navbar-nav")
                    assert menu_button.is_displayed()
                    print("PASSED: Desktop navbar toggle is visible")
                except Exception as e:
                    print("FAIL: Desktop navbar not visible or missing")
                    raise

            print("PASSED: test_responsive_design passed")

        except Exception as e:
            print("FAIL: test_responsive_design failed")
            raise

if __name__ == '__main__':
    unittest.main()