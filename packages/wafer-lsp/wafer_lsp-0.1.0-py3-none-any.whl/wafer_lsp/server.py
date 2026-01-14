from lsprotocol.types import (
    INITIALIZE,
    TEXT_DOCUMENT_HOVER,
)
from pygls.lsp.server import LanguageServer

from .services import (
    create_analysis_service,
    create_docs_service,
    create_document_service,
    create_hover_service,
    create_language_registry_service,
    create_position_service,
)

language_registry_service = create_language_registry_service()
analysis_service = create_analysis_service()
docs_service = create_docs_service()
position_service = create_position_service()
hover_service = create_hover_service(
    language_registry_service,
    analysis_service,
    docs_service,
    position_service
)

server = LanguageServer("wafer-lsp", "1.0.0")
document_service = create_document_service(server)


@server.feature(INITIALIZE)
def initialize(params):
    return {
        "capabilities": {
            "hoverProvider": True,
        }
    }


@server.feature(TEXT_DOCUMENT_HOVER)
def hover(params):
    uri = params.text_document.uri
    position = params.position
    content = document_service.get_document_content(uri)
    if not content:
        test_message = "🎉🎉🎉 **HEYOOO!!! LSP IS DEFINITELY WORKING!!!** 🎉🎉🎉\n\n**THIS IS THE WAFER LSP SERVER!**\n\n**Document content not available, but LSP is running!**"
        from lsprotocol.types import Hover, MarkupContent, MarkupKind
        return Hover(contents=MarkupContent(kind=MarkupKind.Markdown, value=test_message))
    result = hover_service.handle_hover(uri, position, content)
    if not result:
        test_message = "🎉🎉🎉 **HEYOOO!!! LSP IS DEFINITELY WORKING!!!** 🎉🎉🎉\n\n**THIS IS THE WAFER LSP SERVER!**\n\n**Hover service returned None, but LSP is running!**"
        from lsprotocol.types import Hover, MarkupContent, MarkupKind
        return Hover(contents=MarkupContent(kind=MarkupKind.Markdown, value=test_message))
    return result


if __name__ == "__main__":
    server.start_io()
