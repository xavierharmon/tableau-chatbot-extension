class TableauBridge:
    """
    Manages session-scoped state that mirrors what the JS version
    stored in tableau.extensions.settings — conversation history,
    loaded data context, and basic session config.
    """

    def __init__(self):
        self.data_context: str  = ""
        self.file_name:    str  = ""
        self.sheet_name:   str  = ""
        self.columns:      list = []
        self.row_count:    int  = 0
        self.history:      list = []   # [{role, content}, ...]
        self.data_ready:   bool = False

    def load_data(self, parsed: dict):
        self.data_context = parsed["data_context"]
        self.file_name    = parsed["file_name"]
        self.sheet_name   = parsed["sheet_name"]
        self.columns      = parsed["columns"]
        self.row_count    = len(parsed["rows"])
        self.data_ready   = True
        self.history      = []   # reset conversation on new data load

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def reset(self):
        self.__init__()

    def summary(self) -> dict:
        return {
            "file_name":  self.file_name,
            "sheet_name": self.sheet_name,
            "columns":    self.columns,
            "row_count":  self.row_count,
            "data_ready": self.data_ready
        }