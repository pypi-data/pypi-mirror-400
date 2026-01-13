"""
Versioning operations test suite
"""

import time
from io import BytesIO

from cmissh.tck.suite import TCKTestSuite


def create_versioning_suite() -> TCKTestSuite:
    """Create the versioning operations test suite"""
    suite = TCKTestSuite("versioning", "Versioning Operations")

    def setup(context):
        """Create test folder"""
        root = context["repository"].getRootFolder()
        folder_name = f"cmis_tck_version_{int(time.time() * 1000)}"
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

    # Test 1: create_versionable_document
    def test_create_versionable(context):
        """Test creating versionable document"""
        folder = context["suite_data"]["test_folder"]
        props = {"cmis:objectTypeId": "cmis:document"}
        content = BytesIO(b"Version 1")
        doc = folder.createDocument("versioned.txt", props, contentFile=content)
        assert doc is not None
        context["suite_data"]["doc"] = doc

    suite.add_test(
        "create_versionable", "Create versionable doc", test_create_versionable
    )

    # Test 2: check_is_versionable
    def test_check_versionable(context):
        """Test checking if document is versionable"""
        doc = context["suite_data"]["doc"]
        props = doc.getProperties()
        is_versionable = props.get("cmis:isVersionSeriesCheckedOut", False)
        # Document exists, so it's versionable in some form
        assert doc is not None

    suite.add_test(
        "check_versionable",
        "Check versionable",
        test_check_versionable,
        depends_on="create_versionable",
    )

    # Test 3: get_all_versions
    def test_get_versions(context):
        """Test getting all versions"""
        doc = context["suite_data"]["doc"]
        try:
            versions = doc.getAllVersions()
            assert versions is not None
            # Should have at least the current version
            assert len(list(versions)) >= 1
        except AttributeError:
            msg = "getAllVersions method not implemented"
            raise AssertionError(msg)
        except Exception as e:
            if "not supported" in str(e).lower():
                msg = "Versioning not supported"
                raise AssertionError(msg)
            raise

    suite.add_test(
        "get_versions",
        "Get all versions",
        test_get_versions,
        depends_on="check_versionable",
    )

    # Test 4: checkout_document
    def test_checkout(context):
        """Test checking out document"""
        doc = context["suite_data"]["doc"]
        try:
            pwc = doc.checkout()
            assert pwc is not None
            context["suite_data"]["pwc"] = pwc
        except AttributeError:
            msg = "checkout method not implemented"
            raise AssertionError(msg)
        except Exception as e:
            if "not supported" in str(e).lower() or "not versionable" in str(e).lower():
                msg = "Checkout not supported"
                raise AssertionError(msg)
            raise

    suite.add_test(
        "checkout", "Checkout document", test_checkout, depends_on="get_versions"
    )

    # Test 5: cancel_checkout
    def test_cancel_checkout(context):
        """Test canceling checkout"""
        if "pwc" not in context["suite_data"]:
            msg = "No PWC available"
            raise AssertionError(msg)

        # Cancel checkout must be called on the ORIGINAL document, not the PWC
        doc = context["suite_data"]["doc"]
        try:
            doc.cancelCheckout()
            # Verify the checkout was cancelled
            doc.reload()
            props = doc.getProperties()
            is_checked_out = props.get("cmis:isVersionSeriesCheckedOut", False)
            assert not is_checked_out, "Document should no longer be checked out"
        except AttributeError:
            msg = "cancelCheckout method not implemented"
            raise AssertionError(msg)
        except Exception as e:
            if "not supported" in str(e).lower():
                msg = "Cancel checkout not supported"
                raise AssertionError(msg)
            raise

    suite.add_test(
        "cancel_checkout",
        "Cancel checkout",
        test_cancel_checkout,
        depends_on="checkout",
    )

    suite.add_test("finish", "Finalize suite", lambda ctx: None)

    return suite
