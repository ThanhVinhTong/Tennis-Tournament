import unittest, time
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from flask_testing import TestCase
from app import create_app, db
from app.models import User

class TestBase(TestCase):
    WAIT_TIMEOUT = 10  # Default wait timeout in seconds
    BASE_URL = "http://127.0.0.1:5001"

    def create_app(self):
        app = create_app()
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            WTF_CSRF_ENABLED=False,
            SERVER_NAME='127.0.0.1:5001'
        )
        return app

    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests"""
        cls.options = Options()
        cls.options.add_argument("--headless")
        cls.options.add_argument("--disable-gpu")
        cls.options.add_argument("--no-sandbox")
        cls.options.add_argument("--disable-dev-shm-usage")

    def setUp(self):
        """Set up test database and webdriver before each test"""
        db.create_all()
        self.driver = webdriver.Edge(options=self.options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, self.WAIT_TIMEOUT)
        
        # Create test user
        self.test_user = User(username='testuser123', email='test123@example.com')
        self.test_user.set_password('Test123!')
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        """Clean up after each test"""
        if hasattr(self, 'driver'):
            self.driver.quit()
        
        # Only delete the test user, not the entire database
        test_user = User.query.filter_by(username='testuser123').first()
        if test_user:
            db.session.delete(test_user)
        
        # Also delete the registration test user if it exists
        new_user = User.query.filter_by(username='newuser').first()
        if new_user:
            db.session.delete(new_user)
            
        db.session.commit()
        db.session.remove()

    def wait_for_element(self, by, value, timeout=None):
        """Wait for element to be present and visible"""
        timeout = timeout or self.WAIT_TIMEOUT
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            self.fail(f"Element not found: {by}={value}")

    def wait_for_url_change(self, url_part, timeout=None):
        """Wait for URL to contain specific part"""
        timeout = timeout or self.WAIT_TIMEOUT
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.url_contains(url_part)
            )
        except TimeoutException:
            self.fail(f"URL did not change to contain: {url_part}")
    
class TestWebApp(TestBase):
    def test_homepage_loads(self):
        """Test if homepage loads with navbar and footer"""
        self.driver.get(f"{self.BASE_URL}/home")
        
        # Check navbar exists
        navbar = self.wait_for_element(By.CLASS_NAME, "navbar")
        self.assertTrue(navbar.is_displayed())
        
        # Check footer exists
        footer = self.wait_for_element(By.TAG_NAME, "footer")
        self.assertTrue(footer.is_displayed())

    def test_user_registration(self):
        """Test user registration flow"""
        self.driver.get(f"{self.BASE_URL}/auth/register")
        
        # Fill registration form
        self.wait_for_element(By.ID, "username").send_keys("newuser")
        self.wait_for_element(By.ID, "email").send_keys("newuser@example.com")
        self.wait_for_element(By.ID, "password").send_keys("NewPass123!")
        self.wait_for_element(By.ID, "country").send_keys("AUSTRALIA")
        
        # Submit form using the preferred style
        WebDriverWait(self.driver, self.WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-tennis"))
        ).click()
        
        # Verify redirect to login page
        self.wait_for_url_change("login")

    def test_login_scenarios(self):
        """Test both failed and successful login attempts"""
        # Test failed login
        self.driver.get(f"{self.BASE_URL}/auth/login")
        self.wait_for_element(By.NAME, "username").clear()
        self.wait_for_element(By.NAME, "username").send_keys("wronguser")
        self.wait_for_element(By.NAME, "password").send_keys("wrongpass")
        # Click login using the preferred style
        WebDriverWait(self.driver, self.WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-tennis"))
        ).click()
        
        # Verify still on login page
        self.wait_for_element(By.ID, "username")
        self.assertIn("login", self.driver.current_url)

        # Test successful login
        self.wait_for_element(By.NAME, "username").clear()
        self.wait_for_element(By.NAME, "username").send_keys("VinceTong")
        self.wait_for_element(By.NAME, "password").clear()
        self.wait_for_element(By.NAME, "password").send_keys("123456")
        # Click login using the preferred style
        WebDriverWait(self.driver, self.WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-tennis"))
        ).click()
        
        # Verify successful login redirect
        self.wait_for_url_change("home")

    def test_protected_route_redirects(self):
        """Test if protected routes redirect to login"""
        self.driver.get(f"{self.BASE_URL}/view_stats")
        self.wait_for_url_change("login")

    def test_navigation_menu(self):
        """Test navigation menu items"""
        self.driver.get(f"{self.BASE_URL}/")
        
        nav_items = ['Home', 'Login', 'Register']
        for item in nav_items:
            self.assertTrue(
                self.wait_for_element(By.XPATH, f"//*[contains(text(), '{item}')]")
            )

    def test_responsive_design(self):
        """Test responsive design elements"""
        # Test mobile viewport
        self.driver.set_window_size(375, 812)
        self.driver.get(f"{self.BASE_URL}/home")
        mobile_menu = self.wait_for_element(By.CLASS_NAME, "navbar-toggler")
        self.assertTrue(mobile_menu.is_displayed())

        # Test desktop viewport
        self.driver.set_window_size(1920, 1080)
        self.driver.get(f"{self.BASE_URL}/home")
        desktop_nav = self.wait_for_element(By.CLASS_NAME, "navbar-nav")
        self.assertTrue(desktop_nav.is_displayed())

if __name__ == '__main__':
    unittest.main()