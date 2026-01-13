class DynamicTable:
    def __init__(self, headers=None):
        self.headers = headers if headers else []
        self.rows = []

    def add_header(self, header):
        self.headers.append(header)

    def add_row(self, row):
        if self.headers and len(row) != len(self.headers):
            raise ValueError("Row length must match headers length")
        self.rows.append(row)

    def display(self):
        if self.headers:
            header_line = " | ".join(self.headers)
            print(header_line)
            print("-" * len(header_line))

        for row in self.rows:
            print(" | ".join(map(str, row)))
