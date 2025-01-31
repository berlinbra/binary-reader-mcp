from typing import Any
import asyncio
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import os
from src.binary_reader.unreal_reader import UnrealAssetReader
from src.binary_reader.base_reader import BinaryReader

server = Server("binary_reader")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools for binary file analysis.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="read-unreal-asset",
            description="Read and analyze Unreal Engine .uasset file structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the .uasset file",
                    },
                },
                "required": ["file_path"],
            },
        ),
        types.Tool(
            name="read-binary-metadata",
            description="Read generic binary file metadata and structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the binary file",
                    },
                    "format": {
                        "type": "string",
                        "description": "File format specification (if known)",
                        "enum": ["auto", "unreal", "custom"],
                        "default": "auto"
                    }
                },
                "required": ["file_path"],
            },
        )
    ]

def format_unreal_asset_data(data: dict) -> str:
    """Format Unreal asset data into a readable string."""
    try:
        return (
            f"Unreal Asset Analysis:\n\n"
            f"Header Information:\n"
            f"Magic: {data.get('header', {}).get('magic', 'N/A')}\n"
            f"Legacy Version: {data.get('header', {}).get('legacy_version', 'N/A')}\n"
            f"UE4 Version: {data.get('header', {}).get('file_version_ue4', 'N/A')}\n"
            f"File Size: {data.get('header', {}).get('file_size', 'N/A')} bytes\n\n"
            f"Metadata:\n"
            f"Flags: {data.get('metadata', {}).get('flags', 'N/A')}\n"
            f"Element Count: {data.get('metadata', {}).get('element_count', 'N/A')}\n"
            f"Bulk Data Size: {data.get('metadata', {}).get('bulk_data_size', 'N/A')} bytes\n"
            "---"
        )
    except Exception as e:
        return f"Error formatting asset data: {str(e)}"

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can read and analyze binary files.
    """
    if not arguments:
        return [types.TextContent(type="text", text="Missing arguments for the request")]
    
    if name == "read-unreal-asset":
        file_path = arguments.get("file_path")
        if not file_path:
            return [types.TextContent(type="text", text="Missing file_path parameter")]

        try:
            with UnrealAssetReader(file_path) as reader:
                data = {
                    "header": reader.read_header(),
                    "metadata": reader.read_metadata(),
                }
                
                formatted_data = format_unreal_asset_data(data)
                return [types.TextContent(type="text", text=formatted_data)]
                
        except FileNotFoundError:
            return [types.TextContent(type="text", text=f"Error: File not found - {file_path}")]
        except ValueError as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Unexpected error: {str(e)}")]

    elif name == "read-binary-metadata":
        file_path = arguments.get("file_path")
        if not file_path:
            return [types.TextContent(type="text", text="Missing file_path parameter")]

        format_type = arguments.get("format", "auto")
        
        try:
            # Auto-detect format or use specified format
            if format_type == "unreal" or (format_type == "auto" and file_path.endswith(".uasset")):
                reader_class = UnrealAssetReader
            else:
                reader_class = BinaryReader

            with reader_class(file_path) as reader:
                metadata = {
                    "file_size": os.path.getsize(file_path),
                    "header": reader.read_header() if hasattr(reader, "read_header") else None,
                    "metadata": reader.read_metadata() if hasattr(reader, "read_metadata") else None
                }

                formatted_text = (
                    f"Binary File Analysis:\n\n"
                    f"File Path: {file_path}\n"
                    f"File Size: {metadata['file_size']} bytes\n"
                    f"Format: {format_type}\n\n"
                )

                if metadata["header"]:
                    formatted_text += f"Header Information:\n{metadata['header']}\n\n"
                if metadata["metadata"]:
                    formatted_text += f"Metadata Information:\n{metadata['metadata']}"

                return [types.TextContent(type="text", text=formatted_text)]

        except FileNotFoundError:
            return [types.TextContent(type="text", text=f"Error: File not found - {file_path}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error analyzing file: {str(e)}")]
    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="binary_reader",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())