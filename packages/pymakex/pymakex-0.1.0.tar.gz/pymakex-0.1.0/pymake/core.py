class Compiler:
    def __init__(self, source_code=None):
        self.source_code = source_code
        self.tokens = []
        self.ast = None

    def tokenize(self):
        if not self.source_code:
            raise ValueError("No source code provided")
        return self.tokens

    def parse(self):
        if not self.tokens:
            self.tokenize()
        return self.ast

    def compile(self):
        self.parse()
        return "Compiled successfully"

    def execute(self):
        compiled_code = self.compile()
        return f"Executing: {compiled_code}"
