File Management
===============

The File Management module provides functionality to upload, retrieve, and manage files within your organization and projects. Files can be used by assistants, stored for reference, or organized into folders.

This section covers:

* Uploading files to organization/project storage
* Retrieving file metadata and content
* Listing files in a project
* Deleting files
* Organizing files into folders

For each operation, you have three implementation options:

* `Command Line`_
* `Low-Level Service Layer`_
* `High-Level Service Layer`_

Overview
--------

File operations are scoped to:

* **Organization**: Top-level container for all resources
* **Project**: Specific project within an organization
* **Folder**: Optional logical grouping within a project

The SDK automatically resolves organization and project IDs from your API token when using the high-level manager.

Upload File
-----------

Uploads a file to project storage.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai files upload \
      --file-path "/path/to/document.pdf" \
      --folder "documents" \
      --file-name "user-manual.pdf"

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.core.files.clients import FileClient

    client = FileClient()
    
    result = client.upload_file(
        file_path="/path/to/document.pdf",
        organization_id="org-uuid",
        project_id="project-uuid",
        folder="documents",
        file_name="user-manual.pdf"
    )
    
    print(f"File uploaded: {result['fileId']}")
    print(f"File URL: {result['url']}")

**Parameters:**

* ``file_path``: (Required) Local path to the file to upload
* ``organization_id``: (Required) Organization UUID
* ``project_id``: (Required) Project UUID
* ``folder``: Optional folder name (defaults to temporary storage if omitted)
* ``file_name``: Optional custom name (defaults to original filename)

**Returns:**
Dictionary containing file ID and URL.

High-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.core.files.managers import FileManager
    from pygeai.core.files.models import UploadFile

    manager = FileManager()
    
    file_to_upload = UploadFile(
        path="/path/to/document.pdf",
        name="user-manual.pdf",
        folder="documents"
    )
    
    response = manager.upload_file(file=file_to_upload)
    
    print(f"File ID: {response.file_id}")
    print(f"File URL: {response.url}")

**Components:**

* ``FileManager``: Automatically resolves organization and project IDs from API token
* ``UploadFile``: Model defining file upload parameters
* ``UploadFileResponse``: Response with file ID and URL

**Returns:**
``UploadFileResponse`` object containing upload details.


List Files
----------

Retrieves all files in a project.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai files list

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.core.files.clients import FileClient

    client = FileClient()
    
    files = client.get_file_list(
        organization="org-uuid",
        project="project-uuid"
    )
    
    for file in files.get('files', []):
        print(f"{file['name']} - {file['folder']}")

**Parameters:**

* ``organization``: (Required) Organization UUID
* ``project``: (Required) Project UUID

**Returns:**
Dictionary containing list of files with metadata.

High-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.core.files.managers import FileManager

    manager = FileManager()
    file_list = manager.get_file_list()
    
    for file in file_list.files:
        print(f"Name: {file.name}")
        print(f"ID: {file.id}")
        print(f"Folder: {file.folder}")
        print(f"Size: {file.size} bytes")
        print("---")

**Returns:**
``FileList`` object containing list of ``File`` objects.


Get File Metadata
-----------------

Retrieves metadata for a specific file.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai files get --id "file-uuid"

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.core.files.clients import FileClient

    client = FileClient()
    
    file_data = client.get_file(
        organization="org-uuid",
        project="project-uuid",
        file_id="file-uuid"
    )
    
    print(f"Name: {file_data['name']}")
    print(f"Size: {file_data['size']}")
    print(f"Folder: {file_data['folder']}")
    print(f"Created: {file_data['createdAt']}")

**Parameters:**

* ``organization``: (Required) Organization UUID
* ``project``: (Required) Project UUID
* ``file_id``: (Required) File UUID

**Returns:**
Dictionary with file metadata (name, size, folder, timestamps, etc.).

High-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.core.files.managers import FileManager

    manager = FileManager()
    file_data = manager.get_file_data(file_id="file-uuid")
    
    print(f"File: {file_data.name}")
    print(f"Size: {file_data.size} bytes")
    print(f"Location: {file_data.folder}")

**Returns:**
``File`` object with file metadata.


Get File Content
----------------

Downloads the raw binary content of a file.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai files download \
      --id "file-uuid" \
      --output "/path/to/save/file.pdf"

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.core.files.clients import FileClient

    client = FileClient()
    
    content = client.get_file_content(
        organization="org-uuid",
        project="project-uuid",
        file_id="file-uuid"
    )
    
    # Save to file
    with open("/path/to/save/file.pdf", "wb") as f:
        f.write(content)

**Parameters:**

* ``organization``: (Required) Organization UUID
* ``project``: (Required) Project UUID
* ``file_id``: (Required) File UUID

**Returns:**
File content as bytes.

High-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.core.files.managers import FileManager

    manager = FileManager()
    content = manager.get_file_content(file_id="file-uuid")
    
    # Save to file
    with open("/path/to/save/file.pdf", "wb") as f:
        f.write(content)
    
    print(f"Downloaded {len(content)} bytes")

**Returns:**
File content as bytes.


Delete File
-----------

Removes a file from storage.

Command Line
^^^^^^^^^^^^

.. code-block:: shell

    geai files delete --id "file-uuid"

Low-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.core.files.clients import FileClient

    client = FileClient()
    
    result = client.delete_file(
        organization="org-uuid",
        project="project-uuid",
        file_id="file-uuid"
    )
    
    print("File deleted successfully")

**Parameters:**

* ``organization``: (Required) Organization UUID
* ``project``: (Required) Project UUID
* ``file_id``: (Required) File UUID

**Returns:**
Dictionary confirming deletion.

High-Level Service Layer
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from pygeai.core.files.managers import FileManager

    manager = FileManager()
    response = manager.delete_file(file_id="file-uuid")
    
    print(f"Status: {response.message}")

**Returns:**
``EmptyResponse`` confirming successful deletion.


Complete Workflow Example
--------------------------

.. code-block:: python

    from pygeai.core.files.managers import FileManager
    from pygeai.core.files.models import UploadFile
    from pathlib import Path

    manager = FileManager()

    # Upload a document
    document = UploadFile(
        path="/path/to/report.pdf",
        name="quarterly-report-Q1-2026.pdf",
        folder="reports/2026/Q1"
    )
    
    upload_response = manager.upload_file(file=document)
    file_id = upload_response.file_id
    print(f"Uploaded: {file_id}")

    # List all files in the project
    file_list = manager.get_file_list()
    print(f"\nTotal files: {len(file_list.files)}")
    
    for file in file_list.files:
        print(f"  - {file.name} ({file.folder})")

    # Get file metadata
    file_data = manager.get_file_data(file_id=file_id)
    print(f"\nFile details:")
    print(f"  Name: {file_data.name}")
    print(f"  Size: {file_data.size:,} bytes")
    print(f"  Folder: {file_data.folder}")

    # Download file content
    content = manager.get_file_content(file_id=file_id)
    
    # Save to local disk
    output_path = Path(f"/tmp/{file_data.name}")
    output_path.write_bytes(content)
    print(f"\nDownloaded to: {output_path}")

    # Clean up - delete file
    manager.delete_file(file_id=file_id)
    print("\nFile deleted from storage")


Folder Organization
-------------------

Organizing Files
~~~~~~~~~~~~~~~~

Use folders to organize files logically:

.. code-block:: python

    from pygeai.core.files.managers import FileManager
    from pygeai.core.files.models import UploadFile

    manager = FileManager()

    # Upload to different folders
    folders = {
        "contracts": "/path/to/contract.pdf",
        "invoices/2026": "/path/to/invoice.pdf",
        "documents/legal": "/path/to/terms.pdf"
    }

    for folder, filepath in folders.items():
        file = UploadFile(
            path=filepath,
            folder=folder
        )
        manager.upload_file(file=file)

**Folder Naming:**

* Use forward slashes for hierarchy: ``"reports/2026/Q1"``
* Use descriptive names: ``"customer-documents"`` not ``"docs1"``
* Be consistent with naming conventions

Listing by Folder
~~~~~~~~~~~~~~~~~

.. code-block:: python

    manager = FileManager()
    all_files = manager.get_file_list()

    # Group by folder
    from collections import defaultdict
    by_folder = defaultdict(list)
    
    for file in all_files.files:
        by_folder[file.folder].append(file)
    
    for folder, files in sorted(by_folder.items()):
        print(f"\n{folder or '(root)'}:")
        for file in files:
            print(f"  - {file.name}")


Best Practices
--------------

File Naming
~~~~~~~~~~~

* Use descriptive names
* Include version or date when relevant
* Avoid special characters (use hyphens/underscores)
* Use consistent extensions

File Organization
~~~~~~~~~~~~~~~~~

* Use folders to group related files
* Create hierarchical folder structures
* Document folder naming conventions
* Clean up temporary files regularly

Storage Management
~~~~~~~~~~~~~~~~~~

* Monitor storage usage
* Delete obsolete files
* Use appropriate file formats (compressed when possible)
* Consider file size limits

Security
~~~~~~~~

* Only upload files you have rights to use
* Don't upload sensitive data without encryption
* Use project scoping to isolate files
* Audit file access regularly


Error Handling
--------------

.. code-block:: python

    from pygeai.core.files.managers import FileManager
    from pygeai.core.files.models import UploadFile
    from pygeai.core.common.exceptions import APIError

    manager = FileManager()

    # Handle file not found
    try:
        file = UploadFile(path="/nonexistent/file.pdf")
        manager.upload_file(file=file)
    except FileNotFoundError as e:
        print(f"File not found: {e}")

    # Handle upload errors
    try:
        file = UploadFile(path="/path/to/file.pdf")
        response = manager.upload_file(file=file)
    except APIError as e:
        print(f"Upload failed: {e}")

    # Handle retrieval errors
    try:
        content = manager.get_file_content(file_id="invalid-id")
    except APIError as e:
        print(f"Could not retrieve file: {e}")


Common Issues
~~~~~~~~~~~~~

**File Not Found**

.. code-block:: python

    # ❌ Wrong
    file = UploadFile(path="relative/path.pdf")
    
    # ✅ Correct - use absolute paths
    file = UploadFile(path="/absolute/path/to/file.pdf")

**Missing Organization/Project ID**

.. code-block:: python

    # ❌ Wrong - using low-level client without IDs
    client = FileClient()
    client.upload_file(file_path="file.pdf")  # Missing org/project IDs
    
    # ✅ Correct - use high-level manager (auto-resolves)
    manager = FileManager()
    file = UploadFile(path="file.pdf")
    manager.upload_file(file=file)
    
    # ✅ Or provide IDs explicitly with client
    client.upload_file(
        file_path="file.pdf",
        organization_id="org-uuid",
        project_id="project-uuid"
    )

**Large File Uploads**

For large files, consider:

* Checking file size before upload
* Implementing progress tracking
* Handling timeout errors
* Using appropriate network settings


Integration Examples
--------------------

Upload File for Assistant
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from pygeai.core.files.managers import FileManager
    from pygeai.core.files.models import UploadFile

    # Upload a knowledge base document
    manager = FileManager()
    
    kb_file = UploadFile(
        path="/path/to/knowledge-base.pdf",
        name="product-documentation-v2.pdf",
        folder="assistant-kb"
    )
    
    response = manager.upload_file(file=kb_file)
    file_url = response.url
    
    # Use file_url with RAG assistant configuration
    print(f"Use this URL in assistant: {file_url}")


Notes
-----

* Files without a folder are stored in temporary storage
* File IDs are UUIDs generated by the system
* The high-level ``FileManager`` automatically resolves organization and project IDs from your API token
* File content is returned as binary data (bytes)
* Deleted files cannot be recovered
* Maximum file size depends on your organization's configuration
