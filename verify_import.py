from network_manager import NetworkManager
import os
import csv

# Setup Test Data
csv_file = "test_import.csv"
manager = NetworkManager()

# Clear existing data for clean import test
if os.path.exists("network_data.json"):
    os.remove("network_data.json")
    manager = NetworkManager() # Reload with empty

# Create a sample CSV
with open(csv_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["AID", "Name", "Building", "Status"])
    writer.writerow(["IMP-001", "Imported Net 1", "Tower I", "active"])
    writer.writerow(["IMP-002", "Imported Net 2", "Tower I", "inactive"])

print("Test 1: Import CSV...")
result = manager.import_from_csv(csv_file)
assert result['added'] == 2
assert result['skipped'] == 0
assert len(manager.get_all()) == 2
print("Passed: Imported 2 records")

# Test 2: Import Duplicate
print("Test 2: Import Duplicate...")
# Create CSV with 1 new, 1 duplicate
with open(csv_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["AID", "Name", "Building", "Status"])
    writer.writerow(["IMP-001", "Imported Net 1", "Tower I", "active"]) # Duplicate
    writer.writerow(["IMP-003", "Imported Net 3", "Tower II", "active"]) # New

result = manager.import_from_csv(csv_file)
assert result['added'] == 1
assert result['skipped'] == 1
assert len(manager.get_all()) == 3
print("Passed: Correctly skipped duplicate and added new")

print("ALL IMPORT TESTS PASSED")

# Clean up
try:
    os.remove(csv_file)
    os.remove("network_data.json")
except:
    pass
