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


def test_json_single_object():
    """Test JSON conversion for a single GraphObject."""
    print("=" * 60)
    print("Testing JSON Single Object Conversion")
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
    
    # Test to_json with pretty print
    try:
        json_data = node.to_json(pretty_print=True)
        print(f"\n✅ to_json(pretty_print=True) successful!")
        print(f"JSON Output (pretty):")
        print(json_data)
        
        # Test to_json without pretty print
        json_compact = node.to_json(pretty_print=False)
        print(f"\n✅ to_json(pretty_print=False) successful!")
        print(f"JSON Output (compact):")
        print(json_compact)
        
        # Test from_json
        try:
            reconstructed_node = VITAL_Node.from_json(json_data)
            print(f"\n✅ from_json() successful!")
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
            print(f"\n❌ from_json() failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"\n❌ to_json() failed: {e}")
        import traceback
        traceback.print_exc()


def test_json_map_conversion():
    """Test JSON map (dict) conversion."""
    print("\n" + "=" * 60)
    print("Testing JSON Map Conversion")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create test JSON map
    json_map = {
        "type": "http://vital.ai/ontology/vital-core#VITAL_Node",
        "URI": "http://example.com/map-test-node",
        "http://vital.ai/ontology/vital-core#URIProp": "http://example.com/map-test-node",
        "http://vital.ai/ontology/vital-core#hasName": "Map Test Node",
        "http://vital.ai/ontology/vital-core#vitaltype": "http://vital.ai/ontology/vital-core#VITAL_Node"
    }
    
    print(f"Test JSON Map:")
    print(json.dumps(json_map, indent=2))
    
    # Test from_json_map
    try:
        node = VITAL_Node.from_json_map(json_map)
        print(f"\n✅ from_json_map() successful!")
        print(f"Created Node:")
        print(f"  URI: {node.URI}")
        print(f"  Name: {node.name}")
        print(f"  Class: {node.get_class_uri()}")
        
        # Test round-trip via to_dict
        try:
            node_dict = node.to_dict()
            print(f"\n✅ Round-trip via to_dict() successful!")
            print(f"Node as dict:")
            print(json.dumps(node_dict, indent=2))
            
        except Exception as e:
            print(f"\n❌ Round-trip via to_dict() failed: {e}")
            
    except Exception as e:
        print(f"\n❌ from_json_map() failed: {e}")
        import traceback
        traceback.print_exc()


def test_json_list_conversion():
    """Test JSON list conversion."""
    print("\n" + "=" * 60)
    print("Testing JSON List Conversion")
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
    
    # Convert to JSON list
    try:
        json_list = []
        for node in nodes:
            json_str = node.to_json(pretty_print=False)
            json_obj = json.loads(json_str)
            json_list.append(json_obj)
        
        json_list_str = json.dumps(json_list, indent=2)
        print(f"\n✅ JSON list creation successful!")
        print(f"JSON List (first 500 chars):")
        print(json_list_str[:500] + "..." if len(json_list_str) > 500 else json_list_str)
        
        # Test from_json_list
        try:
            reconstructed_nodes = VITAL_Node.from_json_list(json_list_str)
            print(f"\n✅ from_json_list() successful!")
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
            print(f"\n❌ from_json_list() failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"\n❌ JSON list creation failed: {e}")


def test_vitalsigns_json_methods():
    """Test JSON methods through VitalSigns interface."""
    print("\n" + "=" * 60)
    print("Testing VitalSigns JSON Methods")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create test JSON string
    json_str = """{
        "type": "http://vital.ai/ontology/vital-core#VITAL_Node",
        "URI": "http://example.com/vs-test-node",
        "http://vital.ai/ontology/vital-core#URIProp": "http://example.com/vs-test-node",
        "http://vital.ai/ontology/vital-core#hasName": "VitalSigns Test Node",
        "http://vital.ai/ontology/vital-core#vitaltype": "http://vital.ai/ontology/vital-core#VITAL_Node"
    }"""
    
    print(f"Test JSON string:")
    print(json_str)
    
    # Test VitalSigns from_json
    try:
        node = vs.from_json(json_str)
        print(f"\n✅ VitalSigns.from_json() successful!")
        print(f"Created Node:")
        print(f"  URI: {node.URI}")
        print(f"  Name: {node.name}")
        print(f"  Class: {node.get_class_uri()}")
        
        # Test VitalSigns from_json_list
        try:
            json_list_str = f"[{json_str}]"
            node_list = vs.from_json_list(json_list_str)
            print(f"\n✅ VitalSigns.from_json_list() successful!")
            print(f"Created {len(node_list)} nodes from JSON list")
            
        except Exception as e:
            print(f"\n❌ VitalSigns.from_json_list() failed: {e}")
            
    except Exception as e:
        print(f"\n❌ VitalSigns.from_json() failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all JSON tests."""
    print("JSON Functionality Test Suite")
    print("Using vital-core ontology only")
    
    try:
        # Test individual functions
        test_json_single_object()
        test_json_map_conversion()
        test_json_list_conversion()
        test_vitalsigns_json_methods()
        
        print("\n" + "=" * 60)
        print("✅ All JSON tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ JSON test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
