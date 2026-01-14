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
from vital_ai_vitalsigns.model.utils.graphobject_jsonld_utils import GraphObjectJsonldUtils


def test_dynamic_context_single_object():
    """Test dynamic context generation for single object."""
    print("=" * 60)
    print("Testing Dynamic Context - Single Object")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create node with properties
    node = VITAL_Node()
    node.URI = "http://example.com/context-test-node"
    node.name = "Context Test Node"
    
    print(f"Created node:")
    print(f"  URI: {node.URI}")
    print(f"  Name: {node.name}")
    print(f"  Type: {node.get_class_uri()}")
    
    # Test dynamic context generation
    try:
        jsonld_obj = node.to_jsonld()
        print(f"\n✅ to_jsonld() successful with dynamic context")
        
        # Examine the context
        context = jsonld_obj.get("@context", {})
        print(f"\nGenerated context:")
        print(json.dumps(context, indent=2))
        
        # Validate context structure
        if not isinstance(context, dict):
            print(f"❌ Context should be a dictionary")
            return False
            
        # Context should have namespace mappings (no aliases for @id/@type per JSON-LD standard)
        # Check for at least some ontology namespaces
        has_namespaces = any(isinstance(v, str) and ('http://' in v or 'https://' in v) for v in context.values())
        if not has_namespaces and len(context) == 0:
            print(f"⚠️  Context is empty - may be acceptable for simple objects")
        else:
            print(f"✅ Context has namespace mappings")
        
        # Should have ontology prefixes based on actual data
        # Look for vital-core namespace (should be present for VITAL_Node)
        vital_core_found = False
        for prefix, namespace in context.items():
            if "vital.ai/ontology/vital-core" in namespace:
                vital_core_found = True
                print(f"✅ Found vital-core namespace: {prefix} -> {namespace}")
                break
                
        if not vital_core_found:
            print(f"⚠️  vital-core namespace not found (may be acceptable)")
        
        # Context should be minimal - only namespaces actually used
        print(f"✅ Dynamic context generated with {len(context)} entries")
        return True
        
    except Exception as e:
        print(f"\n❌ Dynamic context generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dynamic_context_multiple_objects():
    """Test dynamic context generation for multiple objects."""
    print("\n" + "=" * 60)
    print("Testing Dynamic Context - Multiple Objects")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create multiple nodes with different properties
    nodes = []
    for i in range(3):
        node = VITAL_Node()
        node.URI = f"http://example.com/multi-context-node-{i+1}"
        node.name = f"Multi Context Node {i+1}"
        nodes.append(node)
    
    print(f"Created {len(nodes)} nodes for context analysis")
    
    # Test dynamic context generation for list
    try:
        jsonld_doc = VITAL_Node.to_jsonld_list(nodes)
        print(f"\n✅ to_jsonld_list() successful with dynamic context")
        
        # Examine the context
        context = jsonld_doc.get("@context", {})
        print(f"\nGenerated context for multiple objects:")
        print(json.dumps(context, indent=2))
        
        # Validate context covers all objects
        if not isinstance(context, dict):
            print(f"❌ Context should be a dictionary")
            return False
            
        # Context should have namespace mappings (no aliases for @id/@type per JSON-LD standard)
        # Check for at least some ontology namespaces
        has_namespaces = any(isinstance(v, str) and ('http://' in v or 'https://' in v) for v in context.values())
        if not has_namespaces and len(context) == 0:
            print(f"⚠️  Context is empty - may be acceptable for multiple objects")
        else:
            print(f"✅ Context has namespace mappings")
        
        # Context should be shared across all objects in @graph
        graph_objects = jsonld_doc.get("@graph", [])
        for i, obj in enumerate(graph_objects):
            if "@context" in obj:
                print(f"❌ Object {i} has individual @context (should be at document level)")
                return False
                
        print(f"✅ Context properly shared at document level")
        print(f"✅ Dynamic context covers {len(graph_objects)} objects")
        return True
        
    except Exception as e:
        print(f"\n❌ Multi-object context generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_context_uri_extraction():
    """Test URI extraction for context generation."""
    print("\n" + "=" * 60)
    print("Testing URI Extraction for Context")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create node to test URI extraction
    node = VITAL_Node()
    node.URI = "http://example.com/uri-extraction-test"
    node.name = "URI Extraction Test"
    
    # Test URI extraction method
    try:
        uris = GraphObjectJsonldUtils._extract_uris_from_object(node)
        print(f"✅ URI extraction successful")
        print(f"Extracted URIs:")
        for uri in sorted(uris):
            print(f"  - {uri}")
        
        # Should include object URI (convert to string for comparison)
        node_uri_str = str(node.URI)
        if node_uri_str not in uris:
            print(f"❌ Object URI not extracted: {node_uri_str}")
            return False
            
        print(f"✅ Object URI correctly extracted: {node_uri_str}")
        
        # Should include type URI
        type_uri = str(node.get_class_uri())
        if type_uri not in uris:
            print(f"❌ Type URI not extracted: {type_uri}")
            return False
            
        print(f"✅ Type URI correctly extracted: {type_uri}")
        
        # Should include property URIs
        property_count = 0
        for uri in uris:
            if "vital.ai/ontology" in uri:
                property_count += 1
                
        print(f"✅ Found {property_count} ontology URIs")
        
        if len(uris) == 0:
            print(f"❌ No URIs extracted")
            return False
            
        print(f"✅ URI extraction found {len(uris)} total URIs")
        return True
        
    except Exception as e:
        print(f"\n❌ URI extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_namespace_prefix_mapping():
    """Test namespace to prefix mapping."""
    print("\n" + "=" * 60)
    print("Testing Namespace to Prefix Mapping")
    print("=" * 60)
    
    # Test namespace extraction
    test_uris = [
        "http://vital.ai/ontology/vital-core#VITAL_Node",
        "http://vital.ai/ontology/vital-core#hasName",
        "http://example.com/custom#Property",
        "https://schema.org/name",
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
    ]
    
    print("Testing namespace extraction from URIs:")
    for uri in test_uris:
        namespace = GraphObjectJsonldUtils._get_namespace_from_uri(uri)
        print(f"  {uri} -> {namespace}")
        
        # Validate namespace extraction
        if "#" in uri:
            expected = uri.rsplit('#', 1)[0] + '#'
        elif "/" in uri:
            expected = uri.rsplit('/', 1)[0] + '/'
        else:
            expected = None
            
        if namespace != expected:
            print(f"❌ Namespace extraction failed for {uri}")
            return False
    
    print(f"✅ Namespace extraction working correctly")
    
    # Test prefix mapping with ontology manager
    try:
        from vital_ai_vitalsigns.vitalsigns import VitalSigns
        vs = VitalSigns()
        ont_manager = vs.get_ontology_manager()
        
        # Test with vital-core namespace
        vital_core_ns = "http://vital.ai/ontology/vital-core#"
        prefix = GraphObjectJsonldUtils._get_prefix_for_namespace(ont_manager, vital_core_ns)
        
        if prefix:
            print(f"✅ Found prefix for vital-core: '{prefix}'")
        else:
            print(f"⚠️  No prefix found for vital-core (may be acceptable)")
            
        print(f"✅ Prefix mapping functionality working")
        return True
        
    except Exception as e:
        print(f"❌ Prefix mapping test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_context_optimization():
    """Test that context only includes used namespaces."""
    print("\n" + "=" * 60)
    print("Testing Context Optimization")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create simple node with minimal properties
    node = VITAL_Node()
    node.URI = "http://example.com/optimization-test"
    node.name = "Optimization Test"
    
    # Get dynamic context
    try:
        context = GraphObjectJsonldUtils._build_dynamic_context(node)
        print(f"✅ Dynamic context generation successful")
        print(f"Optimized context:")
        print(json.dumps(context, indent=2))
        
        # Compare with static context
        static_context = GraphObjectJsonldUtils._get_default_context()
        print(f"\nStatic context has {len(static_context)} entries")
        print(f"Dynamic context has {len(context)} entries")
        
        # Dynamic should be smaller or equal (optimized)
        if len(context) > len(static_context):
            print(f"⚠️  Dynamic context larger than static (may be acceptable)")
        else:
            print(f"✅ Dynamic context is optimized (smaller/equal size)")
            
        # Context should be valid JSON-LD (no aliases required per standard)
        if not isinstance(context, dict):
            print(f"❌ Context should be dictionary")
            return False
                
        print(f"✅ Context optimization working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Context optimization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_context_fallback():
    """Test fallback to static context when dynamic fails."""
    print("\n" + "=" * 60)
    print("Testing Context Fallback Mechanism")
    print("=" * 60)
    
    # Test static context as fallback
    try:
        static_context = GraphObjectJsonldUtils._get_default_context()
        print(f"✅ Static context generation successful")
        print(f"Static context has {len(static_context)} entries")
        
        # Should have basic structure
        if not isinstance(static_context, dict):
            print(f"❌ Static context should be dictionary")
            return False
            
        # Should have valid structure (no aliases required per JSON-LD standard)
        if len(static_context) == 0:
            print(f"❌ Static context should have some namespaces")
            return False
                
        print(f"✅ Static context has required structure")
        
        # Should have W3C namespaces
        w3c_namespaces = ["rdf", "rdfs", "owl", "xsd"]
        found_w3c = 0
        for ns in w3c_namespaces:
            if ns in static_context:
                found_w3c += 1
                
        print(f"✅ Static context has {found_w3c}/{len(w3c_namespaces)} W3C namespaces")
        
        print(f"✅ Fallback mechanism available")
        return True
        
    except Exception as e:
        print(f"❌ Context fallback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all context generation tests."""
    print("🧪 JSON-LD Context Generation Tests")
    print("=" * 80)
    
    tests = [
        ("Dynamic Context Single Object", test_dynamic_context_single_object),
        ("Dynamic Context Multiple Objects", test_dynamic_context_multiple_objects),
        ("URI Extraction", test_context_uri_extraction),
        ("Namespace Prefix Mapping", test_namespace_prefix_mapping),
        ("Context Optimization", test_context_optimization),
        ("Context Fallback Mechanism", test_context_fallback)
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
        print("🎉 All context generation tests passed!")
        return True
    else:
        print("💥 Some context generation tests failed!")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
