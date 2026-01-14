import os
import pathlib
import re
from markitdown import MarkItDown

def clean_markdown(text):
    """
    Clean the markdown content by removing 'Unnamed: ...' and 'NaN'.
    """
    if not text:
        return ""
    text = re.sub(r'Unnamed: \d+', '', text)
    text = re.sub(r'\bNaN\b', '', text)
    return text

def convert_all_to_md(source_dir, target_dir, openai_api_key=None):
    llm_client = None
    llm_model = None

    if openai_api_key:
        try:
            from openai import OpenAI
            llm_client = OpenAI(api_key=openai_api_key)
            llm_model = "gpt-4o"
            print("LLM support enabled for image description.")
        except Exception as e:
            print(f"Warning: LLM disabled: {e}")

    md = MarkItDown(llm_client=llm_client, llm_model=llm_model)

    os.makedirs(target_dir, exist_ok=True)

    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.startswith('~$'):
                continue

            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, source_dir)
            target_dir_path = os.path.join(target_dir, os.path.dirname(relative_path))
            os.makedirs(target_dir_path, exist_ok=True)

            target_file = os.path.join(
                target_dir_path,
                f"{pathlib.Path(file).stem}.md"
            )

            try:
                result = md.convert(file_path)
                if result and result.text_content:
                    with open(target_file, "w", encoding="utf-8") as f:
                        f.write(clean_markdown(result.text_content))
            except Exception as e:
                print(f"Error converting {file_path}: {e}")
