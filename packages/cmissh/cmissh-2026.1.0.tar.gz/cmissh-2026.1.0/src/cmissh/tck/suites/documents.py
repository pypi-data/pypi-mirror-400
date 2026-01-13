"""
Document operations test suite
"""

import time
from io import BytesIO

from cmissh.tck.suite import TCKTestSuite


def create_document_suite() -> TCKTestSuite:
    """Create the document operations test suite"""
    suite = TCKTestSuite("documents", "Document Operations")

    def setup(context):
        """Create test folder"""
        root = context["repository"].getRootFolder()
        folder_name = f"cmis_tck_docs_{int(time.time() * 1000)}"
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

    # Test 1: create_document_no_content
    def test_create_no_content(context):
        """Test creating document without content"""
        folder = context["suite_data"]["test_folder"]
        doc = folder.createDocument("empty.txt", {"cmis:objectTypeId": "cmis:document"})
        assert doc is not None
        context["suite_data"]["empty_doc"] = doc

    suite.add_test(
        "create_no_content", "Create document (no content)", test_create_no_content
    )

    # Test 2: create_document_with_content
    def test_create_with_content(context):
        """Test creating document with content"""
        folder = context["suite_data"]["test_folder"]
        content = BytesIO(b"Hello, World!")
        doc = folder.createDocument(
            "hello.txt", {"cmis:objectTypeId": "cmis:document"}, contentFile=content
        )
        assert doc is not None
        context["suite_data"]["hello_doc"] = doc

    suite.add_test(
        "create_with_content",
        "Create document (with content)",
        test_create_with_content,
    )

    # Test 3: get_content_stream
    def test_get_content(context):
        """Test retrieving content stream"""
        doc = context["suite_data"]["hello_doc"]
        stream = doc.getContentStream()
        assert stream is not None
        content = stream.read()
        assert content == b"Hello, World!"

    suite.add_test(
        "get_content",
        "Get content stream",
        test_get_content,
        depends_on="create_with_content",
    )

    # Test 4: update_content
    def test_update_content(context):
        """Test updating document content"""
        doc = context["suite_data"]["hello_doc"]
        new_content = BytesIO(b"Updated content")

        # Check if document is versioned (most CMIS servers version by default)
        props = doc.getProperties()
        is_versioned = props.get("cmis:versionLabel") is not None

        try:
            if is_versioned:
                # For versioned documents, use checkout/update/checkin workflow
                pwc = doc.checkout()
                pwc.setContentStream(BytesIO(b"Updated content"))
                new_doc = pwc.checkin(checkinComment="Updated content via TCK")
                # Verify on the new version
                stream = new_doc.getContentStream()
                content = stream.read()
                assert content == b"Updated content"
                context["suite_data"]["hello_doc"] = new_doc
            else:
                # For non-versioned documents, direct update should work
                doc.setContentStream(new_content)
                doc.reload()
                stream = doc.getContentStream()
                content = stream.read()
                assert content == b"Updated content"
        except Exception as e:
            # Some servers may not support content updates
            if "not supported" in str(e).lower():
                msg = "Content updates not supported"
                raise AssertionError(msg)
            raise

    suite.add_test(
        "update_content",
        "Update content stream",
        test_update_content,
        depends_on="get_content",
    )

    # Test 5: delete_document
    def test_delete_doc(context):
        """Test deleting document"""
        doc = context["suite_data"]["empty_doc"]
        doc.delete()

    suite.add_test(
        "delete_document",
        "Delete document",
        test_delete_doc,
        depends_on="create_no_content",
    )

    # Test 6: create_large_document
    def test_create_large(context):
        """Test creating larger document"""
        folder = context["suite_data"]["test_folder"]
        # Create 1MB of content
        content = BytesIO(b"X" * (1024 * 1024))
        doc = folder.createDocument(
            "large.bin", {"cmis:objectTypeId": "cmis:document"}, contentFile=content
        )
        assert doc is not None
        context["suite_data"]["large_doc"] = doc

    suite.add_test("create_large", "Create large document", test_create_large)

    # Test 7: get_large_content
    def test_get_large(context):
        """Test retrieving large content"""
        doc = context["suite_data"]["large_doc"]
        stream = doc.getContentStream()
        content = stream.read()
        assert len(content) == 1024 * 1024

    suite.add_test(
        "get_large", "Get large content", test_get_large, depends_on="create_large"
    )

    suite.add_test("finish", "Finalize suite", lambda ctx: None)

    return suite
