import logging
import inspect
from datetime import datetime
from database import store_log_in_db

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def log(message, user_id=None):
    timestamp = datetime.now()
    # Get the name of the function and file where the error occurred
    caller_frame = inspect.stack()[1]
    file_name = caller_frame.filename
    function_name = caller_frame.function
    logging.error(message)
    store_log_in_db(message, timestamp, file_name, function_name,user_id)
