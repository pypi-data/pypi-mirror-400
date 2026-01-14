from pathlib import Path


class DocsIndex:

    def __init__(self, docs_path: str | None = None):
        if docs_path:
            self.docs_path = Path(docs_path)
        else:
            self.docs_path = Path(__file__).parent.parent.parent.parent.parent / \
                "curriculum" / "cutlass-docs" / "cutedsl-docs"

        self.index = self._build_index()

    def _build_index(self) -> dict[str, list[str]]:
        return {
            "layout": [
                "intro-to-cutedsl.md",
                "partitioning-strategies-inner-outer-threadvalue.md"
            ],
            "TMA": ["blackwell-tutorial-fp16-gemm-0.md"],
            "TMEM": ["colfax-blackwell-umma-tensor-memory-part1.md"],
            "kernel": ["blackwell-tutorial-fp16-gemm-0.md"],
            "struct": ["blackwell-tutorial-fp16-gemm-0.md"],
            "pipeline": ["blackwell-tutorial-fp16-gemm-0.md"],
            "MMA": ["mma-atoms-fundamentals-sm70-example.md"],
        }

    def get_doc_for_concept(self, concept: str) -> str | None:
        concept_lower = concept.lower()
        if self.index.get(concept_lower):
            doc_file = self.index[concept_lower][0]
            doc_path = self.docs_path / doc_file
            if doc_path.exists():
                return str(doc_path)
        return None
