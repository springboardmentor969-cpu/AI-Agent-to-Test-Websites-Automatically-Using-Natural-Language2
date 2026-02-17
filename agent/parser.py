from nltk.stem import WordNetLemmatizer
import re

lemmatizer = WordNetLemmatizer()

def normalize(text):
    words = re.findall(r"\w+", text.lower())
    return [lemmatizer.lemmatize(w) for w in words]

def parse_instruction(text):
    tokens = normalize(text)

    actions = []

    if "open" in tokens:
        if "login" in tokens:
            actions.append({"action": "open_page", "value": "login"})

    if "enter" in tokens or "type" in tokens:
        if "username" in tokens:
            actions.append({"action": "enter_text", "field": "username"})
        if "password" in tokens:
            actions.append({"action": "enter_text", "field": "password"})

    if "click" in tokens:
        if "login" in tokens:
            actions.append({"action": "click", "target": "login_button"})

    return actions


if __name__ == "__main__":
    sample = "Open login page and enter username and password then click login"

    print(parse_instruction(sample))
