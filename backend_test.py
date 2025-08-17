#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import time

class SoccerStreamAPITester:
    def __init__(self, base_url="https://soccer-replay-hub.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.errors = []

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
            self.errors.append(f"{name}: {details}")
        
        if details and success:
            print(f"   Details: {details}")

    def test_endpoint(self, name, endpoint, expected_status=200, method="GET", data=None):
        """Test a single API endpoint"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            print(f"\n🔍 Testing {name}...")
            print(f"   URL: {url}")
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            
            success = response.status_code == expected_status
            
            if success:
                try:
                    response_data = response.json()
                    self.log_test(name, True, f"Status: {response.status_code}, Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'List with ' + str(len(response_data)) + ' items'}")
                    return True, response_data
                except:
                    self.log_test(name, True, f"Status: {response.status_code}, Non-JSON response")
                    return True, response.text
            else:
                try:
                    error_data = response.json()
                    self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}. Error: {error_data}")
                except:
                    self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}. Response: {response.text[:200]}")
                return False, {}
                
        except requests.exceptions.Timeout:
            self.log_test(name, False, "Request timeout (10s)")
            return False, {}
        except requests.exceptions.ConnectionError:
            self.log_test(name, False, "Connection error - server may be down")
            return False, {}
        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return False, {}

    def test_health_endpoint(self):
        """Test health check endpoint"""
        success, response = self.test_endpoint("Health Check", "/api/health")
        if success and isinstance(response, dict):
            if response.get('status') == 'healthy':
                print("   ✅ Database connection is healthy")
                return True
            else:
                print("   ⚠️  Database connection issues detected")
        return success

    def test_leagues_endpoint(self):
        """Test leagues endpoint"""
        success, response = self.test_endpoint("Get Leagues", "/api/leagues")
        if success and isinstance(response, list):
            print(f"   Found {len(response)} leagues:")
            for league in response[:3]:  # Show first 3
                print(f"     - {league.get('name', 'Unknown')} ({league.get('country', 'Unknown')})")
            if len(response) > 3:
                print(f"     ... and {len(response) - 3} more")
            return True
        return success

    def test_matches_endpoint(self):
        """Test matches endpoint with various filters"""
        # Test basic matches endpoint
        success, response = self.test_endpoint("Get All Matches", "/api/matches")
        if not success:
            return False
            
        if isinstance(response, dict) and 'matches' in response:
            matches = response['matches']
            total = response.get('total', 0)
            print(f"   Found {len(matches)} matches (total: {total})")
            
            # Show sample matches
            for match in matches[:2]:
                status = match.get('status', 'unknown')
                home = match.get('home_team', 'Unknown')
                away = match.get('away_team', 'Unknown')
                league = match.get('league', 'Unknown')
                print(f"     - {home} vs {away} ({league}) - {status}")
        
        # Test status filters
        for status in ['live', 'upcoming', 'finished']:
            success, response = self.test_endpoint(f"Get {status.title()} Matches", f"/api/matches?status={status}")
            if success and isinstance(response, dict):
                count = len(response.get('matches', []))
                print(f"   {status.title()} matches: {count}")
        
        # Test league filter
        success, response = self.test_endpoint("Filter by Premier League", "/api/matches?league=Premier League")
        if success and isinstance(response, dict):
            count = len(response.get('matches', []))
            print(f"   Premier League matches: {count}")
        
        # Test search functionality
        success, response = self.test_endpoint("Search for Manchester", "/api/matches?search=Manchester")
        if success and isinstance(response, dict):
            count = len(response.get('matches', []))
            print(f"   Matches with 'Manchester': {count}")
        
        return True

    def test_stats_endpoint(self):
        """Test statistics endpoint"""
        success, response = self.test_endpoint("Get Platform Stats", "/api/stats")
        if success and isinstance(response, dict):
            stats = []
            for key, value in response.items():
                if key != 'last_updated':
                    stats.append(f"{key}: {value}")
            print(f"   Stats: {', '.join(stats)}")
        return success

    def test_individual_match(self):
        """Test getting individual match by ID"""
        # First get a match ID from the matches endpoint
        success, response = self.test_endpoint("Get Matches for ID Test", "/api/matches?limit=1")
        if success and isinstance(response, dict) and response.get('matches'):
            match_id = response['matches'][0].get('id')
            if match_id:
                success, match_response = self.test_endpoint("Get Match by ID", f"/api/matches/{match_id}")
                if success:
                    home = match_response.get('home_team', 'Unknown')
                    away = match_response.get('away_team', 'Unknown')
                    print(f"   Retrieved match: {home} vs {away}")
                return success
        
        self.log_test("Get Match by ID", False, "Could not get match ID for testing")
        return False

    def test_root_endpoint(self):
        """Test root endpoint"""
        success, response = self.test_endpoint("Root Endpoint", "/")
        if success and isinstance(response, dict):
            if 'message' in response and 'endpoints' in response:
                print("   ✅ Root endpoint provides API documentation")
                return True
        return success

    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting SoccerStream Backend API Tests")
        print("=" * 60)
        
        # Test basic connectivity
        print("\n📡 CONNECTIVITY TESTS")
        self.test_root_endpoint()
        self.test_health_endpoint()
        
        # Test core endpoints
        print("\n🏆 CORE API TESTS")
        self.test_leagues_endpoint()
        self.test_matches_endpoint()
        self.test_stats_endpoint()
        self.test_individual_match()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.errors:
            print(f"\n❌ FAILED TESTS:")
            for error in self.errors:
                print(f"  - {error}")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = SoccerStreamAPITester()
    
    print("SoccerStream Backend API Tester")
    print(f"Testing against: {tester.base_url}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Backend is working correctly.")
        return 0
    else:
        print(f"\n⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())