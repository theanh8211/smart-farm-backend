from fastapi import HTTPException

class AgentNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Agent not found")

class CameraError(HTTPException):
    def __init__(self, detail="Camera error"):
        super().__init__(status_code=500, detail=detail)