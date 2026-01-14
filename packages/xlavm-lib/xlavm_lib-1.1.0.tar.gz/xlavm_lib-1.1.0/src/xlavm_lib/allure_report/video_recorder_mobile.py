import time
import base64
import threading
import allure

class VideoRecorderMobile:
    """
    170 porque el recording_screen del driver para mobiles graba solo 3 minutos, entonces
    cuando este en 170, haga otra grabacion parte 2
    """
    def __init__(self, driver, max_seconds=170, check_interval=5):
        self.driver = driver
        self.max_seconds = max_seconds
        self.check_interval = check_interval
        self.segment = 1
        self.last_start = None
        self.running = False
        self.thread = None

    def start(self):
        self.driver.start_recording_screen()
        self.last_start = time.time()
        self.running = True

        self.thread = threading.Thread(
            target=self._watchdog,
            daemon=True
        )
        self.thread.start()

    def _watchdog(self):
        while self.running:
            time.sleep(self.check_interval)
            self.rotate_if_needed()

    def rotate_if_needed(self):
        elapsed = time.time() - self.last_start
        if elapsed >= self.max_seconds:
            self._stop_and_attach()
            self.driver.start_recording_screen()
            self.last_start = time.time()
            self.segment += 1

    def stop(self):
        self.running = False
        time.sleep(0.2)  # deja cerrar el hilo
        self._stop_and_attach()

    def _stop_and_attach(self):
        video = self.driver.stop_recording_screen()
        allure.attach(
            base64.b64decode(video),
            name=f"Video Evidencia Parte {self.segment}",
            attachment_type=allure.attachment_type.MP4
        )
