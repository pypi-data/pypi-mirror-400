from codemie_tools.base.models import ToolMetadata
from codemie_tools.azure_devops.wiki.models import AzureDevOpsWikiConfig

GET_WIKI_TOOL = ToolMetadata(
    name="get_wiki",
    description="""
        Extract ADO wiki information. Takes a wiki identifier (name or ID) and returns detailed information about the wiki,
        including its ID, name, URL, remote URL, type, and associated project and repository IDs.

        Arguments:
        - wiki_identified (str): Wiki ID or wiki name to extract information about.
        Example: "MyWiki.wiki". Regularly, ".wiki" is essential.
        E.g. https://dev.azure.com/Organization/Project/_wiki/wikis/CodeMie.wiki/10/How-to-Create-Angular-Application
        "CodeMie.wiki" is the wiki identifier in this case.
        "How-to-Create-Angular-Application" is the page name.
        """,
    label="Get Wiki",
    user_description="""
        Retrieves information about a specific Azure DevOps wiki. The tool provides details about the wiki
        such as its ID, name, URL, and other metadata from the Azure DevOps project.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        """.strip(),
    config_class=AzureDevOpsWikiConfig
)

GET_WIKI_PAGE_BY_PATH_TOOL = ToolMetadata(
    name="get_wiki_page_by_path",
    description="""
        Extract ADO wiki page content by path with optional attachment download. Retrieves the full content of a wiki page using the page path.
        The content is returned as Markdown text. Optionally downloads and returns attachment file content.

        IMPORTANT: When extracting from Azure DevOps wiki URLs, ALWAYS use the '/{page_id}/{page-slug}' format.
        The tool will automatically resolve nested pages by discovering the full hierarchical path using the page ID.

        Arguments:
        - wiki_identified (str): Wiki ID or wiki name. Example: "MyWiki.wiki". Regularly, ".wiki" is essential.
        - page_name (str): Wiki page path in one of these formats:
          1. FROM URL (RECOMMENDED): Extract the '/{page_id}/{page-slug}' portion from the URL
             Example URL: https://dev.azure.com/Org/Proj/_wiki/wikis/MyWiki.wiki/10/How-to-Create-App
             Use page_name: "/10/How-to-Create-App" (the tool will resolve full nested path automatically)
          2. FULL PATH: For direct path like "/Home" or "/Parent/Child/Page"
        - include_attachments (bool, optional): Whether to download and return attachment content. Default: False.

        Return Format:
        - If include_attachments=False: Returns str (page markdown content only) - BACKWARD COMPATIBLE
        - If include_attachments=True: Returns dict with:
          - 'content': str (page markdown content)
          - 'attachments': dict mapping filename to bytes content
          - 'attachment_count': int (number of attachments downloaded)

        Attachment Download:
        - When include_attachments=True, the tool parses markdown for attachment links
        - Downloads all files referenced in markdown links containing '/_apis/wit/attachments/'
        - Returns file content as bytes for further processing
        - Failed downloads are logged but don't stop the operation

        Examples:
        - URL: https://dev.azure.com/Organization/Project/_wiki/wikis/CodeMie.wiki/10330/This-is-sub-page
          wiki_identified: "CodeMie.wiki"
          page_name: "/10330/This-is-sub-page" (ALWAYS use this format from URLs)
        - Get page with attachments:
          wiki_identified: "CodeMie.wiki"
          page_name: "/Documentation"
          include_attachments: True
          Result: {"content": "...", "attachments": {"file.pdf": b"...", "image.png": b"..."}, "attachment_count": 2}
        """,
    label="Get Wiki Page By Path",
    user_description="""
        Retrieves the content of a wiki page by its path with optional attachment download. The tool returns the Markdown content
        of the specified wiki page in the Azure DevOps project. For wiki URLs, extract the page ID and slug portion (e.g., '/123/Page-Name')
        and the tool will automatically resolve nested page paths.

        When include_attachments=True, also downloads and returns the content of all attached files.

        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        """.strip(),
    config_class=AzureDevOpsWikiConfig
)

GET_WIKI_PAGE_BY_ID_TOOL = ToolMetadata(
    name="get_wiki_page_by_id",
    description="""
        Extract ADO wiki page content by ID with optional attachment download. Retrieves the full content of a wiki page using the page ID.
        The content is returned as Markdown text. Optionally downloads and returns attachment file content.

        Arguments:
        - wiki_identified (str): Wiki ID or wiki name. Example: "MyWiki.wiki". Regularly, ".wiki" is essential.
        - page_id (int): Wiki page ID (numeric identifier)
        - include_attachments (bool, optional): Whether to download and return attachment content. Default: False.

        Return Format:
        - If include_attachments=False: Returns str (page markdown content only) - BACKWARD COMPATIBLE
        - If include_attachments=True: Returns dict with:
          - 'content': str (page markdown content)
          - 'attachments': dict mapping filename to bytes content
          - 'attachment_count': int (number of attachments downloaded)

        Attachment Download:
        - When include_attachments=True, the tool parses markdown for attachment links
        - Downloads all files referenced in markdown links containing '/_apis/wit/attachments/'
        - Returns file content as bytes for further processing
        - Failed downloads are logged but don't stop the operation

        Examples:
        - URL: https://dev.azure.com/Organization/Project/_wiki/wikis/CodeMie.wiki/10/How-to-Create-Angular-Application
          "CodeMie.wiki" is the wiki identifier
          "10" is the page id
        - Get page with attachments:
          wiki_identified: "CodeMie.wiki"
          page_id: 10
          include_attachments: True
          Result: {"content": "...", "attachments": {"file.pdf": b"...", "image.png": b"..."}, "attachment_count": 2}
        """,
    label="Get Wiki Page By ID",
    user_description="""
        Retrieves the content of a wiki page by its ID with optional attachment download. The tool returns the Markdown content
        of the specified wiki page in the Azure DevOps project.

        When include_attachments=True, also downloads and returns the content of all attached files.

        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        """.strip(),
    config_class=AzureDevOpsWikiConfig
)

DELETE_PAGE_BY_PATH_TOOL = ToolMetadata(
    name="delete_page_by_path",
    description="""
        Delete a wiki page by its path. Permanently removes the specified wiki page from the project's wiki.

        IMPORTANT: When extracting from Azure DevOps wiki URLs, ALWAYS use the '/{page_id}/{page-slug}' format.
        The tool will automatically resolve nested pages by discovering the full hierarchical path using the page ID.

        Arguments:
        - wiki_identified (str): Wiki ID or wiki name. Example: "MyWiki.wiki". Regularly, ".wiki" is essential.
        - page_name (str): Wiki page path in one of these formats:
          1. FROM URL (RECOMMENDED): Extract the '/{page_id}/{page-slug}' portion from the URL
             Example URL: https://dev.azure.com/Org/Proj/_wiki/wikis/MyWiki.wiki/10/How-to-Create-App
             Use page_name: "/10/How-to-Create-App" (the tool will resolve full nested path automatically)
          2. FULL PATH: For direct path like "/Home" or "/Parent/Child/Page"

        Examples:
        - URL: https://dev.azure.com/Organization/Project/_wiki/wikis/CodeMie.wiki/10330/This-is-sub-page
          wiki_identified: "CodeMie.wiki"
          page_name: "/10330/This-is-sub-page" (ALWAYS use this format from URLs)
        """,
    label="Delete Wiki Page By Path",
    user_description="""
        Deletes a wiki page identified by its path. The tool removes the specified wiki page from the
        Azure DevOps project wiki. For wiki URLs, extract the page ID and slug portion (e.g., '/123/Page-Name')
        and the tool will automatically resolve nested page paths.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        """.strip(),
    config_class=AzureDevOpsWikiConfig
)

DELETE_PAGE_BY_ID_TOOL = ToolMetadata(
    name="delete_page_by_id",
    description="""
        Delete a wiki page by its ID. Permanently removes the specified wiki page from the project's wiki.
        
        Arguments:
        - wiki_identified (str): Wiki ID or wiki name. Example: "MyWiki.wiki". Regularly, ".wiki" is essential.
        - page_id (int): Wiki page ID to delete (numeric identifier)
        """,
    label="Delete Wiki Page By ID",
    user_description="""
        Deletes a wiki page identified by its ID. The tool removes the specified wiki page from the
        Azure DevOps project wiki.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        """.strip(),
    config_class=AzureDevOpsWikiConfig
)

RENAME_WIKI_PAGE_TOOL = ToolMetadata(
    name="rename_wiki_page",
    description="""
        Rename an existing wiki page in Azure DevOps. This tool ONLY renames existing pages and will fail if the page doesn't exist.

        IMPORTANT: When extracting from Azure DevOps wiki URLs, ALWAYS use the '/{page_id}/{page-slug}' format.
        The tool will automatically resolve nested pages by discovering the full hierarchical path using the page ID.

        Arguments:
        - wiki_identified (str): Wiki ID or wiki name. Example: "MyWiki.wiki". Regularly, ".wiki" is essential.
        - old_page_name (str): Current page path to be renamed. Supports:
          1. FROM URL (RECOMMENDED): Extract the '/{page_id}/{page-slug}' portion from the URL
             Example URL: https://dev.azure.com/Org/Proj/_wiki/wikis/MyWiki.wiki/10/How-to-Create-App
             Use old_page_name: "/10/How-to-Create-App" (the tool will resolve full nested path automatically)
          2. FULL PATH: For direct path like "/OldName" or "/Parent/Child/OldName"
        - new_page_name (str): New page name or full path:
          1. JUST NAME: "NewName" - keeps page in the same parent directory (rename in place)
          2. FULL PATH: "/New/Location/Page" - moves page to a different location
        - version_identifier (str): Version string identifier (name of tag/branch, SHA1 of commit)
        - version_type (str, optional): Version type (branch, tag, or commit). Default is "branch"

        Examples:
        - Rename in place:
          URL: https://dev.azure.com/Organization/Project/_wiki/wikis/CodeMie.wiki/10330/This-is-sub-page
          old_page_name: "/10330/This-is-sub-page" (resolves to "/Parent/Child/Old Page")
          new_page_name: "Renamed Page" (becomes "/Parent/Child/Renamed Page")
        - Move to different location:
          old_page_name: "/10330/This-is-sub-page"
          new_page_name: "/New Parent/Renamed Page"
        """,
    label="Rename Wiki Page",
    user_description="""
        Renames an existing wiki page. The page must already exist. For wiki URLs, extract the page ID
        and slug portion (e.g., '/123/Page-Name') and the tool will automatically resolve nested page paths.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        4. Version identifier (e.g., branch name or commit SHA)
        """.strip(),
    config_class=AzureDevOpsWikiConfig
)

CREATE_WIKI_PAGE_TOOL = ToolMetadata(
    name="create_wiki_page",
    description="""
        Create a new ADO wiki page with optional file attachments. Creates a new page under the specified parent page path.
        If the wiki doesn't exist, it will be automatically created.

        FILE ATTACHMENTS: If files are provided via input_files, they will be uploaded and automatically linked at the end of the page.
        Supported file types: All file types (PDF, images, documents, etc.)

        IMPORTANT: When extracting parent page from Azure DevOps wiki URLs, ALWAYS use the '/{page_id}/{page-slug}' format.
        The tool will automatically resolve nested pages by discovering the full hierarchical path using the page ID.

        Arguments:
        - wiki_identified (str): Wiki ID or wiki name. Example: "MyWiki.wiki". Regularly, ".wiki" is essential.
        - parent_page_path (str): Parent page path where the new page will be created. Supports:
          1. FROM URL (RECOMMENDED): Extract the '/{page_id}/{page-slug}' portion from the URL
             Example URL: https://dev.azure.com/Org/Proj/_wiki/wikis/MyWiki.wiki/10/Parent-Page
             Use parent_page_path: "/10/Parent-Page" (the tool will resolve full nested path automatically)
          2. ROOT LEVEL: Use '/' for root level pages
          3. FULL PATH: For direct path like "/Parent Page" or "/Parent/Child"
        - new_page_name (str): Name of the new page to create (without path, just the name).
          Example: 'My New Page'
        - page_content (str): Markdown content for the new wiki page
        - version_identifier (str): Version string identifier (name of tag/branch, SHA1 of commit)
        - version_type (str, optional): Version type (branch, tag, or commit). Default is "branch".

        File Attachments:
        - Provide files via the config's input_files field
        - All attached files will be uploaded to Azure DevOps
        - Markdown links will be automatically appended to the page content under "## Attachments" section
        - Attachments are uploaded using the Azure DevOps Work Item Attachments API

        Examples:
        - Create under page from URL:
          URL: https://dev.azure.com/Org/Proj/_wiki/wikis/MyWiki.wiki/10395/Page-for-editing
          parent_page_path: "/10395/Page-for-editing" (ALWAYS use this format from URLs)
          new_page_name: "Created Page"
          Result: Resolves parent path and creates nested page
        - Create root level page:
          parent_page_path: "/"
          new_page_name: "My New Page"
          Result: Creates page at "/My New Page"
        - Create page with attachments:
          parent_page_path: "/"
          new_page_name: "Documentation"
          page_content: "# Documentation\\n\\nSee attached files."
          [Provide files via input_files]
          Result: Creates page with markdown links to uploaded files
        """,
    label="Create Wiki Page",
    user_description="""
        Creates a new wiki page under the specified parent page path with optional file attachments.
        If the wiki doesn't exist, it will be created. For wiki URLs, extract the page ID and slug
        portion (e.g., '/123/Page-Name') and the tool will automatically resolve nested page paths.

        Supports attaching files (PDF, images, documents, etc.) which will be uploaded and linked at
        the end of the page content.

        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        4. Version identifier (e.g., branch name or commit SHA)
        """.strip(),
    config_class=AzureDevOpsWikiConfig
)

MODIFY_WIKI_PAGE_TOOL = ToolMetadata(
    name="modify_wiki_page",
    description="""
        Update existing ADO wiki page content. This tool ONLY updates existing pages and will fail if the page doesn't exist.
        Use 'create_wiki_page' tool to create new pages.

        IMPORTANT: When extracting from Azure DevOps wiki URLs, ALWAYS use the '/{page_id}/{page-slug}' format.
        The tool will automatically resolve nested pages by discovering the full hierarchical path using the page ID.

        Arguments:
        - wiki_identified (str): Wiki ID or wiki name. Example: "MyWiki.wiki". Regularly, ".wiki" is essential.
        - page_name (str): Wiki page path in one of these formats:
          1. FROM URL (RECOMMENDED): Extract the '/{page_id}/{page-slug}' portion from the URL
             Example URL: https://dev.azure.com/Org/Proj/_wiki/wikis/MyWiki.wiki/10/How-to-Create-App
             Use page_name: "/10/How-to-Create-App" (the tool will resolve full nested path automatically)
          2. FULL PATH: For direct path like "/Home" or "/Parent/Child/Page"
        - page_content (str): Markdown content for the wiki page
        - version_identifier (str): Version string identifier (name of tag/branch, SHA1 of commit)
        - version_type (str, optional): Version type (branch, tag, or commit). Default is "branch".

        Examples:
        - URL: https://dev.azure.com/Organization/Project/_wiki/wikis/CodeMie.wiki/10330/This-is-sub-page
          wiki_identified: "CodeMie.wiki"
          page_name: "/10330/This-is-sub-page" (ALWAYS use this format from URLs)
        """,
    label="Modify Wiki Page",
    user_description="""
        Updates an existing wiki page with the specified content. The page must already exist.
        For wiki URLs, extract the page ID and slug portion (e.g., '/123/Page-Name')
        and the tool will automatically resolve nested page paths.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        4. Version identifier (e.g., branch name or commit SHA)
        """.strip(),
    config_class=AzureDevOpsWikiConfig
)

SEARCH_WIKI_PAGES_TOOL = ToolMetadata(
    name="search_wiki_pages",
    description="""
        Search for specific text content across all wiki pages. Performs full-text search and returns matching pages
        with content snippets showing where the text was found.

        Arguments:
        - wiki_identified (str): Wiki ID or wiki name. Example: "MyWiki.wiki". Regularly, ".wiki" is essential.
        - search_text (str): Text to search for (case-insensitive). Can be a word, phrase, or partial text.
        - include_context (bool, optional): Whether to include content snippets. Default is True.
        - max_results (int, optional): Maximum number of results to return (max 100). Default is 50.

        Returns:
        - List of matching pages with:
          - Full page URL
          - Page path
          - Page metadata (project, wiki, collection)
          - Content snippets (if include_context=True) showing where text was found

        Example:
        - Search all pages:
          wiki_identified: "CodeMie.wiki"
          search_text: "kubernetes deployment"
          Result: Finds all pages containing "kubernetes deployment" with clickable URLs
        """,
    label="Search Wiki Pages",
    user_description="""
        Searches for specific text content across all wiki pages. Results include page information with
        clickable URLs and content snippets showing where the search text was found.
        Before using it, you need to provide:
        1. Azure DevOps organization URL
        2. Project name
        3. Personal Access Token with appropriate permissions
        """.strip(),
    settings_config=True,
    config_class=AzureDevOpsWikiConfig
)
