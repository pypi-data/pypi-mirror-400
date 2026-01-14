from bs4 import BeautifulSoup
import re
import os

def del_garbage(text: str) -> str:
    out = ""

    for i, char in enumerate(text):
        if not char in "\t\n ":
            out += text[i:]
            break

    i = len(out)
    while i > 1:
        i -= 1
        char = out[i]
        if not char in "\n\t ":
            return out[:i + 1]
    return out

def sum_paths(*paths: str) -> str:
    out = ""
    for path in paths:
        if len(path) > 0:
            if del_garbage(path).replace("/", "\\")[-1] == "\\":
                out += del_garbage(path).replace("/", "\\")
            else:
                out += del_garbage(path).replace("/", "\\") + "\\"
    return out[:-1]

def split_first(text: str, char: str) -> tuple[str, str]:
    return text.split(char)[0], char.join(text.split(char)[1:])

def split_last(text: str, char: str) -> tuple[str, str]:
    return char.join(text.split(char)[:-1]), text.split(char)[-1]

def preprocess_index(path_to_index: str, path_to_static: str) -> None:
    def clear_path(path: str) -> str:
        if path.split(":")[0] in ["https", "http"]:
            return split_first(path[len(path.split(":")[0]) + 3:], "/")[1]
        
        if path.startswith("localhost"):
            return split_first(path, "/")[1]

        if not path[0] in [".", " ", "/"]:
            return path

        i = -1
        while i < len(path) - 1:
            i += 1

            if path[i] == "/":
                return path[i + 1:]

        return path

    def shield_static(path: str) -> str:
        path = clear_path(path)

        fragment = ""

        i = -1
        while i < len(path) - 1:
            i += 1

            if path[i] != "/":
                fragment += path[i]
            else:
                if fragment == "static":
                    return f"/static_/{"/".join(path.split("/")[1:])}"
                return f"/{path}"

        return f"/{path}"

    def replace_head(html: str, head: str) -> str:
        head_pattern = re.compile(r'<head>.*?</head>', re.IGNORECASE | re.DOTALL)
        return head_pattern.sub(head, html)

    out = ""

    with open(path_to_index, "r", encoding="utf-8") as f:
        parser = BeautifulSoup(f.read(), "html.parser")
        
        head = "<head"
        for key, value in parser.find("head").attrs:
            head += f" {key}={value}"
        head += ">"

        tags = parser.find("head").find_all()
        for tag in tags:
            if tag.has_attr("href") and tag.name != "a":
                tag.attrs["href"] = shield_static(del_garbage(tag.get("href")).replace("\\", "/"))

            elif tag.has_attr("src"):
                tag.attrs["src"] = shield_static(del_garbage(tag.get("src")).replace("\\", "/"))

            head += tag.decode()

        head += "</head>"

        out = replace_head(parser.decode(), head)

    with open(path_to_index, "w", encoding="utf-8") as f:
        f.write(out)

    try:
        os.rename(path_to_static, path_to_static + "_")
    except FileNotFoundError:
        pass

# In future:
# def rinfo(name, data, tabs, tab) -> None:
#     print(f"{tab*tabs}{name}:" + " {")
#     for key, value in data.items():
#         if not isinstance(value, dict):
#             print(f"{tab*(tabs+1)}{key}: {value}")
#         else:
#             rinfo(key, value, tabs+1, tab)
#     print(f"{tab*tabs}" + "}")

# def info(request: Request, tab_size: int = 4) -> None:
#     tab = " "*tab_size

#     if not isinstance(request, Request):
#         print("Not request")
#         return
    
#     print(f"Request <{request.content_type}> :" + " {")
#     for key, value in request.json.items():
#         if not isinstance(value, dict):
#             print(f"{tab}{key}: {value}")
#         else:
#             rinfo(key, value, 1, tab)
#     print("}")