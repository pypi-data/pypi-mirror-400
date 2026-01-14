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


def test_jsonld_single_object():
    """Test JSON-LD conversion for a single GraphObject."""
    print("=" * 60)
    print("Testing JSON-LD Single Object Conversion")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create a test VITAL_Node object
    node = VITAL_Node()
    node.URI = "http://example.com/test-node-1"
    node.name = "Test Node 1"
    
    print(f"Created VITAL_Node:")
    print(f"  URI: {node.URI}")
    print(f"  Name: {node.name}")
    print(f"  Class: {node.get_class_uri()}")
    
    # Test to_jsonld
    try:
        jsonld_data = node.to_jsonld()
        print(f"\n✅ to_jsonld() successful!")
        print(f"JSON-LD Output:")
        print(json.dumps(jsonld_data, indent=2))
        
        # Test from_jsonld
        try:
            reconstructed_node = VITAL_Node.from_jsonld(jsonld_data)
            print(f"\n✅ from_jsonld() successful!")
            print(f"Reconstructed Node:")
            print(f"  URI: {reconstructed_node.URI}")
            print(f"  Name: {reconstructed_node.name}")
            print(f"  Class: {reconstructed_node.get_class_uri()}")
            
            # Verify round-trip
            if (node.URI == reconstructed_node.URI and 
                node.name == reconstructed_node.name and
                node.get_class_uri() == reconstructed_node.get_class_uri()):
                print(f"\n✅ Round-trip conversion successful!")
            else:
                print(f"\n❌ Round-trip conversion failed - data mismatch")
                
        except Exception as e:
            print(f"\n❌ from_jsonld() failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"\n❌ to_jsonld() failed: {e}")
        import traceback
        traceback.print_exc()


def test_jsonld_multiple_objects():
    """Test JSON-LD conversion for multiple GraphObjects."""
    print("\n" + "=" * 60)
    print("Testing JSON-LD Multiple Objects Conversion")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create multiple test objects
    nodes = []
    for i in range(3):
        node = VITAL_Node()
        node.URI = f"http://example.com/test-node-{i+1}"
        node.name = f"Test Node {i+1}"
        nodes.append(node)
    
    print(f"Created {len(nodes)} VITAL_Node objects:")
    for node in nodes:
        print(f"  - URI: {node.URI}, Name: {node.name}")
    
    # Test to_jsonld_list
    try:
        jsonld_doc = VITAL_Node.to_jsonld_list(nodes)
        print(f"\n✅ to_jsonld_list() successful!")
        print(f"JSON-LD Document:")
        print(json.dumps(jsonld_doc, indent=2))
        
        # Test from_jsonld_list
        try:
            reconstructed_nodes = VITAL_Node.from_jsonld_list(jsonld_doc)
            print(f"\n✅ from_jsonld_list() successful!")
            print(f"Reconstructed {len(reconstructed_nodes)} nodes:")
            for node in reconstructed_nodes:
                print(f"  - URI: {node.URI}, Name: {node.name}")
            
            # Verify round-trip
            if len(nodes) == len(reconstructed_nodes):
                all_match = True
                for orig, recon in zip(nodes, reconstructed_nodes):
                    if (orig.URI != recon.URI or 
                        orig.name != recon.name or
                        orig.get_class_uri() != recon.get_class_uri()):
                        all_match = False
                        break
                
                if all_match:
                    print(f"\n✅ Round-trip list conversion successful!")
                else:
                    print(f"\n❌ Round-trip list conversion failed - data mismatch")
            else:
                print(f"\n❌ Round-trip list conversion failed - count mismatch")
                
        except Exception as e:
            print(f"\n❌ from_jsonld_list() failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"\n❌ to_jsonld_list() failed: {e}")
        import traceback
        traceback.print_exc()


def test_vitalsigns_jsonld_methods():
    """Test JSON-LD methods through VitalSigns interface."""
    print("\n" + "=" * 60)
    print("Testing VitalSigns JSON-LD Methods")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create test data
    node_dict = {
        "@context": {
            "vital": "http://vital.ai/ontology/vital-core#",
            "type": "@type"
        },
        "@id": "http://example.com/vs-test-node",
        "type": "http://vital.ai/ontology/vital-core#VITAL_Node",
        "http://vital.ai/ontology/vital-core#URIProp": "http://example.com/vs-test-node",
        "http://vital.ai/ontology/vital-core#hasName": "VitalSigns Test Node"
    }
    
    print(f"Test JSON-LD data:")
    print(json.dumps(node_dict, indent=2))
    
    # Test VitalSigns from_jsonld
    try:
        node = vs.from_jsonld(node_dict)
        print(f"\n✅ VitalSigns.from_jsonld() successful!")
        print(f"Created Node:")
        print(f"  URI: {node.URI}")
        print(f"  Name: {node.name}")
        print(f"  Class: {node.get_class_uri()}")
        
        # Test VitalSigns from_jsonld_list
        try:
            node_list = vs.from_jsonld_list([node_dict])
            print(f"\n✅ VitalSigns.from_jsonld_list() successful!")
            print(f"Created {len(node_list)} nodes from list")
            
        except Exception as e:
            print(f"\n❌ VitalSigns.from_jsonld_list() failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"\n❌ VitalSigns.from_jsonld() failed: {e}")
        import traceback
        traceback.print_exc()


def test_context_generation():
    """Test the dynamic context generation."""
    print("\n" + "=" * 60)
    print("Testing Dynamic Context Generation")
    print("=" * 60)
    
    from vital_ai_vitalsigns.model.utils.graphobject_jsonld_utils import GraphObjectJsonldUtils
    
    # Test context generation
    try:
        context = GraphObjectJsonldUtils._get_default_context()
        print(f"✅ Context generation successful!")
        print(f"Generated context:")
        print(json.dumps(context, indent=2))
        
        # Check for expected built-in namespaces
        expected_builtins = ["rdf", "rdfs", "owl", "xsd", "type", "id"]
        missing_builtins = [ns for ns in expected_builtins if ns not in context]
        
        if not missing_builtins:
            print(f"\n✅ All expected built-in namespaces present")
        else:
            print(f"\n⚠️  Missing built-in namespaces: {missing_builtins}")
            
        # Check for ontology namespaces
        ontology_namespaces = [k for k, v in context.items() 
                             if k not in expected_builtins and "vital.ai" in str(v)]
        
        if ontology_namespaces:
            print(f"✅ Found ontology namespaces: {ontology_namespaces}")
        else:
            print(f"⚠️  No ontology namespaces found (this is expected if only vital-core is loaded)")
            
    except Exception as e:
        print(f"❌ Context generation failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all JSON-LD tests."""
    print("JSON-LD Functionality Test Suite")
    print("Using vital-core ontology only")
    
    try:
        # Test individual functions
        test_context_generation()
        test_jsonld_single_object()
        test_jsonld_multiple_objects()
        test_vitalsigns_jsonld_methods()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
