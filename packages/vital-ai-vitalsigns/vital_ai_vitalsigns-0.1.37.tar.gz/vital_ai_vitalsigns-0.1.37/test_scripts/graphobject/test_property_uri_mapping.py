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


def test_property_setting_with_full_uri():
    """Test setting properties using full URIs vs short names."""
    print("=" * 60)
    print("Testing Property Setting with Full URIs")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create a VITAL_Node object
    node = VITAL_Node()
    node.URI = "http://example.com/test-node-1"
    
    print(f"Created Node:")
    print(f"  URI: {node.URI}")
    
    # Test 1: Set property using short name
    try:
        node.name = "Test Node Short Name"
        print(f"\n✅ Setting property with short name 'name' successful")
        print(f"  Value: {node.name}")
    except Exception as e:
        print(f"\n❌ Setting property with short name 'name' failed: {e}")
        return False
    
    # Test 2: Set property using full URI
    name_uri = "http://vital.ai/ontology/vital-core#hasName"
    try:
        setattr(node, name_uri, "Test Node Full URI")
        print(f"\n✅ Setting property with full URI successful")
        print(f"  URI: {name_uri}")
        print(f"  Value: {getattr(node, 'name')}")
        
        # Verify both ways of accessing give same result
        uri_value = getattr(node, name_uri)
        short_value = getattr(node, 'name')
        if uri_value == short_value:
            print(f"✅ Both access methods return same value: '{uri_value}'")
        else:
            print(f"❌ Access methods return different values: URI='{uri_value}', short='{short_value}'")
            return False
            
    except Exception as e:
        print(f"\n❌ Setting property with full URI failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_property_registry_lookup():
    """Test property registry lookup for various URIs."""
    print("\n" + "=" * 60)
    print("Testing Property Registry Lookup")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    registry = vs.get_registry()
    
    # Test common property URIs
    test_uris = [
        "http://vital.ai/ontology/vital-core#hasName",
        "http://vital.ai/ontology/vital-core#URIProp",
        "http://vital.ai/ontology/vital-core#vitaltype",
        "http://vital.ai/ontology/vital-core#hasTimestamp",
        "http://vital.ai/ontology/vital-core#isActive"
    ]
    
    print(f"Testing property registry lookup for common URIs:")
    
    for uri in test_uris:
        trait_cls = registry.vitalsigns_property_classes.get(uri, None)
        if trait_cls:
            print(f"✅ {uri}")
            print(f"   -> {trait_cls}")
        else:
            print(f"❌ {uri} -> NOT FOUND")
    
    # Test getting domain properties for VITAL_Node
    print(f"\nDomain properties for VITAL_Node:")
    node = VITAL_Node()
    domain_props = node.get_allowed_domain_properties()
    
    print(f"Found {len(domain_props)} domain properties:")
    for i, prop_info in enumerate(domain_props[:10]):  # Show first 10
        uri = prop_info['uri']
        prop_class = prop_info['prop_class']
        print(f"  {i+1}. {uri} -> {prop_class}")
    
    if len(domain_props) > 10:
        print(f"  ... and {len(domain_props) - 10} more")
    
    return True


def test_unknown_property_uri():
    """Test setting a property with an unknown URI."""
    print("\n" + "=" * 60)
    print("Testing Unknown Property URI")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create a VITAL_Node object
    node = VITAL_Node()
    node.URI = "http://example.com/test-node-unknown"
    
    # Test setting an unknown property URI
    unknown_uri = "http://example.com/unknown#someProperty"
    
    try:
        setattr(node, unknown_uri, "Unknown Property Value")
        print(f"✅ Setting unknown property URI succeeded")
        print(f"  URI: {unknown_uri}")
        print(f"  Value: {getattr(node, unknown_uri)}")
    except AttributeError as e:
        print(f"❌ Setting unknown property URI failed with AttributeError: {e}")
        print(f"  This is expected behavior for non-GraphContainerObject")
    except Exception as e:
        print(f"❌ Setting unknown property URI failed with unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_graph_container_object_properties():
    """Test property setting with GraphContainerObject (allows extern properties)."""
    print("\n" + "=" * 60)
    print("Testing GraphContainerObject Property Setting")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create a VITAL_GraphContainerObject
    container = VITAL_GraphContainerObject()
    container.URI = "http://example.com/test-container"
    
    print(f"Created GraphContainerObject:")
    print(f"  URI: {container.URI}")
    
    # Test 1: Set standard property with short name
    try:
        container.name = "Test Container"
        print(f"\n✅ Setting standard property 'name' successful")
        print(f"  Value: {container.name}")
    except Exception as e:
        print(f"\n❌ Setting standard property 'name' failed: {e}")
        return False
    
    # Test 2: Set standard property with full URI
    name_uri = "http://vital.ai/ontology/vital-core#hasName"
    try:
        setattr(container, name_uri, "Container Full URI Name")
        print(f"\n✅ Setting standard property with full URI successful")
        print(f"  Value: {getattr(container, 'name')}")
    except Exception as e:
        print(f"\n❌ Setting standard property with full URI failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Set extern property (should work for GraphContainerObject)
    try:
        container.custom_property = "Custom Value"
        print(f"\n✅ Setting extern property 'custom_property' successful")
        print(f"  Value: {container.custom_property}")
    except Exception as e:
        print(f"\n❌ Setting extern property failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Set unknown URI (should work as extern property)
    unknown_uri = "http://example.com/custom#customProperty"
    try:
        setattr(container, unknown_uri, "Unknown URI Value")
        print(f"\n✅ Setting unknown URI as extern property successful")
        print(f"  URI: {unknown_uri}")
        print(f"  Value: {getattr(container, unknown_uri)}")
    except Exception as e:
        print(f"\n❌ Setting unknown URI failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_rdf_style_property_setting():
    """Test property setting as it would happen during RDF/JSON-LD conversion."""
    print("\n" + "=" * 60)
    print("Testing RDF-Style Property Setting")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    registry = vs.get_registry()
    
    # Create a VITAL_Node object
    node = VITAL_Node()
    node.URI = "http://example.com/test-rdf-node"
    
    print(f"Created Node for RDF-style testing:")
    print(f"  URI: {node.URI}")
    
    # Simulate what happens in RDF conversion
    test_properties = [
        ("http://vital.ai/ontology/vital-core#hasName", "RDF Test Node"),
        ("http://vital.ai/ontology/vital-core#hasTimestamp", 1234567890),
        ("http://vital.ai/ontology/vital-core#isActive", True)
    ]
    
    for prop_uri, value in test_properties:
        print(f"\nTesting property: {prop_uri}")
        
        # Check if property is in registry (like RDF utils does)
        trait_cls = registry.vitalsigns_property_classes.get(prop_uri, None)
        print(f"  Registry lookup: {trait_cls}")
        
        # Try to set the property (like RDF utils does)
        try:
            setattr(node, prop_uri, value)
            print(f"  ✅ setattr() successful")
            print(f"  Value: {getattr(node, prop_uri)}")
            
            # Try to access via short name if possible
            domain_props = node.get_allowed_domain_properties()
            short_name = None
            for prop_info in domain_props:
                if prop_info['uri'] == prop_uri:
                    from vital_ai_vitalsigns.impl.vitalsigns_impl import VitalSignsImpl
                    trait_class = VitalSignsImpl.get_trait_class_from_uri(prop_uri)
                    if trait_class:
                        short_name = trait_class.get_short_name()
                        break
            
            if short_name:
                short_value = getattr(node, short_name)
                print(f"  Short name '{short_name}': {short_value}")
            
        except Exception as e:
            print(f"  ❌ setattr() failed: {e}")
            import traceback
            traceback.print_exc()
    
    return True


def test_jsonld_to_vitalsigns_conversion():
    """Test JSON-LD to VitalSigns object conversion with full property URIs."""
    print("\n" + "=" * 60)
    print("Testing JSON-LD to VitalSigns Conversion")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create test JSON-LD data with full property URIs (only using properties that exist in registry)
    jsonld_data = {
        "@context": {
            "vital": "http://vital.ai/ontology/vital-core#"
        },
        "@id": "http://example.com/test-jsonld-node",
        "@type": "vital:VITAL_Node",
        "vital:hasName": "JSON-LD Test Node",
        "vital:hasTimestamp": 1234567890,
        "vital:isActive": True,
        "vital:hasProvenance": "http://example.com/provenance"
    }
    
    print(f"Test JSON-LD data:")
    import json
    print(json.dumps(jsonld_data, indent=2))
    
    # Test 1: Try to convert using from_jsonld
    try:
        from vital_ai_vitalsigns.model.VITAL_Node import VITAL_Node
        node = VITAL_Node.from_jsonld(jsonld_data)
        
        print(f"\n✅ JSON-LD conversion successful!")
        print(f"Created Node:")
        print(f"  URI: {node.URI}")
        print(f"  Type: {type(node).__name__}")
        
        # Check if properties were set correctly
        try:
            print(f"  Name: {node.name}")
        except AttributeError:
            print(f"  Name: NOT SET")
            
        try:
            print(f"  Timestamp: {node.timestamp}")
        except AttributeError:
            print(f"  Timestamp: NOT SET")
            
        try:
            print(f"  Active: {node.isActive}")
        except AttributeError:
            print(f"  Active: NOT SET")
            
        # Check for provenance property
        try:
            prov = getattr(node, "http://vital.ai/ontology/vital-core#hasProvenance")
            print(f"  Provenance (full URI): {prov}")
        except AttributeError:
            print(f"  Provenance (full URI): NOT SET")
            
        try:
            prov = getattr(node, "provenance")
            print(f"  Provenance (short name): {prov}")
        except AttributeError:
            print(f"  Provenance (short name): NOT SET")
        
        # Show all properties that were actually set
        print(f"\nActual properties set:")
        for key in node.keys():
            try:
                value = getattr(node, key)
                print(f"    {key}: {value}")
            except:
                print(f"    {key}: <error accessing>")
                
        return True
        
    except Exception as e:
        print(f"\n❌ JSON-LD conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_jsonld_expanded_format():
    """Test JSON-LD conversion with expanded format (full URIs without context)."""
    print("\n" + "=" * 60)
    print("Testing JSON-LD Expanded Format Conversion")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create test JSON-LD data in expanded format (no @context, full URIs)
    jsonld_expanded = {
        "@id": "http://example.com/test-expanded-node",
        "@type": ["http://vital.ai/ontology/vital-core#VITAL_Node"],
        "http://vital.ai/ontology/vital-core#hasName": [{"@value": "Expanded JSON-LD Node"}],
        "http://vital.ai/ontology/vital-core#hasTimestamp": [{"@value": 9876543210}],
        "http://vital.ai/ontology/vital-core#isActive": [{"@value": True}],
        "http://vital.ai/ontology/vital-core#vitaltype": [{"@id": "http://vital.ai/ontology/vital-core#VITAL_Node"}]
    }
    
    print(f"Test JSON-LD expanded data:")
    import json
    print(json.dumps(jsonld_expanded, indent=2))
    
    # Test conversion
    try:
        from vital_ai_vitalsigns.model.VITAL_Node import VITAL_Node
        node = VITAL_Node.from_jsonld(jsonld_expanded)
        
        print(f"\n✅ Expanded JSON-LD conversion successful!")
        print(f"Created Node:")
        print(f"  URI: {node.URI}")
        print(f"  Type: {type(node).__name__}")
        
        # Check properties
        try:
            print(f"  Name: {node.name}")
        except AttributeError:
            print(f"  Name: NOT SET")
            
        try:
            print(f"  Timestamp: {node.timestamp}")
        except AttributeError:
            print(f"  Timestamp: NOT SET")
            
        try:
            print(f"  Active: {node.isActive}")
        except AttributeError:
            print(f"  Active: NOT SET")
        
        # Show all properties
        print(f"\nAll properties:")
        for key in node.keys():
            try:
                value = getattr(node, key)
                print(f"    {key}: {value}")
            except:
                print(f"    {key}: <error accessing>")
                
        return True
        
    except Exception as e:
        print(f"\n❌ Expanded JSON-LD conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_manual_rdf_conversion():
    """Test the manual RDF conversion process that JSON-LD uses internally."""
    print("\n" + "=" * 60)
    print("Testing Manual RDF Conversion Process")
    print("=" * 60)
    
    # Initialize VitalSigns
    vs = VitalSigns()
    
    # Create RDF triples as they would appear from JSON-LD conversion
    rdf_triples = """
<http://example.com/test-rdf-node> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vital.ai/ontology/vital-core#VITAL_Node> .
<http://example.com/test-rdf-node> <http://vital.ai/ontology/vital-core#vitaltype> <http://vital.ai/ontology/vital-core#VITAL_Node> .
<http://example.com/test-rdf-node> <http://vital.ai/ontology/vital-core#URIProp> <http://example.com/test-rdf-node> .
<http://example.com/test-rdf-node> <http://vital.ai/ontology/vital-core#hasName> "Manual RDF Test Node" .
<http://example.com/test-rdf-node> <http://vital.ai/ontology/vital-core#hasTimestamp> "1111111111"^^<http://www.w3.org/2001/XMLSchema#integer> .
<http://example.com/test-rdf-node> <http://vital.ai/ontology/vital-core#isActive> "true"^^<http://www.w3.org/2001/XMLSchema#boolean> .
"""
    
    print(f"Test RDF triples:")
    print(rdf_triples)
    
    # Test direct RDF conversion
    try:
        from vital_ai_vitalsigns.model.VITAL_Node import VITAL_Node
        node = VITAL_Node.from_rdf(rdf_triples)
        
        print(f"\n✅ RDF conversion successful!")
        print(f"Created Node:")
        print(f"  URI: {node.URI}")
        print(f"  Type: {type(node).__name__}")
        
        # Check properties
        try:
            print(f"  Name: {node.name}")
        except AttributeError:
            print(f"  Name: NOT SET")
            
        try:
            print(f"  Timestamp: {node.timestamp}")
        except AttributeError:
            print(f"  Timestamp: NOT SET")
            
        try:
            print(f"  Active: {node.isActive}")
        except AttributeError:
            print(f"  Active: NOT SET")
        
        # Show internal properties
        print(f"\nInternal _properties:")
        for key, prop in node._properties.items():
            print(f"    {key}: {prop} -> {prop.value}")
                
        return True
        
    except Exception as e:
        print(f"\n❌ RDF conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all property URI mapping tests."""
    print("Property URI Mapping Test Suite")
    print("Testing GraphObject property setting with full URIs vs short names")
    
    test_results = []
    
    try:
        # Run all tests
        test_results.append(("Full URI Property Setting", test_property_setting_with_full_uri()))
        test_results.append(("Property Registry Lookup", test_property_registry_lookup()))
        test_results.append(("Unknown Property URI", test_unknown_property_uri()))
        test_results.append(("GraphContainerObject Properties", test_graph_container_object_properties()))
        test_results.append(("RDF-Style Property Setting", test_rdf_style_property_setting()))
        test_results.append(("JSON-LD to VitalSigns Conversion", test_jsonld_to_vitalsigns_conversion()))
        test_results.append(("JSON-LD Expanded Format", test_jsonld_expanded_format()))
        test_results.append(("Manual RDF Conversion", test_manual_rdf_conversion()))
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:<30} {status}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print(f"\nTotal Tests: {len(test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        if failed == 0:
            print("\n🎉 All property URI mapping tests passed!")
            print("=" * 60)
            return 0
        else:
            print(f"\n❌ {failed} test(s) failed!")
            print("=" * 60)
            return 1
        
    except Exception as e:
        print(f"\n❌ Property URI mapping test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
