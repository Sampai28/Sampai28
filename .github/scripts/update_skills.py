import os, re, requests

USERNAME = os.environ.get("USERNAME", "Sampai28")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.mercy-preview+json"}

# Map: keyword → (badge label, shield logo slug, hex color)
KEYWORD_MAP = {
    # Languages (detected from repo.language)
    "Python":           ("Python",       "python",        "1e3a5f"),
    "TypeScript":       ("TypeScript",   "typescript",    "1e3a5f"),
    "JavaScript":       ("JavaScript",   "javascript",    "1e3a5f"),
    "Jupyter Notebook": ("Jupyter",      "jupyter",       "1e3a5f"),
    "R":                ("R",            "r",             "1e3a5f"),
    "HTML":             ("HTML",         "html5",         "1e3a5f"),
    "CSS":              ("CSS",          "css3",          "1e3a5f"),
    "Shell":            ("Shell",        "gnubash",       "1e3a5f"),
    "Go":               ("Go",           "go",            "1e3a5f"),
    "Java":             ("Java",         "openjdk",       "1e3a5f"),
    "C++":              ("C++",          "cplusplus",     "1e3a5f"),
    "Rust":             ("Rust",         "rust",          "1e3a5f"),
}

TOPIC_KEYWORD_MAP = {
    # ML / AI
    "openai":        ("OpenAI",      "openai",        "0d2137"),
    "pytorch":       ("PyTorch",     "pytorch",       "0d2137"),
    "tensorflow":    ("TensorFlow",  "tensorflow",    "0d2137"),
    "langchain":     ("LangChain",   "chainlink",     "0d2137"),
    "scikit":        ("Scikit-Learn","scikitlearn",   "0d2137"),
    "pandas":        ("Pandas",      "pandas",        "0d2137"),
    "numpy":         ("NumPy",       "numpy",         "0d2137"),
    "huggingface":   ("HuggingFace", "huggingface",   "0d2137"),
    "transformers":  ("Transformers","huggingface",   "0d2137"),
    "streamlit":     ("Streamlit",   "streamlit",     "0d2137"),
    # Web / Backend
    "fastapi":       ("FastAPI",     "fastapi",       "0d2137"),
    "flask":         ("Flask",       "flask",         "0d2137"),
    "react":         ("React",       "react",         "0d2137"),
    "nextjs":        ("Next.js",     "nextdotjs",     "0d2137"),
    "nodejs":        ("Node.js",     "nodedotjs",     "0d2137"),
    # Data / Infra
    "postgresql":    ("PostgreSQL",  "postgresql",    "132847"),
    "mongodb":       ("MongoDB",     "mongodb",       "132847"),
    "neo4j":         ("Neo4j",       "neo4j",         "132847"),
    "docker":        ("Docker",      "docker",        "132847"),
    "aws":           ("AWS",         "amazonaws",     "132847"),
    "graphql":       ("GraphQL",     "graphql",       "132847"),
}

def badge(label, logo, color):
    encoded = label.replace("-", "--").replace(" ", "_")
    return f"![{label}](https://img.shields.io/badge/{encoded}-{color}?style=for-the-badge&logo={logo}&logoColor=white)"

def get_repos():
    repos, page = [], 1
    while True:
        r = requests.get(f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}", headers=HEADERS)
        data = r.json()
        if not data: break
        repos.extend(data)
        page += 1
    return repos

def get_topics(repo_name):
    r = requests.get(f"https://api.github.com/repos/{USERNAME}/{repo_name}/topics", headers=HEADERS)
    return r.json().get("names", []) if r.ok else []

def scan():
    repos = get_repos()
    langs, tools = set(), set()

    for repo in repos:
        if repo.get("language"):
            langs.add(repo["language"])

        topics = get_topics(repo["name"])
        text = " ".join([repo["name"], repo.get("description") or ""] + topics).lower()

        for kw, val in TOPIC_KEYWORD_MAP.items():
            if kw in text:
                tools.add(val)

    return langs, tools

def build_section(langs, tools):
    lang_badges = "\n".join(
        badge(*KEYWORD_MAP[l]) for l in sorted(langs) if l in KEYWORD_MAP
    )
    tool_badges = "\n".join(
        badge(*t) for t in sorted(tools, key=lambda x: x[0])
    )

    lines = ["**Languages**\n", lang_badges or "_None detected yet_"]
    if tool_badges:
        lines += ["\n**Frameworks & Tools**\n", tool_badges]

    return "\n".join(lines)

def update_readme(section_md):
    with open("README.md", "r") as f:
        content = f.read()

    new_block = f"<!-- SKILLS_START -->\n{section_md}\n<!-- SKILLS_END -->"
    updated = re.sub(r"<!-- SKILLS_START -->.*?<!-- SKILLS_END -->", new_block, content, flags=re.DOTALL)

    with open("README.md", "w") as f:
        f.write(updated)
    print("✅ README updated successfully.")

if __name__ == "__main__":
    print("🔍 Scanning repos...")
    langs, tools = scan()
    print(f"   Languages: {langs}")
    print(f"   Tools: {[t[0] for t in tools]}")
    section = build_section(langs, tools)
    update_readme(section)
