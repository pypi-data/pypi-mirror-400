from bs4 import BeautifulSoup
from markdownify import markdownify as md

# Load the HTML
with open("openai-images.html", "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

# Try to find the main documentation area
main = soup.find("main")
if not main:
    # Fall back to something else if <main> doesn't exist
    main = soup.find("body")

# Convert HTML to Markdown
markdown = md(str(main), heading_style="ATX")

# Save to a .md file
with open("openai-images.md", "w", encoding="utf-8") as mdfile:
    mdfile.write(markdown)

print("✅ Markdown file created: openai-images.md")