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


def test_to_jsonld_list():
    """Test to_jsonld_list() - should return document with @graph."""
    print("=" * 60)
    print("Testing to_jsonld_list() - Multiple Objects")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create multiple test objects
    nodes = []
    for i in range(3):
        node = VITAL_Node()
        node.URI = f"http://example.com/list-test-node-{i+1}"
        node.name = f"List Test Node {i+1}"
        nodes.append(node)
    
    print(f"Created {len(nodes)} VITAL_Node objects:")
    for node in nodes:
        print(f"  - URI: {node.URI}, Name: {node.name}")
    
    # Test to_jsonld_list - should return document with @graph
    try:
        jsonld_doc = VITAL_Node.to_jsonld_list(nodes)
        print(f"\n✅ to_jsonld_list() successful!")
        print(f"JSON-LD Document (with @graph):")
        print(json.dumps(jsonld_doc, indent=2))
        
        # Validate structure - should be document with @context and @graph
        if "@context" not in jsonld_doc:
            print(f"❌ Missing @context in document")
            return False
            
        if "@graph" not in jsonld_doc:
            print(f"❌ Missing @graph in document - should contain @graph array")
            return False
            
        if not isinstance(jsonld_doc["@graph"], list):
            print(f"❌ @graph should be a list")
            return False
            
        if len(jsonld_doc["@graph"]) != len(nodes):
            print(f"❌ @graph length mismatch: expected {len(nodes)}, got {len(jsonld_doc['@graph'])}")
            return False
            
        # Check that individual objects don't have @context (should be at document level)
        for i, obj in enumerate(jsonld_doc["@graph"]):
            if "@context" in obj:
                print(f"❌ Object {i} should not have individual @context (should be at document level)")
                return False
                
        print(f"\n✅ Document structure validation passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ to_jsonld_list() failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_from_jsonld_list_with_graph_document():
    """Test from_jsonld_list() with @graph document - should work correctly."""
    print("\n" + "=" * 60)
    print("Testing from_jsonld_list() - @graph Document")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create test JSON-LD document with @graph
    jsonld_doc = {
        "@context": {
            "vital": "http://vital.ai/ontology/vital-core#",
            "type": "@type",
            "id": "@id"
        },
        "@graph": [
            {
                "@id": "http://example.com/doc-test-1",
                "@type": "vital:VITAL_Node",
                "vital:hasName": "Document Test 1"
            },
            {
                "@id": "http://example.com/doc-test-2",
                "@type": "vital:VITAL_Node", 
                "vital:hasName": "Document Test 2"
            }
        ]
    }
    
    print(f"Test JSON-LD @graph document:")
    print(json.dumps(jsonld_doc, indent=2))
    
    # Test from_jsonld_list
    try:
        nodes = VITAL_Node.from_jsonld_list(jsonld_doc)
        print(f"\n✅ from_jsonld_list() successful!")
        print(f"Created {len(nodes)} nodes from @graph document:")
        for node in nodes:
            print(f"  - URI: {node.URI}, Name: {node.name}")
        
        # Validate conversion
        if len(nodes) != 2:
            print(f"❌ Expected 2 nodes, got {len(nodes)}")
            return False
            
        expected_data = [
            ("http://example.com/doc-test-1", "Document Test 1"),
            ("http://example.com/doc-test-2", "Document Test 2")
        ]
        
        for i, (expected_uri, expected_name) in enumerate(expected_data):
            if nodes[i].URI != expected_uri:
                print(f"❌ Node {i} URI mismatch: expected '{expected_uri}', got '{nodes[i].URI}'")
                return False
            if nodes[i].name != expected_name:
                print(f"❌ Node {i} name mismatch: expected '{expected_name}', got '{nodes[i].name}'")
                return False
                
        print(f"\n✅ @graph document conversion validation passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ from_jsonld_list() failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_from_jsonld_list_with_array():
    """Test from_jsonld_list() with plain array - should work correctly."""
    print("\n" + "=" * 60)
    print("Testing from_jsonld_list() - Plain Array")
    print("=" * 60)
    
    # Create test JSON-LD array
    jsonld_array = [
        {
            "@context": {
                "vital": "http://vital.ai/ontology/vital-core#",
                "type": "@type",
                "id": "@id"
            },
            "@id": "http://example.com/array-test-1",
            "@type": "vital:VITAL_Node",
            "vital:hasName": "Array Test 1"
        },
        {
            "@context": {
                "vital": "http://vital.ai/ontology/vital-core#",
                "type": "@type", 
                "id": "@id"
            },
            "@id": "http://example.com/array-test-2",
            "@type": "vital:VITAL_Node",
            "vital:hasName": "Array Test 2"
        }
    ]
    
    print(f"Test JSON-LD array:")
    print(json.dumps(jsonld_array, indent=2))
    
    # Test from_jsonld_list
    try:
        nodes = VITAL_Node.from_jsonld_list(jsonld_array)
        print(f"\n✅ from_jsonld_list() successful!")
        print(f"Created {len(nodes)} nodes from array:")
        for node in nodes:
            print(f"  - URI: {node.URI}, Name: {node.name}")
        
        # Validate conversion
        if len(nodes) != 2:
            print(f"❌ Expected 2 nodes, got {len(nodes)}")
            return False
            
        expected_data = [
            ("http://example.com/array-test-1", "Array Test 1"),
            ("http://example.com/array-test-2", "Array Test 2")
        ]
        
        for i, (expected_uri, expected_name) in enumerate(expected_data):
            if nodes[i].URI != expected_uri:
                print(f"❌ Node {i} URI mismatch: expected '{expected_uri}', got '{nodes[i].URI}'")
                return False
            if nodes[i].name != expected_name:
                print(f"❌ Node {i} name mismatch: expected '{expected_name}', got '{nodes[i].name}'")
                return False
                
        print(f"\n✅ Array conversion validation passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ from_jsonld_list() failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_from_jsonld_list_with_single_object():
    """Test from_jsonld_list() with single object - should return list with one item."""
    print("\n" + "=" * 60)
    print("Testing from_jsonld_list() - Single Object (returns list)")
    print("=" * 60)
    
    # Create test single JSON-LD object
    jsonld_obj = {
        "@context": {
            "vital": "http://vital.ai/ontology/vital-core#",
            "type": "@type",
            "id": "@id"
        },
        "@id": "http://example.com/single-to-list-test",
        "@type": "vital:VITAL_Node",
        "vital:hasName": "Single to List Test"
    }
    
    print(f"Test JSON-LD single object:")
    print(json.dumps(jsonld_obj, indent=2))
    
    # Test from_jsonld_list - should return list with one item
    try:
        nodes = VITAL_Node.from_jsonld_list(jsonld_obj)
        print(f"\n✅ from_jsonld_list() successful!")
        print(f"Created list with {len(nodes)} node(s):")
        for node in nodes:
            print(f"  - URI: {node.URI}, Name: {node.name}")
        
        # Validate conversion - should be list with one item
        if len(nodes) != 1:
            print(f"❌ Expected 1 node in list, got {len(nodes)}")
            return False
            
        node = nodes[0]
        if node.URI != "http://example.com/single-to-list-test":
            print(f"❌ URI mismatch: expected 'http://example.com/single-to-list-test', got '{node.URI}'")
            return False
            
        if node.name != "Single to List Test":
            print(f"❌ Name mismatch: expected 'Single to List Test', got '{node.name}'")
            return False
                
        print(f"\n✅ Single object to list conversion validation passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ from_jsonld_list() failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_round_trip_list():
    """Test round-trip conversion: List -> JSON-LD -> List."""
    print("\n" + "=" * 60)
    print("Testing Round-trip - List Operations")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create original objects
    originals = []
    for i in range(2):
        node = VITAL_Node()
        node.URI = f"http://example.com/round-trip-list-{i+1}"
        node.name = f"Round Trip List {i+1}"
        originals.append(node)
    
    print(f"Original Nodes:")
    for node in originals:
        print(f"  - URI: {node.URI}, Name: {node.name}")
    
    try:
        # Convert to JSON-LD document
        jsonld_doc = VITAL_Node.to_jsonld_list(originals)
        print(f"\n✅ Step 1: to_jsonld_list() successful")
        
        # Convert back to GraphObjects
        reconstructed = VITAL_Node.from_jsonld_list(jsonld_doc)
        print(f"✅ Step 2: from_jsonld_list() successful")
        
        print(f"\nReconstructed Nodes:")
        for node in reconstructed:
            print(f"  - URI: {node.URI}, Name: {node.name}")
        
        # Validate round-trip
        if len(originals) != len(reconstructed):
            print(f"\n❌ Length mismatch: expected {len(originals)}, got {len(reconstructed)}")
            return False
            
        all_match = True
        for orig, recon in zip(originals, reconstructed):
            if (orig.URI != recon.URI or 
                orig.name != recon.name or
                orig.get_class_uri() != recon.get_class_uri()):
                all_match = False
                break
        
        if all_match:
            print(f"\n✅ Round-trip list conversion successful!")
            return True
        else:
            print(f"\n❌ Round-trip list conversion failed - data mismatch")
            return False
            
    except Exception as e:
        print(f"\n❌ Round-trip list conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all list operations JSON-LD tests."""
    print("🧪 JSON-LD List Operations Tests")
    print("=" * 80)
    
    tests = [
        ("to_jsonld_list() Multiple Objects", test_to_jsonld_list),
        ("from_jsonld_list() @graph Document", test_from_jsonld_list_with_graph_document),
        ("from_jsonld_list() Plain Array", test_from_jsonld_list_with_array),
        ("from_jsonld_list() Single Object", test_from_jsonld_list_with_single_object),
        ("Round-trip List Operations", test_round_trip_list)
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
