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


def test_strict_single_object_validation():
    """Test that from_jsonld() strictly validates single object input."""
    print("=" * 60)
    print("Testing Strict Single Object Validation")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Empty List",
            "data": [],
            "should_fail": True,
            "expected_message": "Use from_jsonld_list() instead"
        },
        {
            "name": "List with Multiple Objects",
            "data": [
                {"@id": "http://example.com/1", "@type": "http://vital.ai/ontology/vital-core#VITAL_Node"},
                {"@id": "http://example.com/2", "@type": "http://vital.ai/ontology/vital-core#VITAL_Node"}
            ],
            "should_fail": True,
            "expected_message": "Use from_jsonld_list() instead"
        },
        {
            "name": "@graph Document",
            "data": {
                "@context": {"vital": "http://vital.ai/ontology/vital-core#"},
                "@graph": [
                    {"@id": "http://example.com/1", "@type": "vital:VITAL_Node"}
                ]
            },
            "should_fail": True,
            "expected_message": "Use from_jsonld_list() instead"
        },
        {
            "name": "String Input",
            "data": "not a dict",
            "should_fail": True,
            "expected_message": "Expected dict"
        },
        {
            "name": "Number Input",
            "data": 42,
            "should_fail": True,
            "expected_message": "Expected dict"
        },
        {
            "name": "Valid Single Object",
            "data": {
                "@context": {"vital": "http://vital.ai/ontology/vital-core#"},
                "@id": "http://example.com/valid",
                "@type": "vital:VITAL_Node",
                "vital:hasName": "Valid Object"
            },
            "should_fail": False,
            "expected_message": None
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['name']}")
        print(f"Data: {json.dumps(test_case['data'], indent=2) if isinstance(test_case['data'], (dict, list)) else repr(test_case['data'])}")
        
        try:
            node = VITAL_Node.from_jsonld(test_case['data'])
            
            if test_case['should_fail']:
                print(f"❌ Should have failed but succeeded")
            else:
                print(f"✅ Correctly succeeded")
                print(f"   Created node: {node.URI}")
                passed += 1
                
        except ValueError as e:
            if test_case['should_fail']:
                if test_case['expected_message'] in str(e):
                    print(f"✅ Correctly failed with expected message")
                    print(f"   Error: {e}")
                    passed += 1
                else:
                    print(f"❌ Failed with wrong message")
                    print(f"   Expected: '{test_case['expected_message']}'")
                    print(f"   Got: '{e}'")
            else:
                print(f"❌ Should have succeeded but failed: {e}")
                
        except Exception as e:
            print(f"❌ Unexpected error type: {type(e).__name__}: {e}")
    
    print(f"\n📊 Validation Results: {passed}/{total} tests passed")
    return passed == total


def test_flexible_list_validation():
    """Test that from_jsonld_list() handles various input types flexibly."""
    print("\n" + "=" * 60)
    print("Testing Flexible List Input Validation")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Valid @graph Document",
            "data": {
                "@context": {"vital": "http://vital.ai/ontology/vital-core#"},
                "@graph": [
                    {"@id": "http://example.com/1", "@type": "vital:VITAL_Node", "vital:hasName": "Node 1"}
                ]
            },
            "should_succeed": True,
            "expected_count": 1
        },
        {
            "name": "Valid Array",
            "data": [
                {
                    "@context": {"vital": "http://vital.ai/ontology/vital-core#"},
                    "@id": "http://example.com/1", 
                    "@type": "vital:VITAL_Node",
                    "vital:hasName": "Node 1"
                }
            ],
            "should_succeed": True,
            "expected_count": 1
        },
        {
            "name": "Valid Single Object",
            "data": {
                "@context": {"vital": "http://vital.ai/ontology/vital-core#"},
                "@id": "http://example.com/1",
                "@type": "vital:VITAL_Node", 
                "vital:hasName": "Node 1"
            },
            "should_succeed": True,
            "expected_count": 1
        },
        {
            "name": "String Input",
            "data": "not valid",
            "should_succeed": False,
            "expected_count": 0
        },
        {
            "name": "Number Input", 
            "data": 123,
            "should_succeed": False,
            "expected_count": 0
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_case in test_cases:
        print(f"\n🔍 Testing: {test_case['name']}")
        
        try:
            nodes = VITAL_Node.from_jsonld_list(test_case['data'])
            
            if test_case['should_succeed']:
                if len(nodes) == test_case['expected_count']:
                    print(f"✅ Correctly succeeded with {len(nodes)} node(s)")
                    for i, node in enumerate(nodes):
                        print(f"   Node {i+1}: {node.URI}")
                    passed += 1
                else:
                    print(f"❌ Wrong count: expected {test_case['expected_count']}, got {len(nodes)}")
            else:
                print(f"❌ Should have failed but succeeded with {len(nodes)} node(s)")
                
        except ValueError as e:
            if not test_case['should_succeed']:
                print(f"✅ Correctly failed with validation error")
                print(f"   Error: {e}")
                passed += 1
            else:
                print(f"❌ Should have succeeded but failed: {e}")
                
        except Exception as e:
            print(f"❌ Unexpected error: {type(e).__name__}: {e}")
    
    print(f"\n📊 List Validation Results: {passed}/{total} tests passed")
    return passed == total


def test_error_message_clarity():
    """Test that error messages clearly direct users to correct functions."""
    print("\n" + "=" * 60)
    print("Testing Error Message Clarity")
    print("=" * 60)
    
    # Test from_jsonld with list input
    print("🔍 Testing from_jsonld() with list (should suggest from_jsonld_list())")
    try:
        VITAL_Node.from_jsonld([{"@id": "test"}])
        print("❌ Should have failed")
        return False
    except ValueError as e:
        if "Use from_jsonld_list() instead" in str(e):
            print("✅ Clear error message directing to from_jsonld_list()")
        else:
            print(f"❌ Unclear error message: {e}")
            return False
    
    # Test from_jsonld with @graph document
    print("\n🔍 Testing from_jsonld() with @graph document (should suggest from_jsonld_list())")
    try:
        VITAL_Node.from_jsonld({"@graph": [{"@id": "test"}]})
        print("❌ Should have failed")
        return False
    except ValueError as e:
        if "Use from_jsonld_list() instead" in str(e):
            print("✅ Clear error message directing to from_jsonld_list()")
        else:
            print(f"❌ Unclear error message: {e}")
            return False
    
    # Test invalid input type
    print("\n🔍 Testing invalid input type (should be clear about expected type)")
    try:
        VITAL_Node.from_jsonld("not a dict")
        print("❌ Should have failed")
        return False
    except ValueError as e:
        if "Expected dict" in str(e):
            print("✅ Clear error message about expected type")
        else:
            print(f"❌ Unclear error message: {e}")
            return False
    
    print("\n✅ All error messages are clear and helpful")
    return True


def test_input_type_edge_cases():
    """Test edge cases for input validation."""
    print("\n" + "=" * 60)
    print("Testing Input Type Edge Cases")
    print("=" * 60)
    
    edge_cases = [
        {
            "name": "None Input",
            "data": None,
            "function": "from_jsonld",
            "should_fail": True
        },
        {
            "name": "Empty Dict",
            "data": {},
            "function": "from_jsonld",
            "should_fail": True,
            "expected_message": "missing @type information"
        },
        {
            "name": "Empty List",
            "data": [],
            "function": "from_jsonld_list",
            "should_fail": False  # Should return empty list
        },
        {
            "name": "Nested Lists",
            "data": [[]],
            "function": "from_jsonld_list", 
            "should_fail": True  # Inner list is not valid JSON-LD object
        }
    ]
    
    passed = 0
    total = len(edge_cases)
    
    for case in edge_cases:
        print(f"\n🔍 Testing: {case['name']} with {case['function']}()")
        
        try:
            if case['function'] == 'from_jsonld':
                result = VITAL_Node.from_jsonld(case['data'])
            else:
                result = VITAL_Node.from_jsonld_list(case['data'])
                
            if case['should_fail']:
                print(f"❌ Should have failed but succeeded")
            else:
                print(f"✅ Correctly processed")
                if isinstance(result, list):
                    print(f"   Returned list with {len(result)} items")
                else:
                    print(f"   Returned: {type(result).__name__}")
                passed += 1
                
        except Exception as e:
            if case['should_fail']:
                # Check if expected message is specified
                if 'expected_message' in case:
                    if case['expected_message'] in str(e):
                        print(f"✅ Correctly failed with expected message: {type(e).__name__}: {e}")
                        passed += 1
                    else:
                        print(f"❌ Failed with wrong message: {e}")
                        print(f"   Expected: '{case['expected_message']}'")
                else:
                    print(f"✅ Correctly failed: {type(e).__name__}: {e}")
                    passed += 1
            else:
                print(f"❌ Should have succeeded but failed: {e}")
    
    print(f"\n📊 Edge Case Results: {passed}/{total} tests passed")
    return passed == total


def run_all_tests():
    """Run all validation tests."""
    print("🧪 JSON-LD Validation Tests")
    print("=" * 80)
    
    tests = [
        ("Strict Single Object Validation", test_strict_single_object_validation),
        ("Flexible List Input Validation", test_flexible_list_validation),
        ("Error Message Clarity", test_error_message_clarity),
        ("Input Type Edge Cases", test_input_type_edge_cases)
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
            import traceback
            traceback.print_exc()
    
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
        print("🎉 All validation tests passed!")
        return True
    else:
        print("💥 Some validation tests failed!")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
