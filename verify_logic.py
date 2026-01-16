from network_manager import NetworkManager
import os

# Clean up any existing test data
if os.path.exists("network_data.json"):
    os.remove("network_data.json")

manager = NetworkManager()

# Test 1: Add Entry
print("Test 1: Adding Entry...")
entry = {
    "name": "Test Office",
    "building": "Building A",
    "ip_location": "Floor 1",
    "public_ip": "1.2.3.4",
    "private_ip": "192.168.1.10",
    "bandwidth": "1GB",
    "status": "active",
    "install_date": "2023-10-27"
}
aid = manager.add_entry(entry)
assert aid == 1
print("Passed: Entry added with AID 1")

# Test 2: Search
print("Test 2: Searching...")
results = manager.search("Building A")
assert len(results) == 1
assert results[0]['name'] == "Test Office"
print("Passed: Search found entry")

# Test 3: Update Status
print("Test 3: Updating Status...")
success = manager.update_status(1, "inactive")
assert success is True
updated_entry = manager.get_all()[0]
assert updated_entry['status'] == "inactive"
assert len(updated_entry['history']) > 1
print("Passed: Status updated and history logged")

# Test 4: Persistence
print("Test 4: Testing Persistence...")
manager2 = NetworkManager()
loaded_data = manager2.get_all()
assert len(loaded_data) == 1
assert loaded_data[0]['name'] == "Test Office"
print("Passed: Data persisted to disk")

print("\nALL TESTS PASSED!")
