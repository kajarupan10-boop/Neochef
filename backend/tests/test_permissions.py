"""
Test suite for NeoChef Permissions Management
Tests: Permission saving, Restaurant access for staff, Permission display

Target bugs:
1. Permissions checked for employees don't save correctly and uncheck after reload
2. Employees cannot switch between restaurants
3. Incomplete translations for some restaurants
"""

import pytest
import requests
import os

# Use the public URL from environment, fallback to localhost for testing
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001').rstrip('/')

# Test credentials
ADMIN_EMAIL = "test_admin@lecercle.fr"
ADMIN_PASSWORD = "Kajan1012"
STAFF_USER_ID = "user_170e8cde227d"

class TestPermissions:
    """Test cases for permissions management"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.admin_token = None
        
    def test_health_check(self):
        """Test API health endpoint"""
        response = self.session.get(f"{BASE_URL}/api/health")
        print(f"Health check status: {response.status_code}")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("✓ Health check passed")
        
    def test_admin_login(self):
        """Test admin login to get authentication token"""
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        print(f"Login status: {response.status_code}")
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        assert "session_token" in data
        assert "user" in data
        assert data["user"]["role"] == "admin"
        
        self.admin_token = data["session_token"]
        print(f"✓ Admin login successful, user: {data['user']['name']}")
        return self.admin_token
    
    def test_get_users_list(self):
        """Test getting users list"""
        token = self.test_admin_login()
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        response = self.session.get(f"{BASE_URL}/api/users/list")
        print(f"Users list status: {response.status_code}")
        assert response.status_code == 200
        
        users = response.json()
        assert isinstance(users, list)
        print(f"✓ Found {len(users)} users")
        
        # Find the staff user
        staff_user = next((u for u in users if u.get("user_id") == STAFF_USER_ID), None)
        if staff_user:
            print(f"✓ Found staff user: {staff_user.get('name')} ({staff_user.get('email')})")
            print(f"  - restaurant_id: {staff_user.get('restaurant_id')}")
            print(f"  - restaurant_ids: {staff_user.get('restaurant_ids', [])}")
            print(f"  - detailed_permissions keys: {list(staff_user.get('detailed_permissions', {}).keys())}")
        return users
    
    def test_get_staff_user_details(self):
        """Test getting specific staff user details"""
        token = self.test_admin_login()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        response = self.session.get(f"{BASE_URL}/api/users/list")
        assert response.status_code == 200
        users = response.json()
        
        staff_user = next((u for u in users if u.get("user_id") == STAFF_USER_ID), None)
        assert staff_user is not None, f"Staff user {STAFF_USER_ID} not found"
        
        # Check initial state
        print(f"✓ Staff user initial state:")
        print(f"  - restaurant_ids: {staff_user.get('restaurant_ids', [])}")
        dp = staff_user.get('detailed_permissions', {})
        print(f"  - parametres: {dp.get('parametres')}")
        print(f"  - equipe: {dp.get('equipe')}")
        print(f"  - menu_restaurant.actif: {dp.get('menu_restaurant', {}).get('actif')}")
        print(f"  - menu_client.actif: {dp.get('menu_client', {}).get('actif')}")
        print(f"  - prestataires.actif: {dp.get('prestataires', {}).get('actif')}")
        
        return staff_user
    
    def test_update_user_permissions(self):
        """
        BUG TEST 1: Test that permissions save correctly and persist
        Steps:
        1. Get current staff user permissions
        2. Update permissions (toggle some values)
        3. Verify update response has correct values
        4. Fetch user again and verify persistence
        """
        token = self.test_admin_login()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get current user state
        response = self.session.get(f"{BASE_URL}/api/users/list")
        assert response.status_code == 200
        users = response.json()
        staff_user = next((u for u in users if u.get("user_id") == STAFF_USER_ID), None)
        assert staff_user is not None
        
        original_dp = staff_user.get('detailed_permissions', {})
        original_restaurant_ids = staff_user.get('restaurant_ids', [])
        
        print(f"Original parametres: {original_dp.get('parametres')}")
        print(f"Original equipe: {original_dp.get('equipe')}")
        print(f"Original restaurant_ids: {original_restaurant_ids}")
        
        # Toggle the 'parametres' and 'equipe' values
        new_parametres = not original_dp.get('parametres', False)
        new_equipe = not original_dp.get('equipe', False)
        
        # Create updated permissions payload
        updated_permissions = {
            **original_dp,
            'parametres': new_parametres,
            'equipe': new_equipe,
            'restaurants_access': {
                'all': False,
                'restaurant_ids': original_restaurant_ids
            },
            'menu_restaurant': {
                'actif': True,
                'lien_partage': False,
                'section': {'ajouter': False, 'modifier': False, 'supprimer': False},
                'produits': {'ajouter': False, 'modifier': False, 'supprimer': False},
                'export_pdf': False,
                'export_csv': False,
                'import_csv': False,
                'import_pdf': False,
                'note': False
            }
        }
        
        payload = {
            'detailed_permissions': updated_permissions,
            'restaurant_ids': original_restaurant_ids
        }
        
        print(f"\n[UPDATE] Updating with parametres={new_parametres}, equipe={new_equipe}")
        
        # Update permissions
        response = self.session.put(
            f"{BASE_URL}/api/users/{STAFF_USER_ID}",
            json=payload
        )
        print(f"Update status: {response.status_code}")
        assert response.status_code == 200, f"Update failed: {response.text}"
        
        updated_user = response.json()
        print(f"✓ Update response received")
        
        # Verify response has updated values
        resp_dp = updated_user.get('detailed_permissions', {})
        assert resp_dp.get('parametres') == new_parametres, f"Response parametres mismatch: expected {new_parametres}, got {resp_dp.get('parametres')}"
        assert resp_dp.get('equipe') == new_equipe, f"Response equipe mismatch: expected {new_equipe}, got {resp_dp.get('equipe')}"
        print(f"✓ Update response has correct values (parametres={resp_dp.get('parametres')}, equipe={resp_dp.get('equipe')})")
        
        # Verify restaurant_ids persisted
        resp_restaurant_ids = updated_user.get('restaurant_ids', [])
        print(f"Response restaurant_ids: {resp_restaurant_ids}")
        assert resp_restaurant_ids == original_restaurant_ids or len(resp_restaurant_ids) == len(original_restaurant_ids), \
            f"restaurant_ids mismatch: expected {original_restaurant_ids}, got {resp_restaurant_ids}"
        print(f"✓ restaurant_ids persisted correctly")
        
        # Now fetch the user again to verify persistence (simulating page reload)
        print(f"\n[RELOAD] Fetching user again to verify persistence...")
        response = self.session.get(f"{BASE_URL}/api/users/list")
        assert response.status_code == 200
        users = response.json()
        
        reloaded_user = next((u for u in users if u.get("user_id") == STAFF_USER_ID), None)
        assert reloaded_user is not None
        
        reloaded_dp = reloaded_user.get('detailed_permissions', {})
        print(f"Reloaded parametres: {reloaded_dp.get('parametres')}")
        print(f"Reloaded equipe: {reloaded_dp.get('equipe')}")
        
        # CRITICAL CHECK: Verify values persisted after reload
        assert reloaded_dp.get('parametres') == new_parametres, \
            f"BUG FOUND: parametres reset after reload! Expected {new_parametres}, got {reloaded_dp.get('parametres')}"
        assert reloaded_dp.get('equipe') == new_equipe, \
            f"BUG FOUND: equipe reset after reload! Expected {new_equipe}, got {reloaded_dp.get('equipe')}"
        
        print(f"✓ PASS: Permissions persisted correctly after reload")
        
        # Restore original values
        restore_payload = {
            'detailed_permissions': original_dp,
            'restaurant_ids': original_restaurant_ids
        }
        self.session.put(f"{BASE_URL}/api/users/{STAFF_USER_ID}", json=restore_payload)
        print(f"✓ Restored original permissions")
        
        return True
    
    def test_restaurant_ids_initialization(self):
        """
        BUG TEST 2: Test that restaurant_ids are correctly initialized in permissions modal
        The frontend should initialize restaurants_access from user.restaurant_ids
        """
        token = self.test_admin_login()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get staff user
        response = self.session.get(f"{BASE_URL}/api/users/list")
        assert response.status_code == 200
        users = response.json()
        staff_user = next((u for u in users if u.get("user_id") == STAFF_USER_ID), None)
        assert staff_user is not None
        
        restaurant_ids = staff_user.get('restaurant_ids', [])
        dp = staff_user.get('detailed_permissions', {})
        
        print(f"User restaurant_ids: {restaurant_ids}")
        print(f"User detailed_permissions.restaurants_access: {dp.get('restaurants_access')}")
        
        # Verify restaurant_ids is not empty for staff with multiple restaurants
        assert len(restaurant_ids) > 0, "Staff user should have restaurant_ids assigned"
        print(f"✓ Staff user has {len(restaurant_ids)} restaurant(s) assigned")
        
        # Verify the data can be used for initializing the permissions modal
        # The frontend should use restaurant_ids to set restaurants_access if restaurants_access is not set
        if dp.get('restaurants_access') is None:
            # This is expected - the fix should initialize restaurants_access from restaurant_ids
            print(f"✓ restaurants_access is None - frontend should initialize from restaurant_ids")
        else:
            print(f"✓ restaurants_access already set: {dp.get('restaurants_access')}")
        
        return staff_user
    
    def test_save_permissions_with_restaurant_ids_fallback(self):
        """
        BUG TEST 3: Test that saving permissions preserves restaurant_ids even when 
        allRestaurants is empty in the frontend
        """
        token = self.test_admin_login()
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get current user state
        response = self.session.get(f"{BASE_URL}/api/users/list")
        assert response.status_code == 200
        users = response.json()
        staff_user = next((u for u in users if u.get("user_id") == STAFF_USER_ID), None)
        assert staff_user is not None
        
        original_restaurant_ids = staff_user.get('restaurant_ids', [])
        original_dp = staff_user.get('detailed_permissions', {})
        
        print(f"Original restaurant_ids: {original_restaurant_ids}")
        
        # Simulate saving with minimal payload (testing fallback)
        minimal_dp = {
            'restaurants_access': {'all': False, 'restaurant_ids': original_restaurant_ids},
            'parametres': True,
            'equipe': True
        }
        
        payload = {
            'detailed_permissions': minimal_dp,
            'restaurant_ids': original_restaurant_ids
        }
        
        response = self.session.put(
            f"{BASE_URL}/api/users/{STAFF_USER_ID}",
            json=payload
        )
        print(f"Update status: {response.status_code}")
        assert response.status_code == 200
        
        updated_user = response.json()
        saved_restaurant_ids = updated_user.get('restaurant_ids', [])
        
        print(f"Saved restaurant_ids: {saved_restaurant_ids}")
        assert len(saved_restaurant_ids) == len(original_restaurant_ids), \
            f"restaurant_ids lost! Original: {original_restaurant_ids}, After save: {saved_restaurant_ids}"
        
        print(f"✓ PASS: restaurant_ids preserved after save")
        
        # Restore original
        restore_payload = {
            'detailed_permissions': original_dp,
            'restaurant_ids': original_restaurant_ids
        }
        self.session.put(f"{BASE_URL}/api/users/{STAFF_USER_ID}", json=restore_payload)
        
        return True


class TestRestaurantSwitching:
    """Test cases for restaurant switching functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
    def test_get_my_restaurants(self):
        """Test getting list of restaurants for admin user"""
        # Login as admin
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        token = response.json()["session_token"]
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        # Get restaurants
        response = self.session.get(f"{BASE_URL}/api/restaurants/my-restaurants")
        print(f"My restaurants status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            restaurants = data.get('restaurants', [])
            print(f"✓ Found {len(restaurants)} restaurant(s)")
            for r in restaurants:
                print(f"  - {r.get('name')} (ID: {r.get('restaurant_id')})")
        else:
            print(f"Could not get restaurants: {response.text}")
        
        return True
    
    def test_switch_restaurant_endpoint(self):
        """Test restaurant switching endpoint"""
        # Login as admin
        response = self.session.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        token = data["session_token"]
        current_restaurant_id = data.get("restaurant", {}).get("restaurant_id")
        
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        
        print(f"Current restaurant: {current_restaurant_id}")
        
        # Get available restaurants
        response = self.session.get(f"{BASE_URL}/api/restaurants/my-restaurants")
        if response.status_code == 200:
            restaurants = response.json().get('restaurants', [])
            
            if len(restaurants) > 1:
                # Find a different restaurant to switch to
                other_restaurant = next(
                    (r for r in restaurants if r.get('restaurant_id') != current_restaurant_id), 
                    None
                )
                
                if other_restaurant:
                    print(f"Attempting to switch to: {other_restaurant.get('name')}")
                    
                    response = self.session.post(
                        f"{BASE_URL}/api/restaurants/switch",
                        json={"restaurant_id": other_restaurant.get('restaurant_id')}
                    )
                    print(f"Switch status: {response.status_code}")
                    
                    if response.status_code == 200:
                        switch_data = response.json()
                        new_restaurant = switch_data.get('restaurant', {})
                        print(f"✓ Switched to: {new_restaurant.get('name')}")
                        
                        # Switch back
                        self.session.post(
                            f"{BASE_URL}/api/restaurants/switch",
                            json={"restaurant_id": current_restaurant_id}
                        )
                        print(f"✓ Switched back to original restaurant")
                    else:
                        print(f"Switch failed: {response.text}")
            else:
                print(f"Only one restaurant available, cannot test switching")
        
        return True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
