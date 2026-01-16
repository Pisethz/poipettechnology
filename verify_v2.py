from network_manager import NetworkManager
import os

# Clean up any existing test data
if os.path.exists("network_data.json"):
    os.remove("network_data.json")

manager = NetworkManager()

# Setup Data
print("Setup: Adding Entries...")
entry1 = {
    "name": "Office A",
    "building": "Tower 1",
    "ip_location": "Floor 1",
    "public_ip": "1.1.1.1",
    "private_ip": "192.168.1.10",
    "bandwidth": "100MB",
    "status": "active",
    "install_date": "2023-01-01"
}
aid1 = manager.add_entry(entry1) # AID 1

entry2 = {
    "name": "Office B",
    "building": "Tower 2",
    "ip_location": "Floor 2",
    "public_ip": "2.2.2.2",
    "private_ip": "192.168.1.20",
    "bandwidth": "200MB",
    "status": "inactive",
    "install_date": "2023-01-02"
}
aid2 = manager.add_entry(entry2) # AID 2

# Test 1: Update Specific Column by AID
print("Test 1: Update Column by AID...")
manager.update_entry(aid1, {"status": "suspended"})
entry = manager.get_entry(aid1)
assert entry['status'] == "suspended"
print("Passed")

# Test 2: Update All Fields by Name
print("Test 2: Update All by Name...")
manager.update_entry("Office B", {"bandwidth": "500MB", "building": "Tower 2 Updated"})
entry = manager.get_entry(aid2)
assert entry['bandwidth'] == "500MB"
assert entry['building'] == "Tower 2 Updated"
print("Passed")

# Test 3: Delete by AID
print("Test 3: Delete by AID...")
manager.delete_entry(aid1)
assert manager.get_entry(aid1) is None
print("Passed")

# Test 4: Delete by Name
print("Test 4: Delete by Name...")
manager.delete_entry("Office B")
assert manager.get_entry(aid2) is None
print("Passed")

print("\nALL NEW FEATURE TESTS PASSED!")
