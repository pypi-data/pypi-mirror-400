#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from vital_ai_vitalsigns.vitalsigns import VitalSigns
from vital_ai_vitalsigns.model.VITAL_Node import VITAL_Node
from vital_ai_vitalsigns.model.VITAL_Edge import VITAL_Edge
from vital_ai_vitalsigns.model.VITAL_GraphContainerObject import VITAL_GraphContainerObject
from vital_ai_vitalsigns.model.utils.graphobject_equality_utils import GraphObjectEqualityUtils


def test_identical_objects():
    """Test equality with identical objects."""
    print("=" * 60)
    print("Testing Identical Objects Equality")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create two identical VITAL_Node objects
    node1 = VITAL_Node()
    node1.URI = "http://example.com/test-node-1"
    node1.name = "Test Node 1"
    
    node2 = VITAL_Node()
    node2.URI = "http://example.com/test-node-1"
    node2.name = "Test Node 1"
    
    print(f"Node 1:")
    print(f"  URI: {node1.URI}")
    print(f"  Name: {node1.name}")
    print(f"  Class: {node1.get_class_uri()}")
    
    print(f"\nNode 2:")
    print(f"  URI: {node2.URI}")
    print(f"  Name: {node2.name}")
    print(f"  Class: {node2.get_class_uri()}")
    
    # Test equality
    result = GraphObjectEqualityUtils.equals(node1, node2)
    print(f"\nEquality Result: {result}")
    
    if result:
        print("✅ Identical objects correctly identified as equal!")
    else:
        print("❌ Identical objects incorrectly identified as not equal!")
        return False
    
    return True


def test_different_uris():
    """Test inequality with different URIs."""
    print("\n" + "=" * 60)
    print("Testing Different URIs Inequality")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create two VITAL_Node objects with different URIs
    node1 = VITAL_Node()
    node1.URI = "http://example.com/test-node-1"
    node1.name = "Test Node"
    
    node2 = VITAL_Node()
    node2.URI = "http://example.com/test-node-2"
    node2.name = "Test Node"
    
    print(f"Node 1:")
    print(f"  URI: {node1.URI}")
    print(f"  Name: {node1.name}")
    
    print(f"\nNode 2:")
    print(f"  URI: {node2.URI}")
    print(f"  Name: {node2.name}")
    
    # Test equality
    result = GraphObjectEqualityUtils.equals(node1, node2)
    print(f"\nEquality Result: {result}")
    
    if not result:
        print("✅ Objects with different URIs correctly identified as not equal!")
    else:
        print("❌ Objects with different URIs incorrectly identified as equal!")
        return False
    
    return True


def test_different_properties():
    """Test inequality with different property values."""
    print("\n" + "=" * 60)
    print("Testing Different Properties Inequality")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create two VITAL_Node objects with different names
    node1 = VITAL_Node()
    node1.URI = "http://example.com/test-node-1"
    node1.name = "Test Node One"
    
    node2 = VITAL_Node()
    node2.URI = "http://example.com/test-node-1"
    node2.name = "Test Node Two"
    
    print(f"Node 1:")
    print(f"  URI: {node1.URI}")
    print(f"  Name: {node1.name}")
    
    print(f"\nNode 2:")
    print(f"  URI: {node2.URI}")
    print(f"  Name: {node2.name}")
    
    # Test equality
    result = GraphObjectEqualityUtils.equals(node1, node2)
    print(f"\nEquality Result: {result}")
    
    if not result:
        print("✅ Objects with different properties correctly identified as not equal!")
    else:
        print("❌ Objects with different properties incorrectly identified as equal!")
        return False
    
    return True


def test_null_handling():
    """Test null handling cases."""
    print("\n" + "=" * 60)
    print("Testing Null Handling")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create a VITAL_Node object
    node = VITAL_Node()
    node.URI = "http://example.com/test-node-1"
    node.name = "Test Node"
    
    print(f"Created Node:")
    print(f"  URI: {node.URI}")
    print(f"  Name: {node.name}")
    
    # Test null vs null
    result1 = GraphObjectEqualityUtils.equals(None, None)
    print(f"\nNull vs Null: {result1}")
    
    # Test node vs null
    result2 = GraphObjectEqualityUtils.equals(node, None)
    print(f"Node vs Null: {result2}")
    
    # Test null vs node
    result3 = GraphObjectEqualityUtils.equals(None, node)
    print(f"Null vs Node: {result3}")
    
    if result1 and not result2 and not result3:
        print("✅ Null handling works correctly!")
    else:
        print("❌ Null handling failed!")
        print(f"  Expected: True, False, False")
        print(f"  Got: {result1}, {result2}, {result3}")
        return False
    
    return True


def test_different_types():
    """Test inequality with different object types."""
    print("\n" + "=" * 60)
    print("Testing Different Object Types")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create a VITAL_Node and VITAL_Edge with same URI
    node = VITAL_Node()
    node.URI = "http://example.com/test-object-1"
    node.name = "Test Object"
    
    edge = VITAL_Edge()
    edge.URI = "http://example.com/test-object-1"
    edge.name = "Test Object"
    
    print(f"Node:")
    print(f"  URI: {node.URI}")
    print(f"  Name: {node.name}")
    print(f"  Type: {type(node).__name__}")
    
    print(f"\nEdge:")
    print(f"  URI: {edge.URI}")
    print(f"  Name: {edge.name}")
    print(f"  Type: {type(edge).__name__}")
    
    # Test equality
    result = GraphObjectEqualityUtils.equals(node, edge)
    print(f"\nEquality Result: {result}")
    
    if not result:
        print("✅ Objects of different types correctly identified as not equal!")
    else:
        print("❌ Objects of different types incorrectly identified as equal!")
        return False
    
    return True


def test_container_objects():
    """Test GraphContainerObject with extern properties."""
    print("\n" + "=" * 60)
    print("Testing GraphContainerObject Extern Properties")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create two VITAL_GraphContainerObject instances
    container1 = VITAL_GraphContainerObject()
    container1.URI = "http://example.com/container-1"
    container1.name = "Test Container"
    
    container2 = VITAL_GraphContainerObject()
    container2.URI = "http://example.com/container-1"
    container2.name = "Test Container"
    
    print(f"Container 1:")
    print(f"  URI: {container1.URI}")
    print(f"  Name: {container1.name}")
    
    print(f"\nContainer 2:")
    print(f"  URI: {container2.URI}")
    print(f"  Name: {container2.name}")
    
    # Test equality without extern properties
    result1 = GraphObjectEqualityUtils.equals(container1, container2)
    print(f"\nEquality without extern properties: {result1}")
    
    # Add same extern properties to both
    try:
        setattr(container1, 'custom_prop1', 'value1')
        setattr(container1, 'custom_prop2', 42)
        setattr(container2, 'custom_prop1', 'value1')
        setattr(container2, 'custom_prop2', 42)
        
        print(f"\nAdded extern properties:")
        print(f"  custom_prop1: 'value1'")
        print(f"  custom_prop2: 42")
        
        # Test equality with same extern properties
        result2 = GraphObjectEqualityUtils.equals(container1, container2)
        print(f"\nEquality with same extern properties: {result2}")
        
        # Add different extern property to container2
        setattr(container2, 'custom_prop3', 'different')
        
        print(f"\nAdded different extern property to container2:")
        print(f"  custom_prop3: 'different'")
        
        # Test equality with different extern properties
        result3 = GraphObjectEqualityUtils.equals(container1, container2)
        print(f"\nEquality with different extern properties: {result3}")
        
        if result1 and result2 and not result3:
            print("✅ GraphContainerObject extern properties handling works correctly!")
        else:
            print("❌ GraphContainerObject extern properties handling failed!")
            print(f"  Expected: True, True, False")
            print(f"  Got: {result1}, {result2}, {result3}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing extern properties: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_self_equality():
    """Test that an object equals itself."""
    print("\n" + "=" * 60)
    print("Testing Self Equality")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create a VITAL_Node object
    node = VITAL_Node()
    node.URI = "http://example.com/test-node-1"
    node.name = "Test Node"
    
    print(f"Node:")
    print(f"  URI: {node.URI}")
    print(f"  Name: {node.name}")
    
    # Test self equality
    result = GraphObjectEqualityUtils.equals(node, node)
    print(f"\nSelf Equality Result: {result}")
    
    if result:
        print("✅ Object correctly equals itself!")
    else:
        print("❌ Object does not equal itself!")
        return False
    
    return True


def test_complex_properties():
    """Test objects with multiple properties."""
    print("\n" + "=" * 60)
    print("Testing Complex Properties")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create two VITAL_Node objects with multiple properties
    node1 = VITAL_Node()
    node1.URI = "http://example.com/complex-node-1"
    node1.name = "Complex Test Node"
    # Add timestamp if available
    try:
        node1.timestamp = 1234567890
    except:
        pass
    
    node2 = VITAL_Node()
    node2.URI = "http://example.com/complex-node-1"
    node2.name = "Complex Test Node"
    # Add same timestamp
    try:
        node2.timestamp = 1234567890
    except:
        pass
    
    print(f"Node 1:")
    print(f"  URI: {node1.URI}")
    print(f"  Name: {node1.name}")
    try:
        print(f"  Timestamp: {node1.timestamp}")
    except:
        print(f"  Timestamp: Not available")
    
    print(f"\nNode 2:")
    print(f"  URI: {node2.URI}")
    print(f"  Name: {node2.name}")
    try:
        print(f"  Timestamp: {node2.timestamp}")
    except:
        print(f"  Timestamp: Not available")
    
    # Test equality
    result = GraphObjectEqualityUtils.equals(node1, node2)
    print(f"\nEquality Result: {result}")
    
    if result:
        print("✅ Complex objects with multiple properties correctly identified as equal!")
    else:
        print("❌ Complex objects with multiple properties incorrectly identified as not equal!")
        return False
    
    return True


def main():
    """Run all equality tests."""
    print("GraphObject Equality Test Suite")
    print("Testing GraphObjectEqualityUtils functionality")
    
    test_results = []
    
    try:
        # Run all tests
        test_results.append(("Identical Objects", test_identical_objects()))
        test_results.append(("Different URIs", test_different_uris()))
        test_results.append(("Different Properties", test_different_properties()))
        test_results.append(("Null Handling", test_null_handling()))
        test_results.append(("Different Types", test_different_types()))
        test_results.append(("Container Objects", test_container_objects()))
        test_results.append(("Self Equality", test_self_equality()))
        test_results.append(("Complex Properties", test_complex_properties()))
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:<25} {status}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print(f"\nTotal Tests: {len(test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        if failed == 0:
            print("\n🎉 All equality tests passed!")
            print("=" * 60)
            return 0
        else:
            print(f"\n❌ {failed} test(s) failed!")
            print("=" * 60)
            return 1
        
    except Exception as e:
        print(f"\n❌ Equality test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
