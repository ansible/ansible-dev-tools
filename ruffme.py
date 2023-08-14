import requests

from bs4 import BeautifulSoup


url = "https://github.com/charliermarsh/ruff/issues/970"

response = requests.get(url)
html_content = response.content
soup = BeautifulSoup(html_content, "html.parser")
li_tags = soup.find_all("li")

done = []
for li in li_tags:
    if "class" in li.attrs and "task-list-item" in li.attrs["class"]:
        names = [child.name for child in li.children if child.name]
        if "input" in names and "code" in names:
            checked = [
                child.attrs.get("checked")
                for child in li.children
                if child.name and child.name == "input" and "checked" in child.attrs
            ]
            if checked:
                codes = [child.text for child in li.children if child.name == "code"]
                done.append(tuple(codes))

done.sort(key=lambda x: x[1])

for entry in done:
    name = entry[0]
    pylint_code = entry[1]

    ruff_code = entry[2] if len(entry) == 3 else f"PL{entry[1]}"
    print(f'  "{pylint_code}", # {name} / ruff {ruff_code}')
