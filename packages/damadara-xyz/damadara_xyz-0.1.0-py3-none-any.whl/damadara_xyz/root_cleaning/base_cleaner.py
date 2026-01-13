import datetime


class BaseCleaner:
def __init__(self, module_name: str):
self.module_name = module_name
self.report = {
"module": module_name,
"status": False,
"summary": "",
"details": {},
"timestamp": None,
}


def finalize_report(self, success=True, summary="", details=None):
self.report["status"] = success
self.report["summary"] = summary
self.report["details"] = details or {}
self.report["timestamp"] = datetime.datetime.now().isoformat()
return self.report