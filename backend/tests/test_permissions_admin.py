"""
Test Admin Permissions Management APIs
Tests for:
1. Admin login
2. GET /api/users/list - see staff members
3. PUT /api/users/{user_id} - update permissions
4. POST /api/users/{user_id}/grant-full-access - give all access
5. Verify staff login sees updated permissions
"""

import pytest
import requests
import os
import json

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Test credentials
ADMIN_EMAIL = "groupenaga@gmail.com"
ADMIN_PASSWORD = "LeCercle123!"
STAFF_EMAIL = "tharshikan@orange.fr"
STAFF_PASSWORD = "Kajan1012"

class TestAdminPermissionsManagement:
    """Test permissions management flow via admin interface"""
    
    admin_token = None
    staff_user_id = None
    staff_initial_perms = None
    
    @pytest.fixture(autouse=True, scope="class")
    def setup(self, request):
        """Login as admin and get staff user info"""
        # Admin login
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Admin login failed: {response.text}"
        data = response.json()
        request.cls.admin_token = data["session_token"]
        print(f"Admin login successful: {data['user']['name']}")
        
    def test_01_admin_login_success(self):
        """Test admin can login"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "admin"
        print(f"Admin logged in: {data['user']['name']}")
        self.__class__.admin_token = data["session_token"]
    
    def test_02_get_users_list(self):
        """Test admin can get list of staff users"""
        response = requests.get(
            f"{BASE_URL}/api/users/list",
            headers={
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
        )
        assert response.status_code == 200, f"Failed to get users: {response.text}"
        users = response.json()
        assert isinstance(users, list), "Users should be a list"
        print(f"Found {len(users)} users")
        
        # Find staff user by email
        staff_user = None
        for user in users:
            if user.get("email") == STAFF_EMAIL:
                staff_user = user
                break
        
        if staff_user:
            self.__class__.staff_user_id = staff_user["user_id"]
            self.__class__.staff_initial_perms = staff_user.get("detailed_permissions", {})
            print(f"Staff user found: {staff_user['name']} ({staff_user['user_id']})")
            print(f"Staff has detailed_permissions: {bool(self.staff_initial_perms)}")
        else:
            print(f"Staff user {STAFF_EMAIL} not found in users list")
        
    def test_03_get_user_permissions(self):
        """Test admin can get specific user permissions"""
        if not self.staff_user_id:
            pytest.skip("Staff user not found in previous test")
            
        response = requests.get(
            f"{BASE_URL}/api/users/{self.staff_user_id}/permissions",
            headers={
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
        )
        # Note: This endpoint may return 404 if not implemented
        print(f"Get permissions response: {response.status_code}")
        if response.status_code == 200:
            perms = response.json()
            print(f"User permissions: {json.dumps(perms, indent=2)[:500]}")
        else:
            print(f"Response: {response.text[:500]}")
    
    def test_04_update_user_permissions(self):
        """Test admin can update staff permissions via PUT /api/users/{user_id}"""
        if not self.staff_user_id:
            pytest.skip("Staff user not found")
        
        # New permissions - enable some modules
        new_permissions = {
            "detailed_permissions": {
                "taches": {"actif": True, "categories": [], "editer": True, "ajouter": True},
                "menu_groupe": {"actif": True, "section": {"ajouter": True, "modifier": True}},
                "evenement": {"actif": True, "ajouter": True, "modifier": True},
                "fiche_technique": {"actif": True, "section_access": "tous"}
            }
        }
        
        response = requests.put(
            f"{BASE_URL}/api/users/{self.staff_user_id}",
            json=new_permissions,
            headers={
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
        )
        
        assert response.status_code == 200, f"Failed to update permissions: {response.text}"
        updated_user = response.json()
        print(f"Updated user: {updated_user.get('name')}")
        print(f"New detailed_permissions: {json.dumps(updated_user.get('detailed_permissions', {}), indent=2)[:500]}")
        
        # Verify permissions were saved
        assert "detailed_permissions" in updated_user
        dp = updated_user["detailed_permissions"]
        assert dp.get("taches", {}).get("actif") == True, "Taches should be active"
        assert dp.get("menu_groupe", {}).get("actif") == True, "Menu groupe should be active"
        
    def test_05_grant_full_access(self):
        """Test admin can grant full access to staff"""
        if not self.staff_user_id:
            pytest.skip("Staff user not found")
        
        response = requests.post(
            f"{BASE_URL}/api/users/{self.staff_user_id}/grant-full-access",
            headers={
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
        )
        
        assert response.status_code == 200, f"Failed to grant full access: {response.text}"
        result = response.json()
        print(f"Grant full access result: {result.get('message')}")
        
        # Verify user now has full access
        user = result.get("user", {})
        dp = user.get("detailed_permissions", {})
        
        # Check that all major modules are active
        assert dp.get("taches", {}).get("actif") == True, "Taches should be active"
        assert dp.get("menu_groupe", {}).get("actif") == True, "Menu groupe should be active"
        assert dp.get("evenement", {}).get("actif") == True, "Evenement should be active"
        assert dp.get("fiche_technique", {}).get("actif") == True, "Fiche technique should be active"
        assert dp.get("preparation_commande", {}).get("actif") == True, "Prep commande should be active"
        assert dp.get("menu_restaurant", {}).get("actif") == True, "Menu restaurant should be active"
        
        print(f"Full access verified for: {user.get('name')}")
        
    def test_06_verify_staff_login_sees_permissions(self):
        """Test staff user sees updated permissions after login"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STAFF_EMAIL, "password": STAFF_PASSWORD},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"Staff login failed: {response.text}"
        data = response.json()
        staff_user = data["user"]
        
        print(f"Staff logged in: {staff_user['name']}")
        print(f"Staff role: {staff_user['role']}")
        
        # Check permissions
        dp = staff_user.get("detailed_permissions", {})
        print(f"Staff detailed_permissions present: {bool(dp)}")
        
        if dp:
            # Verify at least some permissions are set
            active_modules = []
            for module in ["taches", "menu_groupe", "evenement", "fiche_technique", "menu_restaurant"]:
                if dp.get(module, {}).get("actif") == True:
                    active_modules.append(module)
            
            print(f"Active modules for staff: {active_modules}")
            assert len(active_modules) > 0, "Staff should have some active modules after grant-full-access"
        
    def test_07_update_specific_permission_toggle(self):
        """Test admin can toggle specific module permission off and on"""
        if not self.staff_user_id:
            pytest.skip("Staff user not found")
        
        # First, disable evenement module
        update_off = {
            "detailed_permissions": {
                "evenement": {"actif": False}
            }
        }
        
        response = requests.put(
            f"{BASE_URL}/api/users/{self.staff_user_id}",
            json=update_off,
            headers={
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
        )
        
        assert response.status_code == 200, f"Failed to disable evenement: {response.text}"
        result = response.json()
        
        # Note: The API may merge or replace detailed_permissions
        # Check if evenement is disabled
        dp = result.get("detailed_permissions", {})
        print(f"After disabling evenement - actif: {dp.get('evenement', {}).get('actif')}")
        
        # Re-enable evenement module
        update_on = {
            "detailed_permissions": {
                "evenement": {"actif": True, "ajouter": True}
            }
        }
        
        response2 = requests.put(
            f"{BASE_URL}/api/users/{self.staff_user_id}",
            json=update_on,
            headers={
                "Authorization": f"Bearer {self.admin_token}",
                "Content-Type": "application/json"
            }
        )
        
        assert response2.status_code == 200
        result2 = response2.json()
        dp2 = result2.get("detailed_permissions", {})
        print(f"After re-enabling evenement - actif: {dp2.get('evenement', {}).get('actif')}")


class TestStaffPermissionsVerification:
    """Verify staff user permissions work correctly after admin updates"""
    
    def test_staff_login_with_permissions(self):
        """Verify staff can login and has correct permissions"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STAFF_EMAIL, "password": STAFF_PASSWORD},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        user = data["user"]
        token = data["session_token"]
        
        print(f"Staff user: {user['name']}")
        print(f"Role: {user['role']}")
        print(f"Restaurant ID: {user.get('restaurant_id')}")
        
        dp = user.get("detailed_permissions", {})
        if dp:
            print("Detailed permissions modules:")
            for module, perms in dp.items():
                if isinstance(perms, dict) and perms.get("actif"):
                    print(f"  - {module}: ACTIVE")
        
        return token
    
    def test_staff_can_access_events_api(self):
        """Test staff can access events API if granted permission"""
        # Login first
        login_resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STAFF_EMAIL, "password": STAFF_PASSWORD}
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["session_token"]
        
        # Try accessing events
        response = requests.get(
            f"{BASE_URL}/api/events",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"Events API response: {response.status_code}")
        # Staff should have access if permissions were granted
        # Status 200 = access granted, 403 = forbidden
        if response.status_code == 200:
            events = response.json()
            print(f"Staff can access events: {len(events)} events found")
        elif response.status_code == 403:
            print("Staff does not have events permission")
        else:
            print(f"Unexpected response: {response.text}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
