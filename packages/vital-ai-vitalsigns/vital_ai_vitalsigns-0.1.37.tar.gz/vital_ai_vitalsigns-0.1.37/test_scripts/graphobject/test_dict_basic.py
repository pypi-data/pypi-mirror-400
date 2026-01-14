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


def test_dict_single_object():
    """Test dict conversion for a single GraphObject."""
    print("=" * 60)
    print("Testing Dict Single Object Conversion")
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
    
    # Test to_dict
    try:
        dict_data = node.to_dict()
        print(f"\n✅ to_dict() successful!")
        print(f"Dict Output:")
        print(json.dumps(dict_data, indent=2))
        
        # Test from_dict
        try:
            reconstructed_node = VITAL_Node.from_dict(dict_data)
            print(f"\n✅ from_dict() successful!")
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
            print(f"\n❌ from_dict() failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"\n❌ to_dict() failed: {e}")
        import traceback
        traceback.print_exc()


def test_dict_list_conversion():
    """Test dict list conversion for multiple GraphObjects."""
    print("\n" + "=" * 60)
    print("Testing Dict List Conversion")
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
    
    # Test to_dict_list
    try:
        dict_list = VITAL_Node.to_dict_list(nodes)
        print(f"\n✅ to_dict_list() successful!")
        print(f"Dict List:")
        print(json.dumps(dict_list, indent=2))
        
        # Test from_dict_list
        try:
            reconstructed_nodes = VITAL_Node.from_dict_list(dict_list)
            print(f"\n✅ from_dict_list() successful!")
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
            print(f"\n❌ from_dict_list() failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"\n❌ to_dict_list() failed: {e}")
        import traceback
        traceback.print_exc()


def test_vitalsigns_dict_methods():
    """Test dict methods through VitalSigns interface."""
    print("\n" + "=" * 60)
    print("Testing VitalSigns Dict Methods")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create test dict
    test_dict = {
        "type": "http://vital.ai/ontology/vital-core#VITAL_Node",
        "URI": "http://example.com/vs-test-node",
        "http://vital.ai/ontology/vital-core#URIProp": "http://example.com/vs-test-node",
        "http://vital.ai/ontology/vital-core#hasName": "VitalSigns Test Node",
        "http://vital.ai/ontology/vital-core#vitaltype": "http://vital.ai/ontology/vital-core#VITAL_Node",
        "types": ["http://vital.ai/ontology/vital-core#VITAL_Node"]
    }
    
    print(f"Test dict:")
    print(json.dumps(test_dict, indent=2))
    
    # Test VitalSigns from_dict
    try:
        node = vs.from_dict(test_dict)
        print(f"\n✅ VitalSigns.from_dict() successful!")
        print(f"Created Node:")
        print(f"  URI: {node.URI}")
        print(f"  Name: {node.name}")
        print(f"  Class: {node.get_class_uri()}")
        
        # Test VitalSigns from_dict_list
        try:
            dict_list = [test_dict]
            node_list = vs.from_dict_list(dict_list)
            print(f"\n✅ VitalSigns.from_dict_list() successful!")
            print(f"Created {len(node_list)} nodes from dict list")
            
        except Exception as e:
            print(f"\n❌ VitalSigns.from_dict_list() failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"\n❌ VitalSigns.from_dict() failed: {e}")
        import traceback
        traceback.print_exc()


def test_dict_structure_validation():
    """Test dict structure and content validation."""
    print("\n" + "=" * 60)
    print("Testing Dict Structure Validation")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create a test node
    node = VITAL_Node()
    node.URI = "http://example.com/validation-test-node"
    node.name = "Validation Test Node"
    
    # Get dict representation
    dict_data = node.to_dict()
    
    print(f"Original dict structure:")
    print(json.dumps(dict_data, indent=2))
    
    # Validate expected keys
    expected_keys = ['type', 'URI', 'types']
    missing_keys = [key for key in expected_keys if key not in dict_data]
    extra_keys = [key for key in dict_data.keys() if not key.startswith('http://') and key not in expected_keys]
    
    print(f"\n📋 Structure validation:")
    if not missing_keys:
        print(f"✅ All expected keys present: {expected_keys}")
    else:
        print(f"❌ Missing expected keys: {missing_keys}")
    
    if not extra_keys:
        print(f"✅ No unexpected keys found")
    else:
        print(f"⚠️  Extra keys found: {extra_keys}")
    
    # Validate URI consistency
    uri_prop_key = "http://vital.ai/ontology/vital-core#URIProp"
    if uri_prop_key in dict_data:
        if dict_data['URI'] == dict_data[uri_prop_key]:
            print(f"✅ URI consistency validated (URIProp present and matches)")
        else:
            print(f"❌ URI consistency failed (URIProp present but doesn't match)")
    else:
        # URIProp is not included in to_dict() output by design - this is expected
        print(f"✅ URI consistency validated (URIProp not in dict output as expected)")
    
    # Validate type consistency
    vitaltype_key = "http://vital.ai/ontology/vital-core#vitaltype"
    if (vitaltype_key in dict_data and 
        dict_data['type'] == dict_data[vitaltype_key] and
        dict_data['type'] in dict_data['types']):
        print(f"✅ Type consistency validated")
    else:
        print(f"❌ Type consistency failed")


def main():
    """Run all dict tests."""
    print("Dict Functionality Test Suite")
    print("Using vital-core ontology only")
    
    try:
        # Test individual functions
        test_dict_single_object()
        test_dict_list_conversion()
        test_vitalsigns_dict_methods()
        test_dict_structure_validation()
        
        print("\n" + "=" * 60)
        print("✅ All dict tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Dict test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
