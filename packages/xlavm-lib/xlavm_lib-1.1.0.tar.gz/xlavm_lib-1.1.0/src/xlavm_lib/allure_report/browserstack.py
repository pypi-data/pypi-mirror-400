class Browserstack():

    def __init__(self, driver):
        self.driver = driver
        
    def log_debug(self, message):
        self.driver.execute_script('browserstack_executor: {"action": "annotate", "arguments": {"data":"'+ message +'", "level": "debug"}}')
        
    def log_error(self, message):
        self.driver.execute_script('browserstack_executor: {"action": "annotate", "arguments": {"data":"'+ message +'", "level": "error"}}')
    
    def log_info(self, message):
        self.driver.execute_script('browserstack_executor: {"action": "annotate", "arguments": {"data":"'+ message +'", "level": "info"}}')

    def network_offline(self):
        self.driver.execute_script('browserstack_executor: {"action": "setNetworkProfile", "arguments": {"profile": "offline"}}')

    def network_online(self):
        self.driver.execute_script('browserstack_executor: {"action": "setNetworkProfile", "arguments": {"profile": "full"}}')
        
    def mark_failed(self, message): 
        self.driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status": "failed", "reason": "'+ message +'"}}')
    
    def mark_passed(self, message): 
        self.driver.execute_script('browserstack_executor: {"action": "setSessionStatus", "arguments": {"status": "passed", "reason": "'+ message +'"}}')
