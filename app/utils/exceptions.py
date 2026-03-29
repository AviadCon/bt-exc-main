class TranscriptFailureException(Exception):
    def __init__(self, message: str = "Transcript extraction failed", original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self):
        if self.original_error:
            return f"{self.message}: {str(self.original_error)}"
        return self.message


class AudioExtractionException(Exception):
    def __init__(self, message: str = "Audio extraction failed", original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self):
        if self.original_error:
            return f"{self.message}: {str(self.original_error)}"
        return self.message
