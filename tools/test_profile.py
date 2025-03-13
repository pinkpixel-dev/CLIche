#!/usr/bin/env python3
"""
Test User Profile Functionality

This script tests the user profile functionality in the memory system.

Made with ❤️ by Pink Pixel
"""
import os
import sys
import json
from pathlib import Path

# Add parent directory to path to import from cliche
script_dir = Path(__file__).parent
project_dir = script_dir.parent
sys.path.append(str(project_dir))

from cliche.core import get_cliche_instance

def test_profile():
    """Test the user profile functionality"""
    print("\n🧪 Testing User Profile Functionality")
    print("====================================")
    
    # Get CLIche instance
    assistant = get_cliche_instance()
    
    if not assistant.memory.enabled:
        print("\n❌ Memory system is disabled. Enable it to test profile functionality.")
        print("   Use 'cliche memory toggle on' to enable the memory system.")
        return False
    
    # Enable user profile
    print("\n1️⃣ Enabling user profile...")
    result = assistant.memory.toggle_profile(True)
    if result:
        print("✅ User profile enabled successfully.")
    else:
        print("❌ Failed to enable user profile.")
        return False
    
    # Get current profile status
    print("\n2️⃣ Getting memory status...")
    status = assistant.memory.get_status()
    print(f"✅ Memory system status: Enabled={status['enabled']}, Profile Enabled={status['profile_enabled']}")
    
    # Set a profile field
    print("\n3️⃣ Setting profile fields...")
    test_fields = {
        "name": "Test User",
        "location": "Test City",
        "occupation": "Software Developer",
        "interests": "Python, AI, Testing"
    }
    
    success = True
    for field, value in test_fields.items():
        result = assistant.memory.set_profile_field(field, value)
        if result:
            print(f"✅ Set {field}={value}")
        else:
            print(f"❌ Failed to set {field}={value}")
            success = False
    
    if not success:
        print("❌ Failed to set some profile fields.")
    
    # Get the profile
    print("\n4️⃣ Getting profile...")
    status = assistant.memory.get_status()
    profile = status.get("profile", {})
    
    if profile:
        print("✅ Profile retrieved successfully:")
        for field, value in profile.items():
            print(f"   {field}: {value}")
    else:
        print("❌ Profile is empty or could not be retrieved.")
        return False
    
    # Check if all fields were set correctly
    all_fields_correct = True
    for field, value in test_fields.items():
        if field not in profile or profile[field] != value:
            print(f"❌ Field {field} was not set correctly.")
            all_fields_correct = False
    
    if all_fields_correct:
        print("✅ All profile fields were set correctly.")
    
    # Clear the profile
    print("\n5️⃣ Clearing profile...")
    result = assistant.memory.clear_profile()
    if result:
        print("✅ Profile cleared successfully.")
    else:
        print("❌ Failed to clear profile.")
        return False
    
    # Verify profile was cleared
    print("\n6️⃣ Verifying profile was cleared...")
    status = assistant.memory.get_status()
    profile = status.get("profile", {})
    
    if not profile:
        print("✅ Profile was cleared successfully.")
    else:
        print("❌ Profile was not cleared correctly.")
        print(f"   Remaining profile: {json.dumps(profile, indent=2)}")
        return False
    
    print("\n✅ All user profile tests passed successfully!")
    return True

if __name__ == "__main__":
    success = test_profile()
    sys.exit(0 if success else 1) 