"""
Property operations test suite
"""

import time

from cmissh.tck.suite import TCKTestSuite


def create_property_suite() -> TCKTestSuite:
    """Create the property operations test suite"""
    suite = TCKTestSuite("properties", "Property Operations")

    def setup(context):
        """Create test folder"""
        root = context["repository"].getRootFolder()
        folder_name = f"cmis_tck_props_{int(time.time() * 1000)}"
        test_folder = root.createFolder(
            folder_name, {"cmis:objectTypeId": "cmis:folder"}
        )
        context["suite_data"]["test_folder"] = test_folder

    def teardown(context):
        """Cleanup"""
        if "test_folder" in context["suite_data"]:
            try:
                context["suite_data"]["test_folder"].deleteTree()
            except Exception:
                pass

    suite.set_setup(setup)
    suite.set_teardown(teardown)

    suite.add_test("begin", "Initialize suite", lambda ctx: None)

    # Test 1: get_properties
    def test_get_props(context):
        """Test getting all properties"""
        folder = context["suite_data"]["test_folder"]
        props = folder.getProperties()
        assert props is not None
        assert "cmis:objectId" in props
        assert "cmis:name" in props
        assert "cmis:objectTypeId" in props
        assert "cmis:baseTypeId" in props

    suite.add_test("get_properties", "Get all properties", test_get_props)

    # Test 2: update_name
    def test_update_name(context):
        """Test updating name property"""
        folder = context["suite_data"]["test_folder"]
        new_name = f"renamed_{int(time.time())}"
        folder.updateProperties({"cmis:name": new_name})
        folder.reload()
        assert folder.getName() == new_name

    suite.add_test(
        "update_name",
        "Update name property",
        test_update_name,
        depends_on="get_properties",
    )

    # Test 3: update_custom_property
    def test_update_custom(context):
        """Test updating custom property"""
        folder = context["suite_data"]["test_folder"]
        try:
            # Try to set a custom property if supported
            folder.updateProperties({"cmis:description": "Test description"})
            folder.reload()
            props = folder.getProperties()
            # Some servers may not support this
            if "cmis:description" in props:
                assert props["cmis:description"] == "Test description"
        except Exception as e:
            if "not allowed" in str(e).lower() or "not supported" in str(e).lower():
                msg = "Custom property updates not supported"
                raise AssertionError(msg)
            raise

    suite.add_test("update_custom", "Update custom property", test_update_custom)

    suite.add_test("finish", "Finalize suite", lambda ctx: None)

    return suite
