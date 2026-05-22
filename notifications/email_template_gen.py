class EmailTemplateGen:
    def fill(self, regex_string: str, line: str) -> str:
        return f"Regex: {regex_string}\nMatch:\n{line}"
