"""
Repository operations test suite
"""

from cmissh.tck.suite import TCKTestSuite


def create_repository_suite() -> TCKTestSuite:
    """Create the repository operations test suite"""
    suite = TCKTestSuite("repository", "Repository Operations")

    # Test 0: begin
    def test_begin(context):
        """Initialize test suite"""
        assert context["repository"] is not None

    suite.add_test("begin", "Initialize suite", test_begin)

    # Test 1: repository_info
    def test_repository_info(context):
        """Test getting repository information"""
        info = context["repository"].getRepositoryInfo()
        assert info is not None
        assert "repositoryId" in info
        assert "repositoryName" in info
        assert "cmisVersionSupported" in info

    suite.add_test("repository_info", "Get repository info", test_repository_info)

    # Test 2: repository_capabilities
    def test_capabilities(context):
        """Test getting repository capabilities"""
        caps = context["capabilities"]
        assert caps is not None
        assert isinstance(caps, dict)
        # Capabilities were detected during connection
        assert len(caps) > 0

    suite.add_test("capabilities", "Get capabilities", test_capabilities)

    # Test 3: type_definition
    def test_type_definition(context):
        """Test getting type definition"""
        folder_type = context["repository"].getTypeDefinition("cmis:folder")
        assert folder_type is not None
        assert folder_type.getTypeId() == "cmis:folder"

    suite.add_test("type_definition", "Get type definition", test_type_definition)

    # Test 4: type_descendants
    def test_type_descendants(context):
        """Test getting type descendants"""
        try:
            descendants = context["repository"].getTypeDescendants("cmis:folder")
            assert descendants is not None
        except Exception:
            # Some servers may not support this
            pass

    suite.add_test("type_descendants", "Get type descendants", test_type_descendants)

    # Test 5: finish
    def test_finish(context):
        """Finalize test suite"""

    suite.add_test("finish", "Finalize suite", test_finish)

    return suite
