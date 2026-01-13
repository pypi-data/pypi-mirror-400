from __future__ import annotations

import asyncio
import json
from io import BytesIO
from pathlib import Path
from typing import Any, Optional

import click

from docudevs_client import (
    DocuDevsClient,
    TemplateFillRequest,
    UploadCommand,
    UploadDocumentBody,
    UploadFilesBody,
    OcrCommand,
)
from docudevs.models.cases_controller_create_case_request import CasesControllerCreateCaseRequest
from docudevs.models.cases_controller_update_case_request import CasesControllerUpdateCaseRequest
from docudevs.models.upload_case_document_body import UploadCaseDocumentBody


from docudevs.types import File, UNSET


def _as_serializable(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):


        return {k: _as_serializable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_as_serializable(item) for item in value]
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "__dict__"):
        return {k: _as_serializable(v) for k, v in vars(value).items()}
    return value




def _echo_response(result: Any) -> None:
    payload = result
    if hasattr(result, "parsed") and getattr(result, "parsed") is not None:
        payload = result.parsed
    elif hasattr(result, "body"):
        payload = result.body


    elif hasattr(result, "content") and isinstance(result.content, (bytes, bytearray)):
        try:
            payload = json.loads(result.content.decode("utf-8"))
        except Exception:
            payload = result.content.decode("utf-8", errors="replace")

    if isinstance(payload, (bytes, bytearray)):
        payload = payload.decode("utf-8", errors="replace")

    if isinstance(payload, str):
        click.echo(payload)
    else:


        click.echo(json.dumps(_as_serializable(payload), indent=2))


def _coerce_case_id(case_id: str) -> Any:
    try:
        return int(case_id)
    except (TypeError, ValueError):
        return case_id


def _parse_key_value_pairs(pairs: tuple[str, ...], param_hint: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise click.BadParameter("Expected key=value format", param_hint=param_hint)
        key, value = pair.split("=", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def _parse_metadata_option(value: str | None) -> dict[str, Any] | None:
    if value is None:
        return None
    candidate = value.strip()
    if not candidate:
        return None
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        pairs = tuple(item.strip() for item in candidate.split(",") if item.strip())
        return _parse_key_value_pairs(pairs, "--metadata") if pairs else None
    if not isinstance(parsed, dict):
        raise click.BadParameter("Metadata must be a JSON object or key=value pairs", param_hint="--metadata")
    return parsed


def _load_json_from_value(value: str, *, param_hint: str) -> Any:
    candidate = value.strip()
    if not candidate:
        raise click.BadParameter("Value cannot be empty", param_hint=param_hint)
    if candidate.startswith("@"):
        path = Path(candidate[1:])
        try:
            candidate = path.read_text()
        except OSError as exc:
            raise click.BadParameter(f"Unable to read file {path}: {exc}", param_hint=param_hint)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise click.BadParameter("Expected JSON content", param_hint=param_hint) from exc


def _parse_tool_options(values: tuple[str, ...]) -> list[dict[str, Any]]:
    descriptors: list[dict[str, Any]] = []
    for raw in values:
        parsed = _load_json_from_value(raw, param_hint="--tool")
        if not isinstance(parsed, dict):
            raise click.BadParameter("Tool entries must be JSON objects", param_hint="--tool")
        if "type" not in parsed:
            raise click.BadParameter("Tool entries must include a 'type' field", param_hint="--tool")
        descriptors.append(parsed)
    return descriptors


def async_command(f):
    """Decorator to run async click commands."""
    import functools

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


@click.group()
@click.option("--api-url", default="https://api.docudevs.ai", help="API URL")
@click.option("--token", help="Authentication token (or set DOCUDEVS_TOKEN env var)")
@click.pass_context
def cli(ctx, api_url: str, token: str):
    """DocuDevs CLI tool"""
    ctx.ensure_object(dict)
    
    # Get token from environment if not provided
    if not token:
        import os
        env_token = os.getenv('DOCUDEVS_TOKEN') or os.getenv('API_KEY')
        if env_token:
            token = env_token
    
    if not token:
        click.echo("Error: No authentication token provided. Use --token or set DOCUDEVS_TOKEN environment variable.", err=True)
        ctx.exit(1)
    
    ctx.obj["client"] = DocuDevsClient(api_url=api_url, token=token)


# High-level convenience commands
@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--prompt", default="", help="Extraction prompt")
@click.option("--prompt-file", type=click.Path(exists=True), help="Path to a text file containing extraction instructions")
@click.option("--schema", default="", help="JSON schema for extraction")
@click.option("--schema-file", type=click.Path(exists=True), help="Path to a JSON schema file")
@click.option("--mime-type", help="Explicit MIME type for the document")
@click.option("--configuration", help="Use a saved configuration for processing")
@click.option("--ocr", type=click.Choice(["DEFAULT", "NONE", "PREMIUM", "AUTO", "EXCEL"]), default="DEFAULT", help="OCR type")
@click.option("--llm", type=click.Choice(["DEFAULT", "MINI", "HIGH"]), default="DEFAULT", help="LLM type")
@click.option("--barcodes", is_flag=True, default=False, help="Enable barcode and QR code detection")
@click.option("--extraction-mode", type=click.Choice(["OCR", "SIMPLE", "STEPS"]), default=None, help="Extraction mode override")
@click.option("--describe-figures", is_flag=True, default=False, help="Request figure descriptions when supported")
@click.option("--timeout", default=60, help="Timeout in seconds")
@click.option("--wait/--no-wait", default=True, help="Wait for processing to complete")
@click.option(
    "--tool",
    "tools",
    multiple=True,
    help="Attach a tool descriptor as JSON or @path (must include 'type'); can be provided multiple times.",
)
@click.pass_context
@async_command
async def process(
    ctx,
    file: str,
    prompt: str,
    prompt_file: Optional[str],
    schema: str,
    schema_file: Optional[str],
    mime_type: Optional[str],
    configuration: Optional[str],
    ocr: str,
    llm: str,
    barcodes: bool,
    extraction_mode: Optional[str],
    describe_figures: bool,
    timeout: int,
    wait: bool,
    tools: tuple[str, ...],
):
    """Upload and process a document in one command."""
    import mimetypes

    file_path = Path(file)
    effective_mime = mime_type or mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"

    with open(file_path, "rb") as f:
        document_data = f.read()

    def make_document_stream() -> BytesIO:
        return BytesIO(document_data)

    prompt_text = prompt
    if prompt_file:
        if prompt:
            raise click.BadParameter("Use either --prompt or --prompt-file, not both.", param_hint="--prompt-file")
        prompt_text = Path(prompt_file).read_text()

    schema_text = schema
    if schema_file:
        if schema:
            raise click.BadParameter("Use either --schema or --schema-file, not both.", param_hint="--schema-file")
        schema_text = Path(schema_file).read_text()

    barcodes_value: Optional[bool] = True if barcodes else None
    describe_value: Optional[bool] = True if describe_figures else None

    tool_descriptors = _parse_tool_options(tools) if tools else []

    if configuration:
        if tool_descriptors:
            raise click.BadParameter("--tool cannot be combined with --configuration", param_hint="--tool")
        if prompt_text.strip():
            raise click.BadParameter("--prompt/--prompt-file cannot be used with --configuration", param_hint="--configuration")
        if schema_text.strip():
            raise click.BadParameter("--schema/--schema-file cannot be used with --configuration", param_hint="--configuration")
        if barcodes_value is not None or extraction_mode or describe_value:
            raise click.BadParameter("Processing flags cannot be combined with --configuration", param_hint="--configuration")
        if ocr != "DEFAULT" or llm != "DEFAULT":
            raise click.BadParameter("--ocr and --llm cannot be combined with --configuration", param_hint="--configuration")

    client: DocuDevsClient = ctx.obj["client"]

    try:
        if configuration:
            guid = await client.submit_and_process_document_with_configuration(
                document=make_document_stream(),
                document_mime_type=effective_mime,
                configuration_name=configuration,
            )
        else:
            guid = await client.submit_and_process_document(
                document=make_document_stream(),
                document_mime_type=effective_mime,
                prompt=prompt_text,
                schema=schema_text,
                ocr=ocr,
                llm=llm,
                barcodes=barcodes_value,
                extraction_mode=extraction_mode,
                describe_figures=describe_value,
                tools=tool_descriptors or None,
            )
        click.echo(f"Document uploaded and queued for processing. GUID: {guid}")

        if wait:
            click.echo("Waiting for processing to complete...")
            result = await client.wait_until_ready(guid, timeout=timeout)
            _echo_response(result)
        else:
            click.echo("Use 'status' and 'result' commands to check progress and get results.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


@cli.command("process-map-reduce")
@click.argument("file", type=click.Path(exists=True))
@click.option("--prompt", default="", help="Extraction prompt")
@click.option("--prompt-file", type=click.Path(exists=True), help="Path to a text file containing extraction instructions")
@click.option("--schema", default="", help="JSON schema for extraction")
@click.option("--schema-file", type=click.Path(exists=True), help="Path to a JSON schema file")
@click.option("--mime-type", help="Explicit MIME type for the document")
@click.option("--ocr", type=click.Choice(["DEFAULT", "NONE", "PREMIUM", "AUTO", "EXCEL"]), default="DEFAULT", help="OCR type")
@click.option("--llm", type=click.Choice(["DEFAULT", "MINI", "HIGH"]), default="DEFAULT", help="LLM type")
@click.option("--barcodes", is_flag=True, default=False, help="Enable barcode and QR code detection")
@click.option("--extraction-mode", type=click.Choice(["OCR", "SIMPLE", "STEPS"]), default=None, help="Extraction mode override")
@click.option("--describe-figures", is_flag=True, default=False, help="Request figure descriptions when supported")
@click.option("--pages-per-chunk", type=int, default=1, show_default=True, help="Pages per chunk for map-reduce")
@click.option("--overlap", type=int, default=0, show_default=True, help="Overlapping pages between chunks")
@click.option("--dedup-key", help="JSON path to deduplicate rows across chunks")
@click.option("--header-page-limit", type=int, help="Number of pages reserved for header extraction")
@click.option("--header-include-in-rows", is_flag=True, default=False, help="Include header pages in row processing")
@click.option("--header-row-prompt-augmentation", help="Additional context added to each chunk prompt")
@click.option("--header-schema", help="JSON schema for header extraction")
@click.option("--header-schema-file", type=click.Path(exists=True), help="Path to JSON schema file for header")
@click.option("--header-prompt", help="Prompt dedicated to header extraction")
@click.option("--header-page-index", "header_page_indices", multiple=True, type=int, help="Explicit page indices for header capture")
@click.option("--stop-when-empty", is_flag=True, default=False, help="Stop processing when empty chunks are detected")
@click.option("--empty-chunk-grace", type=int, help="Number of empty chunks allowed before stopping")
@click.option(
    "--tool",
    "tools",
    multiple=True,
    help="Attach a tool descriptor as JSON or @path (must include 'type'); can be provided multiple times.",
)
@click.option("--timeout", default=60, help="Timeout in seconds")
@click.option("--wait/--no-wait", default=True, help="Wait for processing to complete")
@click.pass_context
@async_command
async def process_map_reduce(
    ctx,
    file: str,
    prompt: str,
    prompt_file: Optional[str],
    schema: str,
    schema_file: Optional[str],
    mime_type: Optional[str],
    ocr: str,
    llm: str,
    barcodes: bool,
    extraction_mode: Optional[str],
    describe_figures: bool,
    pages_per_chunk: int,
    overlap: int,
    dedup_key: Optional[str],
    header_page_limit: Optional[int],
    header_include_in_rows: bool,
    header_row_prompt_augmentation: Optional[str],
    header_schema: Optional[str],
    header_schema_file: Optional[str],
    header_prompt: Optional[str],
    header_page_indices: tuple[int, ...],
    stop_when_empty: bool,
    empty_chunk_grace: Optional[int],
    tools: tuple[str, ...],
    timeout: int,
    wait: bool,
):
    """Upload and process a document using map-reduce chunking."""
    import mimetypes

    file_path = Path(file)
    effective_mime = mime_type or mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"

    with open(file_path, "rb") as f:
        document_data = f.read()

    def make_document_stream() -> BytesIO:
        return BytesIO(document_data)

    prompt_text = prompt
    if prompt_file:
        if prompt:
            raise click.BadParameter("Use either --prompt or --prompt-file, not both.", param_hint="--prompt-file")
        prompt_text = Path(prompt_file).read_text()

    schema_text = schema
    if schema_file:
        if schema:
            raise click.BadParameter("Use either --schema or --schema-file, not both.", param_hint="--schema-file")
        schema_text = Path(schema_file).read_text()

    header_schema_text = header_schema
    if header_schema_file:
        if header_schema:
            raise click.BadParameter("Use either --header-schema or --header-schema-file, not both.", param_hint="--header-schema-file")
        header_schema_text = Path(header_schema_file).read_text()

    barcodes_value: Optional[bool] = True if barcodes else None
    describe_value: Optional[bool] = True if describe_figures else None

    tool_descriptors = _parse_tool_options(tools) if tools else []

    header_options = {}
    if header_page_limit is not None:
        header_options["page_limit"] = header_page_limit
    if header_include_in_rows:
        header_options["include_in_rows"] = True
    if header_row_prompt_augmentation:
        header_options["row_prompt_augmentation"] = header_row_prompt_augmentation
    if header_page_indices:
        header_options["page_indices"] = list(header_page_indices)

    client: DocuDevsClient = ctx.obj["client"]
    try:
        guid = await client.submit_and_process_document_map_reduce(
            document=make_document_stream(),
            document_mime_type=effective_mime,
            prompt=prompt_text,
            schema=schema_text,
            ocr=ocr,
            barcodes=barcodes_value,
            llm=llm,
            extraction_mode=extraction_mode,
            describe_figures=describe_value,
            pages_per_chunk=pages_per_chunk,
            overlap_pages=overlap,
            dedup_key=dedup_key,
            header_options=header_options or None,
            header_schema=header_schema_text,
            header_prompt=header_prompt,
            stop_when_empty=stop_when_empty,
            empty_chunk_grace=empty_chunk_grace,
            tools=tool_descriptors or None,
        )
        click.echo(f"Document uploaded and queued for map-reduce processing. GUID: {guid}")

        if wait:
            click.echo("Waiting for processing to complete...")
            result = await client.wait_until_ready(guid, timeout=timeout)
            _echo_response(result)
        else:
            click.echo("Use 'status' and 'result' commands to check progress and get results.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--ocr", type=click.Choice(["DEFAULT", "NONE", "PREMIUM", "AUTO", "EXCEL"]), default="DEFAULT", help="OCR type")
@click.option("--format", "ocr_format", type=click.Choice(["plain", "markdown", "jsonl"]), default=None, help="OCR output format")
@click.option("--timeout", default=60, help="Timeout in seconds")
@click.option("--wait/--no-wait", default=True, help="Wait for processing to complete")
@click.pass_context
@async_command
async def ocr_only(ctx, file: str, ocr: str, ocr_format: str, timeout: int, wait: bool):
    """Upload and process document with OCR-only mode."""
    from io import BytesIO
    import mimetypes
    
    file_path = Path(file)
    mime_type = mimetypes.guess_type(file)[0] or "application/octet-stream"
    
    with open(file_path, "rb") as f:
        document_bytes = BytesIO(f.read())
    
    effective_format = ocr_format
    if effective_format is None:
        effective_format = "jsonl" if ocr.upper() == "EXCEL" else "plain"

    try:
        guid = await ctx.obj["client"].submit_and_ocr_document(
            document=document_bytes,
            document_mime_type=mime_type,
            ocr=ocr,
            ocr_format=effective_format
        )
        click.echo(f"Document uploaded and queued for OCR processing. GUID: {guid}")
        
        if wait:
            click.echo("Waiting for processing to complete...")
            result = await ctx.obj["client"].wait_until_ready(guid, timeout=timeout)
            _echo_response(result)
        else:
            click.echo("Use 'status' and 'result' commands to check progress and get results.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


@cli.command()
@click.argument("guid")
@click.option("--timeout", default=60, help="Timeout in seconds")
@click.pass_context
@async_command
async def wait(ctx, guid: str, timeout: int):
    """Wait for a job to complete and return the result."""
    try:
        result = await ctx.obj["client"].wait_until_ready(guid, timeout=timeout)
        _echo_response(result)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


# Low-level commands
@cli.command()
@click.argument("uuid")
@click.pass_context
@async_command
async def result(ctx, uuid: str):
    """Get job result."""
    result = await ctx.obj["client"].result(uuid)
    _echo_response(result)



@cli.group("knowledge-base")
@click.pass_context
def knowledge_base(ctx):  # noqa: D401
    """Manage knowledge bases."""


@knowledge_base.command("list")
@click.pass_context
@async_command
async def list_knowledge_bases(ctx):
    """List knowledge bases."""
    result = await ctx.obj["client"].list_knowledge_bases()
    _echo_response(result)


@knowledge_base.command("add")
@click.argument("case_id")
@click.pass_context
@async_command
async def add_knowledge_base(ctx, case_id: str):
    """Promote a case to a knowledge base."""
    result = await ctx.obj["client"].promote_knowledge_base(_coerce_case_id(case_id))
    _echo_response(result)


@knowledge_base.command("get")
@click.argument("case_id")
@click.pass_context
@async_command
async def get_knowledge_base(ctx, case_id: str):
    """Get a knowledge base by case id."""
    result = await ctx.obj["client"].get_knowledge_base(_coerce_case_id(case_id))
    _echo_response(result)


@knowledge_base.command("remove")
@click.argument("case_id")
@click.pass_context
@async_command
async def remove_knowledge_base(ctx, case_id: str):
    """Demote a case from knowledge base status."""
    response = await ctx.obj["client"].delete_knowledge_base(_coerce_case_id(case_id))
    status_code = getattr(response, "status_code", None)
    if status_code is not None:
        click.echo(f"Knowledge base remove status: {status_code}")
    else:
        _echo_response(response)

@cli.command()
@click.argument("guid")
@click.pass_context
@async_command
async def status(ctx, guid: str):
    """Get job status."""
    result = await ctx.obj["client"].status(guid)
    _echo_response(result)


# Configuration commands
@cli.command()
@click.pass_context
@async_command
async def list_configurations(ctx):
    """List all named configurations."""
    result = await ctx.obj["client"].list_configurations()
    _echo_response(result)


@cli.command()
@click.argument("name")
@click.pass_context
@async_command
async def get_configuration(ctx, name: str):
    """Get a named configuration."""
    result = await ctx.obj["client"].get_configuration(name)
    _echo_response(result)


@cli.command()
@click.argument("name")
@click.argument("command_file", type=click.Path(exists=True))
@click.pass_context
@async_command
async def save_configuration(ctx, name: str, command_file: str):
    """Save a named configuration from a JSON file."""
    with open(command_file) as f:
        command_data = json.load(f)
    body = UploadCommand.from_dict(command_data)
    result = await ctx.obj["client"].save_configuration(name, body)
    _echo_response(result)


@cli.command()
@click.argument("name")
@click.pass_context
@async_command
async def delete_configuration(ctx, name: str):
    """Delete a named configuration."""
    result = await ctx.obj["client"].delete_configuration(name)
    _echo_response(result)


# Template commands
@cli.command()
@click.pass_context
@async_command
async def list_templates(ctx):
    """List all templates."""
    result = await ctx.obj["client"].list_templates()
    _echo_response(result)


@cli.command("upload-template")
@click.argument("name")
@click.argument("file", type=click.Path(exists=True))
@click.option("--mime-type", help="Override detected MIME type")
@click.pass_context
@async_command
async def upload_template(ctx, name: str, file: str, mime_type: Optional[str]):
    """Upload a template document."""
    import mimetypes

    file_path = Path(file)
    guessed_mime = mime_type or mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    with open(file_path, "rb") as f:
        template_bytes = f.read()
    response = await ctx.obj["client"].upload_template(
        name=name,
        document=BytesIO(template_bytes),
        file_name=file_path.name,
        mime_type=guessed_mime,
    )
    if hasattr(response, "status_code"):
        click.echo(f"Template upload status: {response.status_code}")
    else:
        _echo_response(response)


@cli.command("template-metadata")
@click.argument("name")
@click.pass_context
@async_command
async def template_metadata(ctx, name: str):
    """Get template metadata."""
    result = await ctx.obj["client"].metadata(name)
    _echo_response(result)


@cli.command("delete-template")
@click.argument("name")
@click.pass_context
@async_command
async def delete_template(ctx, name: str):
    """Delete a template."""
    result = await ctx.obj["client"].delete_template(name)
    if hasattr(result, "status_code"):
        click.echo(f"Template delete status: {result.status_code}")
    else:
        _echo_response(result)


@cli.command()
@click.argument("name")
@click.argument("request_file", type=click.Path(exists=True))
@click.option("--output", type=click.Path(), help="Write the filled document to this file")
@click.pass_context
@async_command
async def fill(ctx, name: str, request_file: str, output: Optional[str]):
    """Fill a template with data from JSON file."""
    with open(request_file) as f:
        request_data = json.load(f)
    body = TemplateFillRequest.from_dict(request_data)
    response = await ctx.obj["client"].fill(name, body)

    binary_content: Optional[bytes] = None
    if hasattr(response, "content") and isinstance(response.content, (bytes, bytearray)):
        binary_content = bytes(response.content)
    elif hasattr(response, "body") and isinstance(response.body, (bytes, bytearray)):
        binary_content = bytes(response.body)

    if output and binary_content is not None:
        Path(output).write_bytes(binary_content)
        click.echo(f"Filled document saved to {output}")
    elif output:
        # Nothing to write; fall back to structured output
        _echo_response(response)
    elif binary_content is not None:
        click.echo("Binary document returned; re-run with --output to save the file.")
    else:
        _echo_response(response)


# ---------------- Cases Management ----------------
@cli.group()
@click.pass_context
def cases(ctx):
    """Manage document cases."""
    pass


@cases.command("list")
@click.pass_context
@async_command
async def list_cases(ctx):
    """List all cases."""
    result = await ctx.obj["client"].list_cases()
    _echo_response(result)


@cases.command("create")
@click.option("--name", required=True, help="Case name")
@click.option("--description", help="Optional case description")
@click.pass_context
@async_command
async def create_case(ctx, name: str, description: Optional[str]):
    """Create a new case."""
    body = CasesControllerCreateCaseRequest(name=name, description=description if description is not None else UNSET)
    result = await ctx.obj["client"].create_case(body)
    _echo_response(result)


@cases.command("get")
@click.argument("case_id")
@click.pass_context
@async_command
async def get_case(ctx, case_id: str):
    """Get details for a case."""
    result = await ctx.obj["client"].get_case(_coerce_case_id(case_id))
    _echo_response(result)


@cases.command("update")
@click.argument("case_id")
@click.option("--name", required=True, help="Updated case name")
@click.option("--description", help="Updated description")
@click.pass_context
@async_command
async def update_case(ctx, case_id: str, name: str, description: Optional[str]):
    """Update a case."""
    body = CasesControllerUpdateCaseRequest(name=name, description=description if description is not None else UNSET)
    result = await ctx.obj["client"].update_case(_coerce_case_id(case_id), body)
    _echo_response(result)


@cases.command("delete")
@click.argument("case_id")
@click.pass_context
@async_command
async def delete_case(ctx, case_id: str):
    """Delete a case."""
    response = await ctx.obj["client"].delete_case(_coerce_case_id(case_id))
    if hasattr(response, "status_code"):
        click.echo(f"Case delete status: {response.status_code}")
    else:
        _echo_response(response)


@cases.command("list-documents")
@click.argument("case_id")
@click.option("--page", default=0, show_default=True, help="Page number", type=int)
@click.option("--size", default=20, show_default=True, help="Page size", type=int)
@click.pass_context
@async_command
async def list_case_documents(ctx, case_id: str, page: int, size: int):
    """List documents within a case."""
    result = await ctx.obj["client"].list_case_documents(_coerce_case_id(case_id), page=page, size=size)
    _echo_response(result)


@cases.command("get-document")
@click.argument("case_id")
@click.argument("document_id")
@click.pass_context
@async_command
async def get_case_document(ctx, case_id: str, document_id: str):
    """Get details for a document stored in a case."""
    result = await ctx.obj["client"].get_case_document(_coerce_case_id(case_id), document_id)
    _echo_response(result)


@cases.command("delete-document")
@click.argument("case_id")
@click.argument("document_id")
@click.pass_context
@async_command
async def delete_case_document(ctx, case_id: str, document_id: str):
    """Delete a document from a case."""
    response = await ctx.obj["client"].delete_case_document(_coerce_case_id(case_id), document_id)
    status_code = getattr(response, "status_code", None)
    if status_code is not None:
        click.echo(f"Case document delete status: {status_code}")
    else:
        _echo_response(response)


@cases.command("upload-document")
@click.argument("case_id")
@click.argument("file", type=click.Path(exists=True))
@click.option("--filename", help="Custom filename for the uploaded document")
@click.option("--mime-type", help="Explicit MIME type for the document")
@click.option("--metadata", help="Document metadata (JSON object or comma-separated key=value pairs)")
@click.pass_context
@async_command
async def upload_case_document(
    ctx,
    case_id: str,
    file: str,
    filename: str | None,
    mime_type: str | None,
    metadata: str | None,
):
    """Upload a document to an existing case."""
    import mimetypes

    file_path = Path(file)
    resolved_name = filename or file_path.name
    resolved_mime = mime_type or mimetypes.guess_type(resolved_name)[0] or "application/octet-stream"

    document_bytes = file_path.read_bytes()
    document = File(payload=BytesIO(document_bytes), file_name=resolved_name, mime_type=resolved_mime)

    body = UploadCaseDocumentBody(document=document)
    metadata_dict = _parse_metadata_option(metadata)
    if metadata_dict:
        body.additional_properties.update(metadata_dict)

    result = await ctx.obj["client"].upload_case_document(_coerce_case_id(case_id), body)
    _echo_response(result)


# ---------------- Operations Management ----------------
@cli.group()
@click.pass_context
def operations(ctx):
    """Manage post-processing operations."""
    pass


@operations.command("submit")
@click.argument("job_guid")
@click.option("--type", "operation_type", required=True, help="Operation type to execute")
@click.option("--llm-type", type=click.Choice(["DEFAULT", "MINI", "HIGH"]), help="Optional LLM type override")
@click.option("--parameter", "parameters", multiple=True, help="Custom operation parameter in key=value form")
@click.option("--wait/--no-wait", default=False, help="Wait for the operation result")
@click.option("--timeout", default=120, show_default=True, help="Wait timeout in seconds")
@click.option("--poll-interval", default=2.0, show_default=True, help="Polling interval in seconds")
@click.pass_context
@async_command
async def operations_submit(
    ctx,
    job_guid: str,
    operation_type: str,
    llm_type: Optional[str],
    parameters: tuple[str, ...],
    wait: bool,
    timeout: int,
    poll_interval: float,
):
    """Submit an operation for a completed job."""
    param_map = _parse_key_value_pairs(parameters, "--parameter") if parameters else {}
    client: DocuDevsClient = ctx.obj["client"]
    if wait:
        result = await client.submit_and_wait_for_operation_with_parameters(
            job_guid=job_guid,
            operation_type=operation_type,
            llm_type=llm_type,
            custom_parameters=param_map or None,
            timeout=timeout,
            poll_interval=poll_interval,
        )
        _echo_response(result)
    else:
        response = await client.submit_operation_with_parameters(
            job_guid=job_guid,
            operation_type=operation_type,
            llm_type=llm_type,
            custom_parameters=param_map or None,
        )
        _echo_response(response)


@operations.command("status")
@click.argument("job_guid")
@click.pass_context
@async_command
async def operations_status(ctx, job_guid: str):
    """Get status of operations for a job."""
    result = await ctx.obj["client"].get_operation_status(job_guid)
    _echo_response(result)


@operations.command("result")
@click.argument("job_guid")
@click.option("--type", "operation_type", required=True, help="Operation type to retrieve")
@click.pass_context
@async_command
async def operations_result(ctx, job_guid: str, operation_type: str):
    """Get the result of a specific operation."""
    result = await ctx.obj["client"].get_operation_result(job_guid, operation_type)
    _echo_response(result)


@operations.command("error-analysis")
@click.argument("job_guid")
@click.option("--llm-type", type=click.Choice(["DEFAULT", "MINI", "HIGH"]), help="Optional LLM fallback")
@click.option("--parameter", "parameters", multiple=True, help="Custom parameter in key=value form")
@click.option("--wait/--no-wait", default=True, help="Wait for completion")
@click.option("--timeout", default=120, show_default=True, help="Wait timeout in seconds")
@click.option("--poll-interval", default=2.0, show_default=True, help="Polling interval in seconds")
@click.pass_context
@async_command
async def operations_error_analysis(
    ctx,
    job_guid: str,
    llm_type: Optional[str],
    parameters: tuple[str, ...],
    wait: bool,
    timeout: int,
    poll_interval: float,
):
    """Run error analysis on a completed job."""
    param_map = _parse_key_value_pairs(parameters, "--parameter") if parameters else {}
    client: DocuDevsClient = ctx.obj["client"]
    if wait:
        result = await client.submit_and_wait_for_operation_with_parameters(
            job_guid=job_guid,
            operation_type="error-analysis",
            llm_type=llm_type,
            custom_parameters=param_map or None,
            timeout=timeout,
            poll_interval=poll_interval,
        )
        _echo_response(result)
    else:
        response = await client.submit_operation_with_parameters(
            job_guid=job_guid,
            operation_type="error-analysis",
            llm_type=llm_type,
            custom_parameters=param_map or None,
        )
        _echo_response(response)


@operations.command("generative-task")
@click.argument("parent_job_id")
@click.option("--prompt", required=True, help="Prompt for the generative task")
@click.option("--model", help="Optional LLM model override")
@click.option("--temperature", type=float, help="Sampling temperature")
@click.option("--max-tokens", type=int, help="Maximum tokens to generate")
@click.option("--wait/--no-wait", default=True, help="Wait for task completion")
@click.option("--timeout", default=120, show_default=True, help="Wait timeout in seconds")
@click.option("--poll-interval", default=2.0, show_default=True, help="Polling interval in seconds")
@click.pass_context
@async_command
async def operations_generative_task(
    ctx,
    parent_job_id: str,
    prompt: str,
    model: Optional[str],
    temperature: Optional[float],
    max_tokens: Optional[int],
    wait: bool,
    timeout: int,
    poll_interval: float,
):
    """Create a generative task for a completed job."""
    client: DocuDevsClient = ctx.obj["client"]
    if wait:
        result = await client.submit_and_wait_for_generative_task(
            parent_job_id=parent_job_id,
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            poll_interval=poll_interval,
        )
        _echo_response(result)
    else:
        response = await client.create_generative_task(
            parent_job_id=parent_job_id,
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        _echo_response(response)


# ---------------- LLM Provider Management ----------------
@cli.group()
@click.pass_context
def llm(ctx):
    """Manage LLM providers and key bindings."""
    pass


@llm.command("providers")
@click.pass_context
@async_command
async def list_llm_providers(ctx):
    """List LLM providers."""
    resp = await ctx.obj["client"].list_llm_providers()
    click.echo(resp.text)


@llm.command("create")
@click.option("--name", required=True)
@click.option("--type", "type_", required=True, help="Provider type (e.g. OPENAI, AZURE_OPENAI)")
@click.option("--base-url")
@click.option("--api-key")
@click.option("--model")
@click.option("--description")
@click.pass_context
@async_command
async def create_llm(ctx, name, type_, base_url, api_key, model, description):
    """Create an LLM provider."""
    resp = await ctx.obj["client"].create_llm_provider(name, type_, base_url, api_key, model, description)
    click.echo(resp.text)


@llm.command("get")
@click.argument("provider_id", type=int)
@click.pass_context
@async_command
async def get_llm(ctx, provider_id):
    """Get LLM provider by id."""
    resp = await ctx.obj["client"].get_llm_provider(provider_id)
    click.echo(resp.text)


@llm.command("update")
@click.argument("provider_id", type=int)
@click.option("--name")
@click.option("--base-url")
@click.option("--model")
@click.option("--description")
@click.pass_context
@async_command
async def update_llm(ctx, provider_id, name, base_url, model, description):
    """Update LLM provider (patch)."""
    resp = await ctx.obj["client"].update_llm_provider(provider_id, name=name, base_url=base_url, model=model, description=description)
    click.echo(resp.text)


@llm.command("delete")
@click.argument("provider_id", type=int)
@click.pass_context
@async_command
async def delete_llm(ctx, provider_id):
    """Delete (soft) an LLM provider."""
    resp = await ctx.obj["client"].delete_llm_provider(provider_id)
    click.echo(resp.status_code)


@llm.command("keys")
@click.pass_context
@async_command
async def list_llm_keys(ctx):
    """List LLM key bindings."""
    resp = await ctx.obj["client"].list_llm_keys()
    click.echo(resp.text)


@llm.command("bind")
@click.argument("key")
@click.option("--provider-id", type=int, required=False, help="Provider id to bind; omit to clear")
@click.pass_context
@async_command
async def bind_llm_key(ctx, key, provider_id):
    """Bind (or clear) a logical LLM key to a provider."""
    resp = await ctx.obj["client"].update_llm_key_binding(key, provider_id)
    click.echo(resp.status_code)


# ---------------- OCR Provider Management ----------------
@cli.group()
@click.pass_context
def ocr(ctx):
    """Manage OCR providers and key bindings."""
    pass


@ocr.command("providers")
@click.pass_context
@async_command
async def list_ocr_providers(ctx):
    """List OCR providers."""
    resp = await ctx.obj["client"].list_ocr_providers()
    click.echo(resp.text)


@ocr.command("create")
@click.option("--name", required=True)
@click.option("--endpoint")
@click.option("--api-key")
@click.option("--model")
@click.option("--description")
@click.pass_context
@async_command
async def create_ocr(ctx, name, endpoint, api_key, model, description):
    """Create an OCR provider."""
    resp = await ctx.obj["client"].create_ocr_provider(name, endpoint=endpoint, api_key=api_key, model=model, description=description)
    click.echo(resp.text)


@ocr.command("get")
@click.argument("provider_id", type=int)
@click.pass_context
@async_command
async def get_ocr(ctx, provider_id):
    """Get OCR provider by id."""
    resp = await ctx.obj["client"].get_ocr_provider(provider_id)
    click.echo(resp.text)


@ocr.command("update")
@click.argument("provider_id", type=int)
@click.option("--name")
@click.option("--endpoint")
@click.option("--model")
@click.option("--description")
@click.pass_context
@async_command
async def update_ocr(ctx, provider_id, name, endpoint, model, description):
    """Update OCR provider (patch)."""
    resp = await ctx.obj["client"].update_ocr_provider(provider_id, name=name, endpoint=endpoint, model=model, description=description)
    click.echo(resp.text)


@ocr.command("delete")
@click.argument("provider_id", type=int)
@click.pass_context
@async_command
async def delete_ocr(ctx, provider_id):
    """Delete (soft) an OCR provider."""
    resp = await ctx.obj["client"].delete_ocr_provider(provider_id)
    click.echo(resp.status_code)


@ocr.command("keys")
@click.pass_context
@async_command
async def list_ocr_keys(ctx):
    """List OCR key bindings."""
    resp = await ctx.obj["client"].list_ocr_keys()
    click.echo(resp.text)


@ocr.command("bind")
@click.argument("key")
@click.option("--provider-id", type=int, required=False, help="Provider id to bind; omit to clear")
@click.pass_context
@async_command
async def bind_ocr_key(ctx, key, provider_id):
    """Bind (or clear) an OCR key to a provider."""
    resp = await ctx.obj["client"].update_ocr_key_binding(key, provider_id)
    click.echo(resp.status_code)


if __name__ == "__main__":
    cli()
