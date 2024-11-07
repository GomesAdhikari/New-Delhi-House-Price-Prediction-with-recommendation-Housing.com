import sys

def error_message(error:Exception,detail:sys):
    _,_,exc_tb = detail.exc_info()
    filename = exc_tb.tb_frame.f_code.co_filename
    line_no = exc_tb.tb_lineno

    error_message = f"Error Occured in file [{filename}] line no - [{line_no}]  message - [{error}]"
    return error_message
class CustomException(Exception):
    
    def __init__(self,error_message,detail):
        super().__init__(error_message)
        self.error_mesage = error_message(error_message,detail=detail)

    def __str__(self):
        return self.error_mesage
    

