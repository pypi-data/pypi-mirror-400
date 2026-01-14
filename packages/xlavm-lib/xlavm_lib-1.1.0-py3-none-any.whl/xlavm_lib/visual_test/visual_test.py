from PIL import Image, ImageChops  # type: ignore
import easyocr  # type: ignore
import cv2  # type: ignore
import os
import numpy as np
import time

class VisualTest:
    """
    Realiza pruebas visuales donde se instancie
    
    Responsabilidades:
    - Toma imagen de referencia si no existe en ui/
    - Compara la imagen de referencia con la imagen del test
    - Concluye si hay cambios o no y se genera un reporte con las diferencias
        
    Prerrequisitos:
        En el conftest.py dentro de la funcion driver() y despues del driver.quit(), se
        debe ubicar:
        
        from xlavm_lib import VisualTestReport
        VisualTestReport().exec()
        
    Uso:
        from xlavm_lib import VisualTest
        VisualTest(self.driver, 'nombre_pagina').exec()
        
    Args:
        driver (driver): Driver web o mobile
        page_name (str): Nombre de pagina, modal, pantalla a testear
    """
    
    def __init__(self, driver, page_name):
        self.driver = driver
        self.page= page_name
        #variables de entorno
        self.compare_ui = True
        self.compare_ui_and_texts = False
        self.base_img_path = "ui/"
        self.INITIAL_DELAY = 1
        #screenshots estandarizados
        if self.is_mobile(self.driver):
            #mobile
            self.STANDARD_WIDTH = 390
            self.STANDARD_HEIGHT = 844
        else:
            #web
            self.STANDARD_WIDTH = 1920
            self.STANDARD_HEIGHT = 1080
        
    def exec(self):
        time.sleep(self.INITIAL_DELAY)
        base_path = f'{self.base_img_path}{self.page}'
        # Limpia test.png, diff.png, error, etc.
        self.clean_base_path_except_ref(base_path)
        if self.compare_ui:
            self.compare_images_with_threshold(
                f'{base_path}/ref.png',
                f'{base_path}/test.png',
                f'{base_path}/diff.png',
                base_path
            )
        if self.compare_ui_and_texts:
            self.compare_images_and_texts(
                f'{base_path}/ref.png',
                f'{base_path}/test.png',
                f'{base_path}/diff.png',
                base_path
            )

    def is_not_reference_image(self, reference_path, test_path, diff_path):
        os.makedirs(os.path.dirname(reference_path), exist_ok=True)
        os.makedirs(os.path.dirname(test_path), exist_ok=True)
        os.makedirs(os.path.dirname(diff_path), exist_ok=True)
        if not os.path.isfile(reference_path):
            self.take_standard_screenshot(reference_path)
            self.take_standard_screenshot(test_path)
            return True
        else:
            self.take_standard_screenshot(test_path)
            return False

    def compare_images_with_threshold(self, reference_path, test_path, diff_path, base_path):
        if self.is_not_reference_image(reference_path, test_path, diff_path):
            print("VisualTest OK: Prueba UI no necesaria porque no hay imagen de referencia \n Imagen de Referencia Creada con Exito!")
        else:
            # Mantengo el nombre de la variable
            difference_threshold = 5  # se mantiene, pero ya NO será la única regla
            # nueva regla (sin cambiar nombres de funciones): cambios pequeños
            min_contour_area = 10  # detecta cambios mínimos como un dígito
            min_changed_pixels = 1  # por si el contorno es ultra pequeño
            # Cargar las imágenes
            ref_image = cv2.imread(reference_path)
            test_image = cv2.imread(test_path)
            # Verificar que las imágenes tengan el mismo tamaño
            if ref_image is None or test_image is None:
                print("VisualTest BUG: No se pudieron leer las imágenes (ref_image/test_image es None).")
            if ref_image.shape != test_image.shape:
                print("VisualTest BUG: Las imágenes deben tener el mismo tamaño para ser comparadas.")
            # Convertir a escala de grises
            gray_ref = cv2.cvtColor(ref_image, cv2.COLOR_BGR2GRAY)
            gray_test = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
            # Calcular la diferencia absoluta
            diff = cv2.absdiff(gray_ref, gray_test)
            # Umbral más sensible (25 es ideal para cambios pequeños de texto)
            _, diff_thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            # Reducir ruido pero mantener dígitos
            kernel = np.ones((2, 2), np.uint8)
            diff_thresh = cv2.morphologyEx(diff_thresh, cv2.MORPH_OPEN, kernel, iterations=1)
            diff_thresh = cv2.dilate(diff_thresh, kernel, iterations=1)
            # Calcular el porcentaje de diferencia (se imprime, pero NO define solo el fallo)
            total_pixels = diff_thresh.size
            differing_pixels = np.count_nonzero(diff_thresh)
            difference_ratio = (differing_pixels / total_pixels) * 100
            print(f"VisualTest Diferencia detectada: {difference_ratio:.6f}%  (pixeles distintos: {differing_pixels})")
            # REGLA REAL: contornos con área mínima (detecta “Password12” -> “Password123”)
            contours, _ = cv2.findContours(diff_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contour_areas = [cv2.contourArea(c) for c in contours] if contours else []
            max_area = max(contour_areas) if contour_areas else 0
            # Condición final: o supera threshold global (para cambios grandes) O hay un contorno real (cambios pequeños)
            has_significant_change = (difference_ratio >= float(difference_threshold)) or (max_area >= min_contour_area) or (differing_pixels >= min_changed_pixels and max_area > 0)
            if has_significant_change:
                # Dibujar las diferencias sobre la imagen de prueba
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    # ignora micro-ruido extremo si lo hubiera
                    if cv2.contourArea(contour) < 2:
                        continue
                    cv2.rectangle(test_image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                diff_image = Image.fromarray(cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB))
                os.makedirs(os.path.dirname(diff_path), exist_ok=True)
                diff_image.save(diff_path)
                print(
                    "VisualTest BUG:"
                    f"Diferencias detectadas (cambio pequeño incluido). "
                    f"ratio={difference_ratio:.6f}% | max_contour_area={max_area:.2f} | diff_path={diff_path}"
                )
            else:
                print("VisualTest OK: No se detectaron diferencias significativas.")

    # OCR
    def compare_texts(self, reference_path, test_path, diff_path, base_path):
        if self.is_not_reference_image(reference_path, test_path, diff_path):
            print("VisualTest OK: Prueba UI no necesaria porque no hay imagen de referencia \n Imagen de Referencia Creada con Exito!")
        else:
            # Idioma correcto para ingles y baja confianza para dígitos
            reader = easyocr.Reader(["en"], gpu=False)
            reference_text = []
            test_text = []
            # Pre-procesado simple para OCR (mejora dígitos)
            def _prep_for_ocr(p):
                img = cv2.imread(p)
                if img is None:
                    return None
                g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                g = cv2.resize(g, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                _, g = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                return g
            ref_img = _prep_for_ocr(reference_path)
            tst_img = _prep_for_ocr(test_path)
            if ref_img is None or tst_img is None:
                print("VisualTest BUG: No se pudieron preparar imágenes para OCR.")
            # saco los textos de las imagenes (usando arrays preprocesados)
            reference_result = reader.readtext(ref_img)
            test_result = reader.readtext(tst_img)
            # recorro la imagen de referencia para almacenar el texto
            for bbox, text, prob in reference_result:
                if prob > 0.2:  # baja el umbral para números
                    reference_text.append(str(text).strip())
            # recorro la imagen de prueba para verificar si los textos coinciden
            for bbox, text, prob in test_result:
                if prob > 0.2:
                    test_text.append(str(text).strip())
            # Normalización ligera para comparar (sin cambiar nombres de variables)
            reference_text_norm = [t.lower().replace(" ", "") for t in reference_text]
            test_text_norm = [t.lower().replace(" ", "") for t in test_text]
            solo_en_reference = set(reference_text_norm) - set(test_text_norm)
            solo_en_test = set(test_text_norm) - set(reference_text_norm)
            if not solo_en_reference and not solo_en_test:
                return True, "No hay diferencias de textos"
            file_name = f"{base_path}/error"
            with open(file_name, "w") as file:
                file.write(
                    f"Falló porque hubo un cambio en la UI.\n"
                    f"Faltó estos textos en la prueba:\n{solo_en_reference}\n\n"
                    f"Estos textos NO se esperaban:\n{solo_en_test}\n"
                )
            print(
                "VisualTest BUG:"
                f"Falló porque hubo un cambio en la UI.\n"
                f"Faltó estos textos en la prueba:\n{solo_en_reference}\n"
                f"Estos textos NO se esperaban:\n{solo_en_test}"
            )

    def compare_images_and_texts(self, reference_path, test_path, diff_path, base_path):
        if self.is_not_reference_image(reference_path, test_path, diff_path):
            print("VisualTest OK: Prueba UI no necesaria porque no hay imagen de referencia \n Imagen de Referencia Creada con Exito!")
        else:
            # VALIDACION DE IMAGENES
            reference = Image.open(reference_path).convert("RGB")
            test = Image.open(test_path).convert("RGB")
            diff = ImageChops.difference(reference, test)
            image_has_diff = (diff.getbbox() is not None)
            # Si hay diff visual, genero diff.png (como ya lo hacías)
            if image_has_diff:
                imageRef = cv2.imread(reference_path)
                imageTest = cv2.imread(test_path)
                grayRef = cv2.cvtColor(imageRef, cv2.COLOR_BGR2GRAY)
                grayTest = cv2.cvtColor(imageTest, cv2.COLOR_BGR2GRAY)
                diff_cv = cv2.absdiff(grayRef, grayTest)
                _, thresh = cv2.threshold(diff_cv, 25, 255, cv2.THRESH_BINARY)
                kernel = np.ones((2, 2), np.uint8)
                thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
                thresh = cv2.dilate(thresh, kernel, iterations=1)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                # detecta cambios pequeños por área
                min_contour_area = 10
                max_area = 0
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > max_area:
                        max_area = area
                    if area < 2:
                        continue
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(imageTest, (x, y), (x + w, y + h), (0, 0, 255), 2)
                diff_image = Image.fromarray(cv2.cvtColor(imageTest, cv2.COLOR_BGR2RGB))
                os.makedirs(os.path.dirname(diff_path), exist_ok=True)
                diff_image.save(diff_path)
            # VALIDACION DE TEXTOS
            reader = easyocr.Reader(["en"], gpu=False)
            # preprocesado OCR
            def _prep_for_ocr(p):
                img = cv2.imread(p)
                if img is None:
                    return None
                g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                g = cv2.resize(g, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
                _, g = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                return g
            ref_img = _prep_for_ocr(reference_path)
            tst_img = _prep_for_ocr(test_path)
            reference_text = []
            if ref_img is not None:
                reference_result = reader.readtext(ref_img)
                for bbox, text, prob in reference_result:
                    if prob > 0.2:
                        reference_text.append(str(text).strip().lower().replace(" ", ""))
            test_result = []
            if tst_img is not None:
                test_result = reader.readtext(tst_img)
            diff_text = []
            test_text_norm = []
            for bbox, text, prob in test_result:
                if prob > 0.2:
                    test_text_norm.append(str(text).strip().lower().replace(" ", ""))
            solo_en_reference = set(reference_text) - set(test_text_norm)
            solo_en_test = set(test_text_norm) - set(reference_text)
            if solo_en_reference or solo_en_test:
                diff_text.append(f"Faltan: {solo_en_reference}")
                diff_text.append(f"Sobran: {solo_en_test}")

            # Falla si hay cambio visual O cambio de textos
            if image_has_diff or diff_text:
                file_name = f"{base_path}/error"
                with open(file_name, "w") as file:
                    file.write(
                        f"Falló porque hubo un cambio en la UI.\n"
                        f"Revisar: {diff_path}\n"
                        f"Diferencias en Textos:\n{diff_text}\n"
                    )
                print(
                    f"Falló porque hubo un cambio en la UI"
                    f"Revisar: {diff_path}"
                    f"Diferencias en Textos:\n{diff_text}"
                    )
            print("VisualTest OK: Sin cambios")

    def compare_texts_excluding_words(self, reference_path, test_path, diff_path, base_path, arrayWords):
        if self.is_not_reference_image(reference_path, test_path, diff_path):
            print("VisualTest OK: Prueba UI no necesaria porque no hay imagen de referencia \n Imagen de Referencia Creada con Exito!")
        else:
            reader = easyocr.Reader(["en"], gpu=False)
            reference_result = reader.readtext(reference_path)
            reference_text = []
            for bbox, text, prob in reference_result:
                if prob > 0.2:
                    reference_text.append(str(text).lower().replace(" ", ""))
            test_result = reader.readtext(test_path)
            diff_text = []
            excluded_norm = [str(word).lower().replace(" ", "") for word in arrayWords]
            test_text = []
            for bbox, text, prob in test_result:
                if prob > 0.2:
                    test_text.append(str(text).lower().replace(" ", ""))
            for ref in reference_text:
                if ref not in test_text and ref not in excluded_norm:
                    diff_text.append(f"Falta texto esperado: '{ref}'")
            for t in test_text:
                if t not in reference_text and t not in excluded_norm:
                    diff_text.append(f"Texto inesperado: '{t}'")
            if diff_text:
                print(
                    f"Fallo porque hubo un cambio en el texto"
                    f"Diferencias en Textos:\n{diff_text}"
                )
            print("VisualTest OK")

    def clean_base_path_except_ref(self, base_path):
        """
        Elimina todos los archivos dentro de base_path excepto ref.png
        """
        if not os.path.exists(base_path):
            return
        for file_name in os.listdir(base_path):
            file_path = os.path.join(base_path, file_name)
            # No tocar la imagen de referencia
            if file_name.lower() == "ref.png":
                continue
            # Eliminar solo archivos
            if os.path.isfile(file_path):
                os.remove(file_path)
        time.sleep(1)
    
    def take_standard_screenshot(self, path: str):
        """
        Screenshot estándar para visual testing:
        - Mobile: SOLO contenido real de la app (sin status / nav bar)
        - Web: screenshot completo normal
        """
        #MOBILE
        if self.is_mobile(self.driver):
            platform = self.driver.capabilities.get("platformName", "").lower()
            # ANDROID → viewport real de la app
            if platform == "android":
                root = self.driver.find_element(
                    by="id",
                value="android:id/content"
                )
            # IOS → ventana principal de la app
            elif platform == "ios":
                root = self.driver.find_element(
                    by="xpath",
                value="//XCUIElementTypeWindow[1]"
                )
            else:
                raise Exception("Plataforma mobile no soportada")
            png = root.screenshot_as_png

        # WEB
        else:
            png = self.driver.get_screenshot_as_png()
        # CONVERSIÓN + NORMALIZACIÓN
        img_array = np.frombuffer(png, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if img is None:
            raise Exception("No se pudo convertir el screenshot")
        img_resized = cv2.resize(
            img,
            (self.STANDARD_WIDTH, self.STANDARD_HEIGHT),
            interpolation=cv2.INTER_AREA
        )
        # GUARDAR
        os.makedirs(os.path.dirname(path), exist_ok=True)
        cv2.imwrite(path, img_resized)
        
    def is_mobile(self, driver) -> bool:
        try:
            caps = driver.capabilities
            return caps.get("platformName", "").lower() in ["android", "ios"]
        except:
            return False
