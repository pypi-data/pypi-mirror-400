"""
Basic CMIS operations test suite
"""

import time

from cmissh.tck.suite import TCKTestSuite


def create_basic_suite() -> TCKTestSuite:
    """Create the basic operations test suite"""
    suite = TCKTestSuite("basic", "Basic CMIS Operations")

    def setup(context):
        """Suite setup"""
        context["start_time"] = time.time()

    def teardown(context):
        """Suite cleanup"""
        # Clean up any test artifacts
        if "test_folder" in context["suite_data"]:
            try:
                context["suite_data"]["test_folder"].deleteTree()
            except Exception:
                pass

    suite.set_setup(setup)
    suite.set_teardown(teardown)

    # Test 0: begin
    def test_begin(context):
        """Initialize test suite"""
        assert context["client"] is not None
        assert context["repository"] is not None

    suite.add_test("begin", "Initialize test suite", test_begin)

    # Test 1: connect
    def test_connect(context):
        """Test connection to CMIS server"""
        repo_info = context["repository"].getRepositoryInfo()
        assert repo_info is not None
        assert repo_info.get("repositoryId") is not None

    suite.add_test("connect", "Connect to CMIS server", test_connect)

    # Test 2: get_repositories
    def test_get_repositories(context):
        """Test listing repositories"""
        repos = context["client"].getRepositories()
        assert repos is not None
        assert len(repos) > 0
        assert isinstance(repos, list)

    suite.add_test("get_repositories", "List repositories", test_get_repositories)

    # Test 3: get_root_folder
    def test_get_root_folder(context):
        """Test accessing root folder"""
        root = context["repository"].getRootFolder()
        assert root is not None
        props = root.getProperties()
        assert props.get("cmis:baseTypeId") == "cmis:folder"
        context["suite_data"]["root"] = root

    suite.add_test(
        "get_root_folder", "Get root folder", test_get_root_folder, depends_on="connect"
    )

    # Test 4: create_test_folder
    def test_create_test_folder(context):
        """Test creating test folder"""
        root = context["suite_data"]["root"]
        folder_name = f"cmis_tck_test_{int(time.time() * 1000)}"
        folder = root.createFolder(folder_name, {"cmis:objectTypeId": "cmis:folder"})
        assert folder is not None
        assert folder.getName() == folder_name
        context["suite_data"]["test_folder"] = folder

    suite.add_test(
        "create_folder",
        "Create test folder",
        test_create_test_folder,
        depends_on="get_root_folder",
    )

    # Test 5: list_children
    def test_list_children(context):
        """Test listing folder children"""
        root = context["suite_data"]["root"]
        children = root.getChildren()
        assert children is not None
        # Root folder should now have at least our test folder
        found = False
        test_folder_id = context["suite_data"]["test_folder"].getObjectId()
        for child in children:
            if child.getObjectId() == test_folder_id:
                found = True
                break
        assert found, "Test folder not found in root children"

    suite.add_test(
        "list_children",
        "List folder children",
        test_list_children,
        depends_on="create_folder",
    )

    # Test 6: get_properties
    def test_get_properties(context):
        """Test getting object properties"""
        folder = context["suite_data"]["test_folder"]
        props = folder.getProperties()
        assert props is not None
        assert "cmis:objectId" in props
        assert "cmis:name" in props
        assert "cmis:objectTypeId" in props

    suite.add_test(
        "get_properties",
        "Get object properties",
        test_get_properties,
        depends_on="create_folder",
    )

    # Test 7: create_document
    def test_create_document(context):
        """Test creating a document"""
        folder = context["suite_data"]["test_folder"]
        doc_name = "test_doc.txt"
        content = "Hello, CMIS!"

        from io import BytesIO

        content_stream = BytesIO(content.encode("utf-8"))
        doc = folder.createDocument(
            doc_name, {"cmis:objectTypeId": "cmis:document"}, contentFile=content_stream
        )

        assert doc is not None
        assert doc.getName() == doc_name
        context["suite_data"]["test_document"] = doc

    suite.add_test(
        "create_document",
        "Create document",
        test_create_document,
        depends_on="create_folder",
    )

    # Test 8: get_content
    def test_get_content(context):
        """Test retrieving document content"""
        doc = context["suite_data"]["test_document"]
        content_stream = doc.getContentStream()
        assert content_stream is not None
        content = content_stream.read()
        assert content == b"Hello, CMIS!"

    suite.add_test(
        "get_content",
        "Get document content",
        test_get_content,
        depends_on="create_document",
    )

    # Test 9: delete_document
    def test_delete_document(context):
        """Test deleting a document"""
        doc = context["suite_data"]["test_document"]
        doc_id = doc.getObjectId()
        doc.delete()

        # Verify it's gone
        from cmissh.exceptions import ObjectNotFoundException

        try:
            context["repository"].getObject(doc_id)
            msg = "Document should have been deleted"
            raise AssertionError(msg)
        except ObjectNotFoundException:
            pass  # Expected

    suite.add_test(
        "delete_document",
        "Delete document",
        test_delete_document,
        depends_on="get_content",
    )

    # Test 10: delete_folder
    def test_delete_folder(context):
        """Test deleting folder"""
        folder = context["suite_data"]["test_folder"]
        folder.delete()
        context["suite_data"]["test_folder"] = None

    suite.add_test(
        "delete_folder",
        "Delete folder",
        test_delete_folder,
        depends_on="delete_document",
    )

    # Test 11: finish
    def test_finish(context):
        """Finalize test suite"""
        elapsed = time.time() - context["start_time"]
        assert elapsed >= 0

    suite.add_test("finish", "Finalize test suite", test_finish)

    return suite
