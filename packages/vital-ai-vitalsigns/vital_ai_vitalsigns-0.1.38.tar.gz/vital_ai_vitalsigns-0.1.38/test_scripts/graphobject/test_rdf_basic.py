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


def test_rdf_single_object():
    """Test RDF conversion for a single GraphObject."""
    print("=" * 60)
    print("Testing RDF Single Object Conversion")
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
    
    # Test to_rdf with different formats
    formats = ['nt', 'turtle']
    
    for fmt in formats:
        try:
            rdf_data = node.to_rdf(format=fmt)
            print(f"\n✅ to_rdf(format='{fmt}') successful!")
            print(f"RDF Output ({fmt}):")
            print(rdf_data[:200] + "..." if len(rdf_data) > 200 else rdf_data)
            
            # Test from_rdf
            try:
                reconstructed_node = VITAL_Node.from_rdf(rdf_data)
                print(f"✅ from_rdf() successful for {fmt}!")
                print(f"Reconstructed Node:")
                print(f"  URI: {reconstructed_node.URI}")
                print(f"  Name: {reconstructed_node.name}")
                print(f"  Class: {reconstructed_node.get_class_uri()}")
                
                # Verify round-trip
                if (node.URI == reconstructed_node.URI and 
                    node.name == reconstructed_node.name and
                    node.get_class_uri() == reconstructed_node.get_class_uri()):
                    print(f"✅ Round-trip conversion successful for {fmt}!")
                else:
                    print(f"❌ Round-trip conversion failed for {fmt} - data mismatch")
                    
            except Exception as e:
                print(f"❌ from_rdf() failed for {fmt}: {e}")
                
        except Exception as e:
            print(f"❌ to_rdf(format='{fmt}') failed: {e}")


def test_rdf_multiple_objects():
    """Test RDF conversion for multiple GraphObjects."""
    print("\n" + "=" * 60)
    print("Testing RDF Multiple Objects Conversion")
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
    
    # Test from_rdf_list
    try:
        # First create RDF strings for each node
        rdf_strings = []
        for node in nodes:
            rdf_data = node.to_rdf(format='nt')
            rdf_strings.append(rdf_data)
        
        # Combine all RDF data
        combined_rdf = "\n".join(rdf_strings)
        print(f"\n✅ Combined RDF generation successful!")
        print(f"Combined RDF (first 300 chars):")
        print(combined_rdf[:300] + "..." if len(combined_rdf) > 300 else combined_rdf)
        
        # Test from_rdf_list
        try:
            reconstructed_nodes = VITAL_Node.from_rdf_list(combined_rdf)
            print(f"\n✅ from_rdf_list() successful!")
            print(f"Reconstructed {len(reconstructed_nodes)} nodes:")
            for node in reconstructed_nodes:
                print(f"  - URI: {node.URI}, Name: {node.name}")
            
            # Verify round-trip
            if len(nodes) == len(reconstructed_nodes):
                print(f"✅ Round-trip list conversion successful!")
            else:
                print(f"❌ Round-trip list conversion failed - count mismatch")
                
        except Exception as e:
            print(f"❌ from_rdf_list() failed: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ RDF list generation failed: {e}")


def test_vitalsigns_rdf_methods():
    """Test RDF methods through VitalSigns interface."""
    print("\n" + "=" * 60)
    print("Testing VitalSigns RDF Methods")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create test RDF data
    rdf_data = """<http://example.com/vs-test-node> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vital.ai/ontology/vital-core#VITAL_Node> .
<http://example.com/vs-test-node> <http://vital.ai/ontology/vital-core#URIProp> <http://example.com/vs-test-node> .
<http://example.com/vs-test-node> <http://vital.ai/ontology/vital-core#hasName> "VitalSigns Test Node" .
<http://example.com/vs-test-node> <http://vital.ai/ontology/vital-core#vitaltype> <http://vital.ai/ontology/vital-core#VITAL_Node> ."""
    
    print(f"Test RDF data:")
    print(rdf_data)
    
    # Test VitalSigns from_rdf
    try:
        node = vs.from_rdf(rdf_data)
        print(f"\n✅ VitalSigns.from_rdf() successful!")
        print(f"Created Node:")
        print(f"  URI: {node.URI}")
        print(f"  Name: {node.name}")
        print(f"  Class: {node.get_class_uri()}")
        
        # Test VitalSigns from_rdf_list
        try:
            node_list = vs.from_rdf_list(rdf_data)
            print(f"\n✅ VitalSigns.from_rdf_list() successful!")
            print(f"Created {len(node_list)} nodes from RDF")
            
        except Exception as e:
            print(f"\n❌ VitalSigns.from_rdf_list() failed: {e}")
            
    except Exception as e:
        print(f"\n❌ VitalSigns.from_rdf() failed: {e}")
        import traceback
        traceback.print_exc()


def test_rdf_with_graph_uri():
    """Test RDF conversion with graph URI."""
    print("\n" + "=" * 60)
    print("Testing RDF with Graph URI")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create a test node
    node = VITAL_Node()
    node.URI = "http://example.com/graph-test-node"
    node.name = "Graph Test Node"
    
    graph_uri = "http://example.com/test-graph"
    
    print(f"Created VITAL_Node with graph URI: {graph_uri}")
    print(f"  URI: {node.URI}")
    print(f"  Name: {node.name}")
    
    # Test to_rdf with graph_uri
    try:
        rdf_data = node.to_rdf(format='turtle', graph_uri=graph_uri)
        print(f"\n✅ to_rdf() with graph_uri successful!")
        print(f"RDF Output with graph URI:")
        print(rdf_data)
        
    except Exception as e:
        print(f"\n❌ to_rdf() with graph_uri failed: {e}")


def main():
    """Run all RDF tests."""
    print("RDF Functionality Test Suite")
    print("Using vital-core ontology only")
    
    try:
        # Test individual functions
        test_rdf_single_object()
        test_rdf_multiple_objects()
        test_vitalsigns_rdf_methods()
        test_rdf_with_graph_uri()
        
        print("\n" + "=" * 60)
        print("✅ All RDF tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ RDF test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
