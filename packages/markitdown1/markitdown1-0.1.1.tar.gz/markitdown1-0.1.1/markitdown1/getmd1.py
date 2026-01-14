import sys
import re
import requests
from urllib.parse import urlparse

def safe_filename(name: str) -> str:
    """
    修正文件名，移除各平台不允许的字符
    """
    name = name.strip()
    name = re.sub(r'[\\/:*?"<>|]', '_', name)
    name = re.sub(r'\s+', ' ', name)
    return name

def handle_github(url: str):
    """
    处理 GitHub 仓库 README
    """
    parts = url.rstrip('/').split('/')
    if len(parts) < 5:
        raise ValueError("无效的 GitHub 仓库 URL")

    user = parts[-2]
    repo = parts[-1]

    readme_url = f"https://raw.githubusercontent.com/{user}/{repo}/master/README.md"

    resp = requests.get(readme_url)
    if resp.status_code != 200:
        raise RuntimeError("未找到 README.md（可能不是 master 分支）")

    filename = safe_filename(f"github_{user}_{repo}.md")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(resp.text)

    print(f"✅ GitHub README 已保存为: {filename}")

def extract_qiita_title_from_metadata(md_text: str) -> str:
    """
    从 Qiita Markdown 的 YAML metadata 中提取 title
    """
    lines = md_text.splitlines()

    if not lines or lines[0].strip() != "---":
        return "untitled"

    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("title:"):
            return line[len("title:"):].strip().strip('"').strip("'")

    return "untitled"

def handle_qiita(url: str):
    """
    处理 Qiita 文章
    """
    if not url.endswith(".md"):
        md_url = url + ".md"
    else:
        md_url = url

    parts = url.rstrip('/').split('/')
    if len(parts) < 5:
        raise ValueError("无效的 Qiita URL")

    user = parts[-3]

    resp = requests.get(md_url)
    if resp.status_code != 200:
        raise RuntimeError("Qiita Markdown 下载失败")

    content = resp.text

    title = extract_qiita_title_from_metadata(content)

    filename = safe_filename(f"qiita_{user}_{title}.md")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Qiita 文章已保存为: {filename}")


def main():
    if len(sys.argv) != 2:
        print("用法: getmd1 <url>")
        sys.exit(1)

    url = sys.argv[1]

    if "github.com" in url:
        handle_github(url)
    elif "qiita.com" in url:
        handle_qiita(url)
    else:
        raise ValueError("暂不支持该 URL 类型")

if __name__ == "__main__":
    main()
