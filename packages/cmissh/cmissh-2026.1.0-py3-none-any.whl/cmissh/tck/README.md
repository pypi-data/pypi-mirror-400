# CMIS Test Compatibility Kit (TCK)

A comprehensive compliance testing suite for CMIS servers, inspired by Litmus for WebDAV.

## Overview

The CMIS TCK provides a standardized way to test CMIS server implementations for compliance with the CMIS specification. It features:

- **Capability Detection**: Automatically detects and tests only supported features
- **Litmus-style Output**: Clear, concise test results similar to WebDAV Litmus
- **Modular Test Suites**: Organized by functionality (basic, repository, folders, documents, etc.)
- **Easy Integration**: Can be used in CI/CD pipelines for regression testing

## Installation

The TCK is included with cmissh:

```bash
pip install cmissh
```

## Usage

### Basic Usage

Test a CMIS server with default credentials:

```bash
cmis-tck http://localhost:8080/alfresco/api/-default-/public/cmis/versions/1.1/atom
```

### With Custom Credentials

```bash
cmis-tck -u myuser -p mypass http://cmis-server/cmis/atom
```

### Run Specific Test Suites

```bash
# Run only basic tests
cmis-tck --suites basic http://localhost:8080/alfresco/api/.../atom

# Run multiple suites
cmis-tck --suites basic,folders,documents http://localhost:8080/alfresco/api/.../atom
```

### Verbose Output

Show detected capabilities and detailed error messages:

```bash
cmis-tck -v http://localhost:8080/alfresco/api/.../atom
```

## Test Suites

### 1. Basic Operations (`basic`)
Tests fundamental CMIS operations:
- Connection and authentication
- Repository listing
- Folder creation and deletion
- Document creation and deletion
- Content retrieval

### 2. Repository Operations (`repository`)
Tests repository-level operations:
- Repository information retrieval
- Capabilities detection
- Type definitions
- Type descendants

### 3. Folder Operations (`folders`)
Tests folder-specific operations:
- Subfolder creation
- Parent navigation
- Children listing
- Nested folder structures
- Folder tree operations
- Folder deletion

### 4. Document Operations (`documents`)
Tests document-specific operations:
- Document creation (with and without content)
- Content stream retrieval
- Content updates
- Large document handling
- Document deletion

### 5. Property Operations (`properties`)
Tests property manipulation:
- Property retrieval
- Property updates
- Name changes
- Custom properties

### 6. Navigation Operations (`navigation`)
Tests navigation and search:
- Get object by ID
- Get object by path
- Parent navigation
- Descendants retrieval

### 7. Versioning Operations (`versioning`)
Tests version control:
- Version history
- Document checkout
- Checkout cancellation
- Version series

## Output Format

The TCK provides litmus-style output:

```
======================================================================
CMIS Test Compatibility Kit (TCK)
======================================================================
-> connecting to http://localhost:8080/alfresco/api/.../atom

-> running `basic':
  0. begin................ pass
  1. connect.............. pass
  2. get_repositories..... pass
  3. get_root_folder...... pass
  4. create_folder........ pass
  5. list_children........ pass
  6. get_properties....... pass
  7. create_document...... pass
  8. get_content.......... pass
  9. delete_document...... pass
 10. delete_folder........ pass
 11. finish............... pass
<- summary for `basic': of 12 tests run: 12 passed, 0 failed. 100.0%

======================================================================
CMIS TCK Results: 1 suites, 12 tests
  Passed:  12
  Failed:  0
  Skipped: 0
```

## Test Results

- **pass**: Test passed successfully
- **FAIL (message)**: Test failed with error message
- **SKIPPED**: Test skipped due to missing capability
- **WARNING**: Test passed but with warnings

## Capability Detection

The TCK automatically detects server capabilities and skips tests for unsupported features:

```bash
cmis-tck -v http://localhost:8080/alfresco/api/.../atom

-> detected capabilities:
   ACL: NO
   Query: YES
   GetDescendants: NO
   GetFolderTree: NO
   ...

-> running `folders':
  4. get_folder_tree...... SKIPPED   # Automatically skipped
```

## Exit Codes

- **0**: All tests passed
- **1**: One or more tests failed or connection error

## CI/CD Integration

### GitHub Actions

```yaml
name: CMIS Compliance
on: [push, pull_request]

jobs:
  tck:
    runs-on: ubuntu-latest
    services:
      alfresco:
        image: alfresco/alfresco-content-repository-community:latest
        ports:
          - 8080:8080

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install cmissh
      - run: |
          # Wait for Alfresco to start
          sleep 60
          # Run TCK
          cmis-tck http://localhost:8080/alfresco/api/-default-/public/cmis/versions/1.1/atom
```

### GitLab CI

```yaml
cmis_tck:
  image: python:3.11
  services:
    - name: alfresco/alfresco-content-repository-community:latest
      alias: alfresco
  before_script:
    - pip install cmissh
    - sleep 60  # Wait for Alfresco
  script:
    - cmis-tck http://alfresco:8080/alfresco/api/-default-/public/cmis/versions/1.1/atom
```

## Extending the TCK

You can add custom test suites by creating a new suite module:

```python
from cmissh.tck.suite import TCKTestSuite

def create_my_suite() -> TCKTestSuite:
    suite = TCKTestSuite("my_tests", "My Custom Tests")

    def test_something(context):
        # Your test logic
        assert context["repository"] is not None

    suite.add_test("my_test", "Test something", test_something)
    return suite
```

## Known Issues

Some CMIS servers have known limitations:

1. **Content Updates**: Some servers return 500 errors for content stream updates
2. **Versioning**: Checkout cancellation may fail on some servers
3. **Capabilities**: Not all servers properly report all capabilities

These are server-side issues, not TCK problems.

## Comparison with Other Tools

### vs. Apache Chemistry Workbench
- **Workbench**: Interactive GUI for manual testing
- **TCK**: Automated command-line testing for CI/CD

### vs. cmis-python Tests
- **cmis-python**: Library-specific unit tests
- **TCK**: Server compliance testing across implementations

### vs. CMIS Specification Tests
- **Spec Tests**: Reference tests from OASIS
- **TCK**: Practical compliance testing with real-world scenarios

## Contributing

To add new test suites:

1. Create a new file in `src/cmissh/tck/suites/`
2. Define your suite using `TCKTestSuite`
3. Add it to `src/cmissh/tck/suites/__init__.py`
4. Update the CLI in `src/cmissh/tck/cli.py`

## License

Apache License 2.0 (same as cmissh)

## See Also

- [CMIS Specification](http://docs.oasis-open.org/cmis/CMIS/v1.1/CMIS-v1.1.html)
- [Litmus (WebDAV TCK)](http://www.webdav.org/neon/litmus/)
- [Apache Chemistry](https://chemistry.apache.org/)
