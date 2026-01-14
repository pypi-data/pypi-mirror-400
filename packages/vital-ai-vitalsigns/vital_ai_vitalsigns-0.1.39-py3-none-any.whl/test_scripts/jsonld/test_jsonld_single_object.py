#!/usr/bin/env python3

import json
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from vital_ai_vitalsigns.vitalsigns import VitalSigns
from vital_ai_vitalsigns.model.VITAL_Node import VITAL_Node


def test_to_jsonld_single_object():
    """Test to_jsonld() for single GraphObject - should return object with context."""
    print("=" * 60)
    print("Testing to_jsonld() - Single Object")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create a test VITAL_Node object
    node = VITAL_Node()
    node.URI = "http://example.com/test-single-node"
    node.name = "Single Test Node"
    
    print(f"Created VITAL_Node:")
    print(f"  URI: {node.URI}")
    print(f"  Name: {node.name}")
    print(f"  Class: {node.get_class_uri()}")
    
    # Test to_jsonld - should return single object with context
    try:
        jsonld_obj = node.to_jsonld()
        print(f"\n✅ to_jsonld() successful!")
        print(f"JSON-LD Object (single object with context):")
        print(json.dumps(jsonld_obj, indent=2))
        
        # Validate structure - should be single object with @context
        if "@context" not in jsonld_obj:
            print(f"❌ Missing @context in single object")
            return False
            
        if "@graph" in jsonld_obj:
            print(f"❌ Unexpected @graph in single object - should use to_jsonld_list() for documents")
            return False
            
        if "@id" not in jsonld_obj:
            print(f"❌ Missing @id in single object")
            return False
            
        print(f"\n✅ Single object structure validation passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ to_jsonld() failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_from_jsonld_single_object():
    """Test from_jsonld() with single JSON-LD object - should work correctly."""
    print("\n" + "=" * 60)
    print("Testing from_jsonld() - Single Object")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create test JSON-LD single object (not document)
    jsonld_obj = {
        "@context": {
            "vital": "http://vital.ai/ontology/vital-core#",
            "type": "@type",
            "id": "@id"
        },
        "@id": "http://example.com/test-from-single",
        "@type": "vital:VITAL_Node",
        "vital:hasName": "From JSON-LD Single"
    }
    
    print(f"Test JSON-LD single object:")
    print(json.dumps(jsonld_obj, indent=2))
    
    # Test from_jsonld
    try:
        node = VITAL_Node.from_jsonld(jsonld_obj)
        print(f"\n✅ from_jsonld() successful!")
        print(f"Created Node:")
        print(f"  URI: {node.URI}")
        print(f"  Name: {node.name}")
        print(f"  Class: {node.get_class_uri()}")
        
        # Validate conversion
        if node.URI != "http://example.com/test-from-single":
            print(f"❌ URI mismatch: expected 'http://example.com/test-from-single', got '{node.URI}'")
            return False
            
        if node.name != "From JSON-LD Single":
            print(f"❌ Name mismatch: expected 'From JSON-LD Single', got '{node.name}'")
            return False
            
        print(f"\n✅ Single object conversion validation passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ from_jsonld() failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_from_jsonld_rejects_list():
    """Test from_jsonld() rejects list input - should raise ValueError."""
    print("\n" + "=" * 60)
    print("Testing from_jsonld() - Rejects List Input")
    print("=" * 60)
    
    # Create test list (should be rejected)
    jsonld_list = [
        {
            "@id": "http://example.com/obj1",
            "@type": "http://vital.ai/ontology/vital-core#VITAL_Node",
            "http://vital.ai/ontology/vital-core#hasName": "Object 1"
        },
        {
            "@id": "http://example.com/obj2", 
            "@type": "http://vital.ai/ontology/vital-core#VITAL_Node",
            "http://vital.ai/ontology/vital-core#hasName": "Object 2"
        }
    ]
    
    print(f"Test JSON-LD list (should be rejected):")
    print(json.dumps(jsonld_list, indent=2))
    
    # Test from_jsonld - should raise ValueError
    try:
        node = VITAL_Node.from_jsonld(jsonld_list)
        print(f"\n❌ from_jsonld() should have rejected list input!")
        return False
        
    except ValueError as e:
        expected_message = "Use from_jsonld_list() instead"
        if expected_message in str(e):
            print(f"\n✅ from_jsonld() correctly rejected list input!")
            print(f"Error message: {e}")
            return True
        else:
            print(f"\n❌ Wrong error message: {e}")
            return False
            
    except Exception as e:
        print(f"\n❌ Unexpected error type: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_from_jsonld_rejects_graph_document():
    """Test from_jsonld() rejects @graph document - should raise ValueError."""
    print("\n" + "=" * 60)
    print("Testing from_jsonld() - Rejects @graph Document")
    print("=" * 60)
    
    # Create test @graph document (should be rejected)
    jsonld_doc = {
        "@context": {
            "vital": "http://vital.ai/ontology/vital-core#",
            "type": "@type",
            "id": "@id"
        },
        "@graph": [
            {
                "@id": "http://example.com/obj1",
                "@type": "vital:VITAL_Node",
                "vital:hasName": "Object 1"
            }
        ]
    }
    
    print(f"Test JSON-LD @graph document (should be rejected):")
    print(json.dumps(jsonld_doc, indent=2))
    
    # Test from_jsonld - should raise ValueError
    try:
        node = VITAL_Node.from_jsonld(jsonld_doc)
        print(f"\n❌ from_jsonld() should have rejected @graph document!")
        return False
        
    except ValueError as e:
        expected_message = "Use from_jsonld_list() instead"
        if expected_message in str(e):
            print(f"\n✅ from_jsonld() correctly rejected @graph document!")
            print(f"Error message: {e}")
            return True
        else:
            print(f"\n❌ Wrong error message: {e}")
            return False
            
    except Exception as e:
        print(f"\n❌ Unexpected error type: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_round_trip_single_object():
    """Test round-trip conversion: GraphObject -> JSON-LD -> GraphObject."""
    print("\n" + "=" * 60)
    print("Testing Round-trip - Single Object")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create original object
    original = VITAL_Node()
    original.URI = "http://example.com/round-trip-test"
    original.name = "Round Trip Test"
    
    print(f"Original Node:")
    print(f"  URI: {original.URI}")
    print(f"  Name: {original.name}")
    
    try:
        # Convert to JSON-LD
        jsonld_obj = original.to_jsonld()
        print(f"\n✅ Step 1: to_jsonld() successful")
        
        # Convert back to GraphObject
        reconstructed = VITAL_Node.from_jsonld(jsonld_obj)
        print(f"✅ Step 2: from_jsonld() successful")
        
        print(f"\nReconstructed Node:")
        print(f"  URI: {reconstructed.URI}")
        print(f"  Name: {reconstructed.name}")
        
        # Validate round-trip
        if (original.URI == reconstructed.URI and 
            original.name == reconstructed.name and
            original.get_class_uri() == reconstructed.get_class_uri()):
            print(f"\n✅ Round-trip conversion successful!")
            return True
        else:
            print(f"\n❌ Round-trip conversion failed - data mismatch")
            return False
            
    except Exception as e:
        print(f"\n❌ Round-trip conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all single object JSON-LD tests."""
    print("🧪 JSON-LD Single Object Tests")
    print("=" * 80)
    
    tests = [
        ("to_jsonld() Single Object", test_to_jsonld_single_object),
        ("from_jsonld() Single Object", test_from_jsonld_single_object),
        ("from_jsonld() Rejects List", test_from_jsonld_rejects_list),
        ("from_jsonld() Rejects @graph Document", test_from_jsonld_rejects_graph_document),
        ("Round-trip Single Object", test_round_trip_single_object)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"Result: {status}")
        except Exception as e:
            results.append((test_name, False))
            print(f"❌ FAILED with exception: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
