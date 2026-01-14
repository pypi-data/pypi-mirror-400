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
from vital_ai_vitalsigns.model.vital_constants import VitalConstants


def test_uri_to_id_conversion():
    """Test VitalSigns URI property -> JSON-LD @id conversion."""
    print("=" * 60)
    print("Testing URI -> @id Conversion")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create node with URI
    node = VITAL_Node()
    test_uri = "http://example.com/identifier-test-uri"
    node.URI = test_uri
    node.name = "URI Test Node"
    
    print(f"Created node with URI: {node.URI}")
    print(f"Internal URI property: {node._properties.get(VitalConstants.uri_prop_uri)}")
    
    # Convert to JSON-LD
    try:
        jsonld_obj = node.to_jsonld()
        print(f"\n✅ to_jsonld() successful")
        
        # Check that @id is present and matches URI
        if "@id" not in jsonld_obj:
            print(f"❌ Missing @id in JSON-LD output")
            return False
            
        if jsonld_obj["@id"] != test_uri:
            print(f"❌ @id mismatch: expected '{test_uri}', got '{jsonld_obj['@id']}'")
            return False
            
        print(f"✅ @id correctly set to: {jsonld_obj['@id']}")
        
        # Verify no URI field in JSON-LD (should be @id only)
        if "URI" in jsonld_obj:
            print(f"❌ Unexpected 'URI' field in JSON-LD (should be '@id' only)")
            return False
            
        print(f"✅ No 'URI' field in JSON-LD (correctly using @id)")
        return True
        
    except Exception as e:
        print(f"\n❌ URI -> @id conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_id_to_uri_conversion():
    """Test JSON-LD @id -> VitalSigns URI property conversion."""
    print("\n" + "=" * 60)
    print("Testing @id -> URI Conversion")
    print("=" * 60)
    
    # Create JSON-LD with @id
    test_id = "http://example.com/identifier-test-id"
    jsonld_obj = {
        "@context": {
            "vital": "http://vital.ai/ontology/vital-core#",
            "type": "@type",
            "id": "@id"
        },
        "@id": test_id,
        "@type": "vital:VITAL_Node",
        "vital:hasName": "ID Test Node"
    }
    
    print(f"JSON-LD with @id: {test_id}")
    
    # Convert from JSON-LD
    try:
        node = VITAL_Node.from_jsonld(jsonld_obj)
        print(f"\n✅ from_jsonld() successful")
        
        # Check that URI property is set correctly
        if not hasattr(node, 'URI') or node.URI != test_id:
            print(f"❌ URI property mismatch: expected '{test_id}', got '{getattr(node, 'URI', 'NOT SET')}'")
            return False
            
        print(f"✅ URI property correctly set to: {node.URI}")
        
        # Check internal property storage
        internal_uri = node._properties.get(VitalConstants.uri_prop_uri)
        if internal_uri != test_id:
            print(f"❌ Internal URI property mismatch: expected '{test_id}', got '{internal_uri}'")
            return False
            
        print(f"✅ Internal URI property correctly set: {internal_uri}")
        return True
        
    except Exception as e:
        print(f"\n❌ @id -> URI conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_identifier_round_trip():
    """Test identifier consistency through round-trip conversion."""
    print("\n" + "=" * 60)
    print("Testing Identifier Round-trip Consistency")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Test multiple URIs with different formats
    test_uris = [
        "http://example.com/simple-uri",
        "https://secure.example.com/secure-uri",
        "http://example.com/path/with/segments",
        "http://example.com/uri-with-fragment#fragment",
        "urn:uuid:12345678-1234-5678-9012-123456789012"
    ]
    
    passed = 0
    total = len(test_uris)
    
    for i, test_uri in enumerate(test_uris):
        print(f"\n🔍 Testing URI {i+1}: {test_uri}")
        
        try:
            # Create original node
            original = VITAL_Node()
            original.URI = test_uri
            original.name = f"Round Trip Test {i+1}"
            
            # Convert to JSON-LD
            jsonld_obj = original.to_jsonld()
            
            # Verify @id in JSON-LD
            if jsonld_obj.get("@id") != test_uri:
                print(f"❌ JSON-LD @id mismatch: expected '{test_uri}', got '{jsonld_obj.get('@id')}'")
                continue
                
            # Convert back to GraphObject
            reconstructed = VITAL_Node.from_jsonld(jsonld_obj)
            
            # Verify URI in reconstructed object
            if reconstructed.URI != test_uri:
                print(f"❌ Reconstructed URI mismatch: expected '{test_uri}', got '{reconstructed.URI}'")
                continue
                
            # Verify internal property consistency
            orig_internal = original._properties.get(VitalConstants.uri_prop_uri)
            recon_internal = reconstructed._properties.get(VitalConstants.uri_prop_uri)
            
            if orig_internal != recon_internal:
                print(f"❌ Internal property mismatch: '{orig_internal}' != '{recon_internal}'")
                continue
                
            print(f"✅ Round-trip successful: {test_uri}")
            passed += 1
            
        except Exception as e:
            print(f"❌ Round-trip failed: {e}")
    
    print(f"\n📊 Round-trip Results: {passed}/{total} URIs passed")
    return passed == total


def test_list_identifier_consistency():
    """Test identifier consistency in list operations."""
    print("\n" + "=" * 60)
    print("Testing List Identifier Consistency")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create multiple nodes with different URIs
    nodes = []
    test_uris = [
        "http://example.com/list-node-1",
        "http://example.com/list-node-2", 
        "http://example.com/list-node-3"
    ]
    
    for i, uri in enumerate(test_uris):
        node = VITAL_Node()
        node.URI = uri
        node.name = f"List Node {i+1}"
        nodes.append(node)
    
    print(f"Created {len(nodes)} nodes with URIs:")
    for node in nodes:
        print(f"  - {node.URI}")
    
    try:
        # Convert to JSON-LD list
        jsonld_doc = VITAL_Node.to_jsonld_list(nodes)
        print(f"\n✅ to_jsonld_list() successful")
        
        # Verify @id fields in @graph
        if "@graph" not in jsonld_doc:
            print(f"❌ Missing @graph in document")
            return False
            
        graph_objects = jsonld_doc["@graph"]
        if len(graph_objects) != len(test_uris):
            print(f"❌ @graph length mismatch: expected {len(test_uris)}, got {len(graph_objects)}")
            return False
            
        # Check each object's @id
        for i, (obj, expected_uri) in enumerate(zip(graph_objects, test_uris)):
            if obj.get("@id") != expected_uri:
                print(f"❌ Object {i} @id mismatch: expected '{expected_uri}', got '{obj.get('@id')}'")
                return False
                
        print(f"✅ All @id fields correct in @graph")
        
        # Convert back to list
        reconstructed_nodes = VITAL_Node.from_jsonld_list(jsonld_doc)
        print(f"✅ from_jsonld_list() successful")
        
        # Verify URIs in reconstructed objects
        if len(reconstructed_nodes) != len(test_uris):
            print(f"❌ Reconstructed list length mismatch: expected {len(test_uris)}, got {len(reconstructed_nodes)}")
            return False
            
        for i, (node, expected_uri) in enumerate(zip(reconstructed_nodes, test_uris)):
            if node.URI != expected_uri:
                print(f"❌ Reconstructed node {i} URI mismatch: expected '{expected_uri}', got '{node.URI}'")
                return False
                
        print(f"✅ All reconstructed URIs correct")
        print(f"✅ List identifier consistency validated")
        return True
        
    except Exception as e:
        print(f"\n❌ List identifier consistency test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_missing_identifier_handling():
    """Test handling of objects without identifiers."""
    print("\n" + "=" * 60)
    print("Testing Missing Identifier Handling")
    print("=" * 60)
    
    # Test node without URI - should fail
    print("🔍 Testing node without URI")
    try:
        node = VITAL_Node()
        node.name = "Node Without URI"
        
        # Should fail because URI is required
        jsonld_obj = node.to_jsonld()
        print(f"❌ to_jsonld() should have failed for node without URI")
        return False
            
    except ValueError as e:
        if "missing URI property" in str(e):
            print(f"✅ to_jsonld() correctly failed for node without URI: {e}")
        else:
            print(f"❌ Wrong error message: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error type: {type(e).__name__}: {e}")
        return False
    
    # Test JSON-LD without @id - should fail
    print("\n🔍 Testing JSON-LD without @id")
    try:
        jsonld_obj = {
            "@context": {
                "vital": "http://vital.ai/ontology/vital-core#",
                "type": "@type"
            },
            "@type": "vital:VITAL_Node",
            "vital:hasName": "Node Without ID"
        }
        
        node = VITAL_Node.from_jsonld(jsonld_obj)
        print(f"❌ from_jsonld() should have failed for JSON-LD without @id")
        return False
            
    except ValueError as e:
        if "missing @id property" in str(e):
            print(f"✅ from_jsonld() correctly failed for JSON-LD without @id: {e}")
        else:
            print(f"❌ Wrong error message: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error type: {type(e).__name__}: {e}")
        return False
    
    print(f"\n✅ Missing identifier handling validated")
    return True


def run_all_tests():
    """Run all identifier consistency tests."""
    print("🧪 JSON-LD Identifier Consistency Tests")
    print("=" * 80)
    
    tests = [
        ("URI -> @id Conversion", test_uri_to_id_conversion),
        ("@id -> URI Conversion", test_id_to_uri_conversion),
        ("Identifier Round-trip", test_identifier_round_trip),
        ("List Identifier Consistency", test_list_identifier_consistency),
        ("Missing Identifier Handling", test_missing_identifier_handling)
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
        print("🎉 All identifier consistency tests passed!")
        return True
    else:
        print("💥 Some identifier consistency tests failed!")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
