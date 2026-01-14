import re
from dataclasses import dataclass
from typing import Any

from .base_parser import BaseParser


@dataclass
class CUDAKernel:
    name: str
    line: int
    parameters: list[str]


class CUDAParser(BaseParser):

    def parse_file(self, content: str) -> dict[str, Any]:
        kernels: list[CUDAKernel] = []

        pattern = r'__global__\s+(?:__device__\s+)?(?:void|.*?)\s+(\w+)\s*\('

        for match in re.finditer(pattern, content):
            line = content[:match.start()].count('\n')
            kernel_name = match.group(1)

            params = self._extract_parameters(content, match.end())

            kernels.append(CUDAKernel(
                name=kernel_name,
                line=line,
                parameters=params
            ))

        return {"kernels": kernels}

    def _extract_parameters(self, content: str, start: int) -> list[str]:
        if start >= len(content):
            return []

        depth = 0
        param_start = start
        param_end = start

        for i in range(start, len(content)):
            char = content[i]
            if char == '(':
                depth += 1
            elif char == ')':
                depth -= 1
                if depth == 0:
                    param_end = i
                    break

        if param_end == start:
            return []

        param_str = content[param_start:param_end + 1]

        params: list[str] = []
        current_param = ""
        template_depth = 0
        paren_depth = 0

        for char in param_str[1:-1]:
            if char == '<':
                template_depth += 1
                current_param += char
            elif char == '>':
                template_depth -= 1
                current_param += char
            elif char == '(':
                paren_depth += 1
                current_param += char
            elif char == ')':
                paren_depth -= 1
                current_param += char
            elif char == ',' and template_depth == 0 and paren_depth == 0:
                param_name = current_param.strip()
                if param_name:
                    parts = param_name.split()
                    if parts:
                        name = parts[-1].strip('*&')
                        params.append(name)
                current_param = ""
            else:
                current_param += char

        if current_param.strip():
            param_name = current_param.strip()
            parts = param_name.split()
            if parts:
                name = parts[-1].strip('*&')
                params.append(name)

        return params
