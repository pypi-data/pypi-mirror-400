import argparse
import os
from .core import convert_all_to_md

def main():
    parser = argparse.ArgumentParser(description="Convert documents to Markdown.")
    parser.add_argument("source_dir", nargs="?", default="src")
    parser.add_argument("target_dir", nargs="?", default=os.path.join("output", "markdown"))
    parser.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY"))
    args = parser.parse_args()

    convert_all_to_md(args.source_dir, args.target_dir, args.api_key)

if __name__ == "__main__":
    main()
