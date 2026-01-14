import json
import re
import uuid
from enum import Enum


class StiFunctions:

### String

    def getJavaScriptValue(value) -> str:
        if value is None:
            return 'null'
        
        return json.dumps(value, ensure_ascii=False).replace('\\/', '/')

    def isNullOrEmpty(value) -> bool:
        return len(value or '') == 0
    
    def newGuid(length = 16) -> str:
        return uuid.uuid4().hex[:length]

    def isJavaScriptFunctionName(value) -> bool:
        return re.search("^[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*$", value)
    
    def isDashboardsProduct() -> bool:
        try:
            from stimulsoft_dashboards.report.StiDashboard import StiDashboard
        except Exception as e:
            return False
        
        return True
