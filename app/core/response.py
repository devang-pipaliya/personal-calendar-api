
def success_response(data:str=None, message:str=None) -> dict:
    return {
        "data": data,
        "message": message,
        "status": True
    }

def failure_response(message:str=None, error:str=None, err_code:str=0, err_stack:str=None) -> dict:
    return {
        "status": False,
        "data": [],
        "message": message,
        "error": error,
        "err_code": err_code,
        "err_stack": err_stack
    }
