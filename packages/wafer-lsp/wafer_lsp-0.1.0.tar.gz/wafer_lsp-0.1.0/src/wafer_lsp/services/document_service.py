from pygls.lsp.server import LanguageServer


class DocumentService:

    def __init__(self, server: LanguageServer):
        self._server = server

    def get_document(self, uri: str):
        return self._server.workspace.text_documents.get(uri)

    def get_document_content(self, uri: str) -> str:
        doc = self.get_document(uri)
        if doc is None:
            return ''
        return getattr(doc, 'text', getattr(doc, 'source', ''))


def create_document_service(server: LanguageServer) -> DocumentService:
    return DocumentService(server)
