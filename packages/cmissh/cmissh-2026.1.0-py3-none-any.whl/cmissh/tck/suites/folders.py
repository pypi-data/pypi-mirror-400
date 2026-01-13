"""
Folder operations test suite
"""

import time

from cmissh.tck.suite import TCKTestSuite


def create_folder_suite() -> TCKTestSuite:
    """Create the folder operations test suite"""
    suite = TCKTestSuite("folders", "Folder Operations")

    def setup(context):
        """Create test folder"""
        root = context["repository"].getRootFolder()
        folder_name = f"cmis_tck_folders_{int(time.time() * 1000)}"
        test_folder = root.createFolder(
            folder_name, {"cmis:objectTypeId": "cmis:folder"}
        )
        context["suite_data"]["test_folder"] = test_folder

    def teardown(context):
        """Cleanup test folder"""
        if "test_folder" in context["suite_data"]:
            try:
                context["suite_data"]["test_folder"].deleteTree()
            except Exception:
                pass

    suite.set_setup(setup)
    suite.set_teardown(teardown)

    # Test 0: begin
    suite.add_test("begin", "Initialize suite", lambda ctx: None)

    # Test 1: create_subfolder
    def test_create_subfolder(context):
        """Test creating subfolder"""
        parent = context["suite_data"]["test_folder"]
        subfolder = parent.createFolder(
            "subfolder1", {"cmis:objectTypeId": "cmis:folder"}
        )
        assert subfolder is not None
        assert subfolder.getName() == "subfolder1"
        context["suite_data"]["subfolder"] = subfolder

    suite.add_test("create_subfolder", "Create subfolder", test_create_subfolder)

    # Test 2: get_parent
    def test_get_parent(context):
        """Test getting parent folder"""
        subfolder = context["suite_data"]["subfolder"]
        parent = subfolder.getParent()
        assert parent is not None
        assert (
            parent.getObjectId() == context["suite_data"]["test_folder"].getObjectId()
        )

    suite.add_test(
        "get_parent",
        "Get parent folder",
        test_get_parent,
        depends_on="create_subfolder",
    )

    # Test 3: get_children
    def test_get_children(context):
        """Test listing folder children"""
        parent = context["suite_data"]["test_folder"]
        children = list(parent.getChildren())
        assert len(children) >= 1
        found = any(c.getName() == "subfolder1" for c in children)
        assert found, "Subfolder not found in children"

    suite.add_test(
        "get_children", "Get children", test_get_children, depends_on="create_subfolder"
    )

    # Test 4: get_folder_tree
    def test_get_folder_tree(context):
        """Test getting folder tree"""
        if not context["capabilities"].get("GetFolderTree", False):
            msg = "GetFolderTree not supported"
            raise AssertionError(msg)

        parent = context["suite_data"]["test_folder"]
        try:
            tree = parent.getTree(depth=2)
            assert tree is not None
        except AttributeError:
            # Method might not be implemented
            msg = "getTree method not implemented"
            raise AssertionError(msg)

    suite.add_test(
        "get_folder_tree",
        "Get folder tree",
        test_get_folder_tree,
        required_capability="GetFolderTree",
        depends_on="create_subfolder",
    )

    # Test 5: delete_empty_folder
    def test_delete_empty_folder(context):
        """Test deleting empty folder"""
        subfolder = context["suite_data"]["subfolder"]
        subfolder.delete()

    suite.add_test(
        "delete_empty",
        "Delete empty folder",
        test_delete_empty_folder,
        depends_on="get_children",
    )

    # Test 6: create_nested_structure
    def test_create_nested(context):
        """Test creating nested folder structure"""
        parent = context["suite_data"]["test_folder"]
        level1 = parent.createFolder("level1", {"cmis:objectTypeId": "cmis:folder"})
        level2 = level1.createFolder("level2", {"cmis:objectTypeId": "cmis:folder"})
        level3 = level2.createFolder("level3", {"cmis:objectTypeId": "cmis:folder"})
        assert level3 is not None
        context["suite_data"]["nested_folder"] = level1

    suite.add_test("create_nested", "Create nested structure", test_create_nested)

    # Test 7: delete_tree
    def test_delete_tree(context):
        """Test deleting folder tree"""
        folder = context["suite_data"]["nested_folder"]
        folder.deleteTree()

    suite.add_test(
        "delete_tree",
        "Delete folder tree",
        test_delete_tree,
        depends_on="create_nested",
    )

    # Test 8: finish
    suite.add_test("finish", "Finalize suite", lambda ctx: None)

    return suite
