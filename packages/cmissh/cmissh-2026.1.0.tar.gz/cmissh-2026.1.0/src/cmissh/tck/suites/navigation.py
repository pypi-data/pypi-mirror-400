"""
Navigation operations test suite
"""

import time

from cmissh.tck.suite import TCKTestSuite


def create_navigation_suite() -> TCKTestSuite:
    """Create the navigation operations test suite"""
    suite = TCKTestSuite("navigation", "Navigation Operations")

    def setup(context):
        """Create test structure"""
        root = context["repository"].getRootFolder()
        folder_name = f"cmis_tck_nav_{int(time.time() * 1000)}"
        test_folder = root.createFolder(
            folder_name, {"cmis:objectTypeId": "cmis:folder"}
        )

        # Create some structure
        sub1 = test_folder.createFolder("sub1", {"cmis:objectTypeId": "cmis:folder"})
        sub2 = test_folder.createFolder("sub2", {"cmis:objectTypeId": "cmis:folder"})
        subsub = sub1.createFolder("subsub", {"cmis:objectTypeId": "cmis:folder"})

        from io import BytesIO

        sub1.createDocument(
            "doc1.txt",
            {"cmis:objectTypeId": "cmis:document"},
            contentFile=BytesIO(b"content1"),
        )
        subsub.createDocument(
            "doc2.txt",
            {"cmis:objectTypeId": "cmis:document"},
            contentFile=BytesIO(b"content2"),
        )

        context["suite_data"]["test_folder"] = test_folder
        context["suite_data"]["sub1"] = sub1
        context["suite_data"]["subsub"] = subsub

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

    # Test 1: get_object_by_id
    def test_get_by_id(context):
        """Test getting object by ID"""
        folder = context["suite_data"]["test_folder"]
        obj_id = folder.getObjectId()
        obj = context["repository"].getObject(obj_id)
        assert obj is not None
        assert obj.getObjectId() == obj_id

    suite.add_test("get_by_id", "Get object by ID", test_get_by_id)

    # Test 2: get_object_by_path
    def test_get_by_path(context):
        """Test getting object by path"""
        folder = context["suite_data"]["test_folder"]
        path = folder.getPaths()[0]
        obj = context["repository"].getObjectByPath(path)
        assert obj is not None
        assert obj.getObjectId() == folder.getObjectId()

    suite.add_test("get_by_path", "Get object by path", test_get_by_path)

    # Test 3: navigate_parent
    def test_navigate_parent(context):
        """Test navigating to parent"""
        subsub = context["suite_data"]["subsub"]
        parent = subsub.getParent()
        assert parent is not None
        assert parent.getObjectId() == context["suite_data"]["sub1"].getObjectId()

    suite.add_test("navigate_parent", "Navigate to parent", test_navigate_parent)

    # Test 4: get_descendants
    def test_get_descendants(context):
        """Test getting descendants"""
        if not context["capabilities"].get("GetDescendants", False):
            msg = "GetDescendants not supported"
            raise AssertionError(msg)

        folder = context["suite_data"]["test_folder"]
        try:
            descendants = folder.getDescendants(depth=2)
            assert descendants is not None
            # Should have at least 2 folders and 2 documents
            assert len(list(descendants)) >= 4
        except AttributeError:
            msg = "getDescendants method not implemented"
            raise AssertionError(msg)

    suite.add_test(
        "get_descendants",
        "Get descendants",
        test_get_descendants,
        required_capability="GetDescendants",
    )

    # Test 5: get_folder_parent
    def test_folder_parent(context):
        """Test getting folder parent"""
        folder = context["suite_data"]["test_folder"]
        parent = folder.getParent()
        assert parent is not None
        # Should be root
        root = context["repository"].getRootFolder()
        assert parent.getObjectId() == root.getObjectId()

    suite.add_test("folder_parent", "Get folder parent", test_folder_parent)

    suite.add_test("finish", "Finalize suite", lambda ctx: None)

    return suite
