import os
import allure
import requests
from xlavm_lib.allure_report.browserstack import Browserstack
from xlavm_lib.allure_report.video_recorder_mobile import VideoRecorderMobile
from xlavm_lib.allure_report.video_recorder_web import VideoRecorderWeb
import env
import random

class AllureReport():
    """
    Crea un reporte en Allure ya sea para ejecuciones locales o de Browserstack
    
    Prerrequisitos:
        En el conftest.py se crean estos hooks:
        from xlavm_lib import AllureReport
        # HOOKS
        def pytest_runtest_call(item):
            report = getattr(item, "report", None)
            if report:
                report.start_record_video()
                
        def pytest_runtest_teardown(item):
            report = getattr(item, "report", None)
            if report:
                report.stop_record_video()
        
        En el conftest.py dentro de la funcion driver(request) y y antes del driver.quit(), se
        debe ubicar:
        request.node.report = AllureReport(driver)
        
        Se debe crear el archivo env.py en la raiz del proyecto con los siguientes valores (si no usas Browserstack, dejalos vacio)
        import os
        os.environ["BROWSERSTACK_USERNAME"] = "tu_username"
        os.environ["BROWSERSTACK_ACCESS_KEY"] = "tu_access_key"
        
    Uso:
        from xlavm_lib import AllureReport
        AllureReport(driver).step("1. Ingreso credenciales validas", request.node.name)
        AllureReport(driver).info("este es un mensaje infomativo")
        AllureReport(driver).error("este es un mensaje de error")
        
    Args:
        driver (driver): Driver web o mobile
    """
    
    video_path_web = f"videos/evidencia.mp4"
    web_recorder = VideoRecorderWeb(video_path_web)
    
    def __init__(self, driver):
        self.driver = driver
        self.mobile_recorder = None
        # BrowserStack credentials (desde ENV)
        self.BS_username = os.getenv("BROWSERSTACK_USERNAME")
        self.BS_access_key = os.getenv("BROWSERSTACK_ACCESS_KEY")
        self.BS_session_id = None
        if not self.BS_username or not self.BS_access_key:
            raise EnvironmentError("Variables de entorno BROWSERSTACK_USERNAME / BROWSERSTACK_ACCESS_KEY no definidas")
        
    def info(self, description):
        with allure.step(description):
            pass
        if not self.is_local_execution():
            browserstack = Browserstack(self.driver)
            browserstack.log_debug(description)
            
    def error(self, description):
        if not self.is_local_execution():
            browserstack = Browserstack(self.driver)
            browserstack.log_error(description)
        with allure.step(description):
            assert False, description

    def step(self, description, TC):
        """
        - Use:
        report.step(description, request.node.name)
        """
        SC_PATH = f'screenshots/evidences/{TC}/{description}.png'
        with allure.step(description):
            with allure.step("Evidencia"):
                os.makedirs(os.path.dirname(SC_PATH), exist_ok=True)  
                self.driver.save_screenshot(SC_PATH)
                with open(SC_PATH, "rb") as image_file:
                    allure.attach(image_file.read(), name="Evidencia", attachment_type=allure.attachment_type.PNG)
     
    """
    Metodo que se ejecuta antes del 'yield driver' para grabar evidencias
    """
    def start_record_video(self):
        if self.is_local_execution():
            if self.driver.platform in ["android", "ios"]:
                self.mobile_recorder = VideoRecorderMobile(self.driver)
                self.mobile_recorder.start()
            else:
                self.web_recorder.start()
        else:
            """Uso BS, entonces guardo el session id para obtener el video"""
            self.BS_session_id = self.driver.session_id
    
    """
    Metodo que se ejecuta despues del 'driver.quit' para detener la grabacion y guardar evidencias
    """
    def stop_record_video(self):
        if self.is_local_execution():
            if self.driver.platform in ["android", "ios"]:
                if self.mobile_recorder:
                    self.mobile_recorder.stop()
            else:
                self.web_recorder.stop()
                if os.path.exists(self.video_path_web):
                    with open(self.video_path_web, "rb") as video:
                        allure.attach(
                            video.read(),
                            name="Video Evidencia de la Prueba",
                            attachment_type=allure.attachment_type.MP4
                        )
        else:
            video_url = self.get_browserstack_video_url(self.BS_session_id, self.BS_username, self.BS_access_key)
            if video_url:
                allure.attach(
                    video_url,
                    name="Video Evidencia de la Prueba en BrowserStack",
                    attachment_type=allure.attachment_type.URI_LIST
                )
        # tomo pantallazo despues de la grabacion
        SC_PATH = f'screenshots/evidences/post_record/post-{random.random()}.png'
        os.makedirs(os.path.dirname(SC_PATH), exist_ok=True)
        self.driver.save_screenshot(SC_PATH)
        with open(SC_PATH, "rb") as image_file:
            allure.attach(
                image_file.read(),
                name="Screenshot Final",
                attachment_type=allure.attachment_type.PNG
            )

    """
    Este metodo verifica si la ejecucion es local o desde Browserstack
    """
    def is_local_execution(self):
        return "hub-use.browserstack.com" not in str(self.driver.capabilities)
    
    """
    Este metodo obtiene la url del video que se graba en Browserstack
    """
    def get_browserstack_video_url(self, session_id, user, key):
        if self.driver.platform in ["android", "ios"]:
            url = f"https://api.browserstack.com/app-automate/sessions/{session_id}.json" # para mobile
        else:
            url = f"https://api.browserstack.com/automate/sessions/{session_id}.json" # para web
        response = requests.get(url, auth=(user, key))
        response.raise_for_status()
        return response.json()["automation_session"]["video_url"]
