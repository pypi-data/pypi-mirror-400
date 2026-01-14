"""
CLI commands for page operations.
"""

import json
from typing import Optional

import click

from konigle import models
from konigle.cli.main import cli, get_client
from konigle.filters.website import PageFilters


@cli.group()
def pages() -> None:
    """Page management commands."""
    pass


@pages.command()
@click.option("--title", "-t", required=True, help="Page title")
@click.option(
    "--name", "-n", help="Page name (defaults to title if not provided)"
)
@click.option(
    "--handle", "-h", help="URL handle (auto-generated if not provided)"
)
@click.option("--content", "-c", help="Page content as EditorJS JSON string")
@click.option(
    "--content-file",
    type=click.Path(exists=True, readable=True),
    help=(
        "Path to content file. If data-source is 'file', this should be a "
        ".txt or .md file. Otherwise, this should be an EditorJS JSON file."
    ),
)
@click.option(
    "--data-source",
    "-d",
    type=click.Choice(["self", "file", "data_table"], case_sensitive=False),
    default="self",
    help="Data source for the page content (default: self)",
)
@click.option(
    "--folder", "-f", required=True, help="Folder ID to place the page in"
)
@click.option("--author", "-a", help="Author ID")
@click.pass_context
def create(
    ctx: click.Context,
    title: str,
    name: Optional[str],
    handle: Optional[str],
    content: Optional[str],
    content_file: Optional[str],
    data_source: str,
    folder: str,
    author: Optional[str],
) -> None:
    """Create a new page."""
    name = name or title

    # Handle content based on data source
    content_data = None
    file_to_upload = None

    if data_source == "file":
        # When data source is file, upload the file directly
        if content_file:
            file_to_upload = content_file
        elif content:
            click.echo(
                "Error: When data-source is 'file', use --content-file "
                "instead of --content",
                err=True,
            )
            return
        else:
            click.echo(
                "Error: --content-file is required when data-source is "
                "'file'",
                err=True,
            )
            return
    else:
        # For 'self' or 'data_table', handle as EditorJS JSON
        if content_file:
            try:
                with open(content_file, "r", encoding="utf-8") as f:
                    content_content = f.read()
                content_data = json.loads(content_content)
            except Exception as e:
                click.echo(f"Error reading content file: {e}", err=True)
                return
        elif content:
            try:
                content_data = json.loads(content)
            except json.JSONDecodeError:
                click.echo("Error: Invalid JSON format for content", err=True)
                return
        else:
            content_data = {}

    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        page_data = models.PageCreate(
            title=title,
            name=name,
            handle=handle,
            content=content_data,
            folder=folder,
            author=author,
            data_source=data_source,
            content_file=file_to_upload,
        )

        result = client.pages.create(page_data)

        click.echo("✓ Page created successfully!")
        click.echo(result)

    except Exception as e:
        click.echo(f"✗ Error creating page: {e}", err=True)
        ctx.exit(1)


@pages.command("list")
@click.option("--page", "-p", default=1, help="Page number (default: 1)")
@click.option(
    "--page-size", "-s", default=10, help="Items per page (default: 10)"
)
@click.option("--folder", "-f", help="Filter by folder ID")
@click.option("--page-type", "-t", help="Filter by page type")
@click.option("--published", is_flag=True, help="Filter by published status")
@click.pass_context
def list_pages(
    ctx: click.Context,
    page: int,
    page_size: int,
    folder: Optional[str],
    page_type: Optional[str],
    published: Optional[bool],
) -> None:
    """List pages."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        filters = PageFilters(
            folder=folder,
            page_type=page_type,
            published=published,
        )

        result = client.pages.list(
            page=page, page_size=page_size, filters=filters
        )

        if not result.payload:
            click.echo("No pages found.")
            return

        click.echo(f"Pages (page {page}):")
        click.echo()

        for page_item in result.payload:
            click.echo(page_item)

    except Exception as e:
        click.echo(f"✗ Error listing pages: {e}", err=True)
        ctx.exit(1)


@pages.command()
@click.argument("page_id")
@click.pass_context
def get(ctx: click.Context, page_id: str) -> None:
    """Get a page by ID."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        page = client.pages.get(page_id)

        click.echo("✓ Fetched page successfully!")
        click.echo(page)

        click.echo("Details:")
        click.echo(page.model_dump_json(indent=2))

    except Exception as e:
        click.echo(f"✗ Error getting page: {e}", err=True)
        ctx.exit(1)


@pages.command()
@click.argument("page_id")
@click.option("--title", "-t", help="New page title")
@click.option("--name", "-n", help="New page name")
@click.option(
    "--content", "-c", help="New page content as EditorJS JSON string"
)
@click.option(
    "--content-file",
    type=click.Path(exists=True, readable=True),
    help=(
        "Path to content file. Can be a .txt/.md file (if page data-source "
        "is 'file') or an EditorJS JSON file (if page data-source is 'self')"
    ),
)
@click.option("--json-ld", "-j", help="JSON-LD structured data as JSON string")
@click.option("--seo", "-m", help="SEO meta as JSON string")
@click.pass_context
def update(
    ctx: click.Context,
    page_id: str,
    title: Optional[str],
    name: Optional[str],
    content: Optional[str],
    content_file: Optional[str],
    json_ld: Optional[str],
    seo: Optional[str],
) -> None:
    """Update a page.

    Note: The data source of a page cannot be changed after creation.
    """
    # Handle content from file or direct input
    # If content_file is provided, it will be uploaded directly
    # The backend will handle it based on the page's existing data_source
    content_data = None
    file_to_upload = None

    if content_file:
        # Check if it might be an EditorJS JSON file
        if content_file.endswith(".json"):
            # Try to parse as JSON for EditorJS content
            try:
                with open(content_file, "r", encoding="utf-8") as f:
                    content_content = f.read()
                content_data = json.loads(content_content)
            except json.JSONDecodeError:
                # Not valid JSON, treat as file upload
                file_to_upload = content_file
            except Exception as e:
                click.echo(f"Error reading content file: {e}", err=True)
                return
        else:
            # Non-JSON files are uploaded directly
            file_to_upload = content_file
    elif content:
        try:
            content_data = json.loads(content)
        except json.JSONDecodeError:
            click.echo("Error: Invalid JSON format for content", err=True)
            return

    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])

        update_data = {}
        if title:
            update_data["title"] = title
        if name:
            update_data["name"] = name
        if content_data is not None:
            update_data["content"] = content_data
        if file_to_upload:
            update_data["content_file"] = file_to_upload
        if json_ld:
            try:
                update_data["json_ld"] = json.loads(json_ld)
            except json.JSONDecodeError:
                click.echo("Error: Invalid JSON format for JSON-LD", err=True)
                return
        if seo:
            try:
                update_data["seo_meta"] = json.loads(seo)
            except json.JSONDecodeError:
                click.echo("Error: Invalid JSON format for SEO meta", err=True)
                return

        if not update_data:
            click.echo("No update fields provided.", err=True)
            ctx.exit(1)

        page_update = models.PageUpdate(**update_data)
        result = client.pages.update(page_id, page_update)

        click.echo("✓ Page updated successfully!")
        click.echo(result)

    except Exception as e:
        click.echo(f"✗ Error updating page: {e}", err=True)
        ctx.exit(1)


@pages.command()
@click.argument("page_id")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
@click.pass_context
def delete(
    ctx: click.Context,
    page_id: str,
    yes: bool,
) -> None:
    """Delete a page."""
    if not yes:
        if not click.confirm(
            f"Are you sure you want to delete page {page_id}?"
        ):
            click.echo("Cancelled.")
            return

    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        client.pages.delete(page_id)

        click.echo(f"✓ Page {page_id} deleted successfully!")

    except Exception as e:
        click.echo(f"✗ Error deleting page: {e}", err=True)
        ctx.exit(1)


@pages.command()
@click.argument("page_id")
@click.pass_context
def publish(ctx: click.Context, page_id: str) -> None:
    """Publish a page."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        result = client.pages.publish(page_id)

        click.echo(f"✓ Page {page_id} published successfully!")
        click.echo(result)

    except Exception as e:
        click.echo(f"✗ Error publishing page: {e}", err=True)
        ctx.exit(1)


@pages.command()
@click.argument("page_id")
@click.pass_context
def unpublish(ctx: click.Context, page_id: str) -> None:
    """Unpublish a page."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        result = client.pages.unpublish(page_id)

        click.echo(f"✓ Page {page_id} unpublished successfully!")
        click.echo(result)

    except Exception as e:
        click.echo(f"✗ Error unpublishing page: {e}", err=True)
        ctx.exit(1)


@pages.command("change-handle")
@click.argument("page_id")
@click.argument("new_handle")
@click.option(
    "--redirect", "-r", is_flag=True, help="Create redirect from old handle"
)
@click.pass_context
def change_handle(
    ctx: click.Context, page_id: str, new_handle: str, redirect: bool
) -> None:
    """Change the handle of a page."""
    try:
        client = get_client(ctx.obj["api_key"], ctx.obj["base_url"])
        result = client.pages.change_handle(page_id, new_handle, redirect)

        click.echo(f"✓ Page {page_id} handle changed to '{new_handle}'!")
        if redirect:
            click.echo("✓ Redirect created from old handle.")
        click.echo(result)

    except Exception as e:
        click.echo(f"✗ Error changing page handle: {e}", err=True)
        ctx.exit(1)
