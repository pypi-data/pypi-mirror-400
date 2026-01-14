# ai_test_generator.py
import os
import argparse
from pathlib import Path
import tomllib
import openai

MODEL = "gpt-4.1-2025-04-14"
TEMP = 0.2


class Dictdot:
    def __init__(self, dictionnary: dict):
        self.dictionnary = dict(dictionnary or {})

    def get(self, key, default=Ellipsis):
        if key not in self.dictionnary:
            return default if default is not Ellipsis else Dictdot(None)

        value = self.dictionnary[key]
        return Dictdot(value) if isinstance(value, dict) else value

    def scan(self, path: str, default=None):
        if "." in path:
            head, rest = path.split(".", maxsplit=1)
            return self.get(head).scan(rest, default)
        return self.get(path, default)


def parse_args():
    p = argparse.ArgumentParser(description="Auto-generate pytest+Hypothesis tests")
    p.add_argument(
        "--project-dir",
        "-p",
        type=Path,
        help="Path to project root (pyproject.toml)",
    )
    p.add_argument(
        "--tests-dir",
        "-t",
        type=Path,
        default=None,
        help="Output tests folder (default: <project>/tests)",
    )
    p.add_argument(
        "--api-key",
        "-a",
        type=str,
        default=None,
        help="Openai api key",
    )
    return p.parse_args()


def get_source_packages(root: Path):
    with open(root / "pyproject.toml", "rb") as file:
        config = tomllib.load(file)

    # if uv package defined
    packages = Dictdot(config).scan("tool.hatch.build.targets.wheel.packages", None)
    if packages:
        return [root / pkg_name for pkg_name in packages]

    # fallback: src/ or root modules
    src_path: Path = root / "src"
    if src_path.is_dir():
        return [src_path]
    return [root]


def load_python_files(src_dirs):
    for src in src_dirs:
        for f in src.rglob("*.py"):
            if f.name.startswith("test_") or f.name == "__init__.py":
                continue
            yield f


def ai_generate_pytest(client, filename, code):
    prompt = f"""You are an AI test engineer. Generate a pytest module with:
    - unit tests for all public functions/classes
    - property-based tests (using hypothesis) for data invariants
    - edge and error cases
    - well-documented fixtures for complex inputs

    Provide only valid Python code.

    Filename: {filename}
    ```python
    {code}
    ```
    """
    completion = openai.chat.completions.create(
        model=MODEL,
        temperature=TEMP,
        messages=[
            {"role": "system", "content": "Generate pytest+Hypothesis tests."},
            {"role": "user", "content": prompt},
        ],
    )
    return completion.choices[0].message.content


def main():
    args = parse_args()
    project = args.project_dir.resolve()
    tests_dir = (args.tests_dir or project / "tests").resolve()
    src_dirs = get_source_packages(project)
    tests_dir.mkdir(parents=True, exist_ok=True)
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key
    client = openai.OpenAI()
    for src in src_dirs:
        for f in load_python_files([src]):
            rel = f.relative_to(src)
            out_dir = (tests_dir / rel.parent).resolve()
            out_dir.mkdir(parents=True, exist_ok=True)
            code = f.read_text()
            tests = ai_generate_pytest(client, f.name, code)
            out_file = out_dir / f"test_{f.stem}.py"
            out_file.write_text(tests + "\n")
    print(f"✅ Tests generated in {tests_dir}")


if __name__ == "__main__":
    main()
