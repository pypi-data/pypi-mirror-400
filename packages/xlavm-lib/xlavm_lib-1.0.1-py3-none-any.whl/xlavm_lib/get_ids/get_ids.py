from lxml import etree
import cv2
import random
import os
import time
import re
import glob
from pathlib import Path

class GetIds:
    """
    Obtiene los accessibility ids o xpath para los elementos de la pagina donde se instancie
    
    Responsabilidades:
    - Obtiene el html para web o el app_source para mobile (Android o Ios)
    - Usa el html o app_source para extraer los elementos y luego obtener su id o xpath
        
    Uso:
        from xlavm_lib import GetIds
        GetIds(self.driver, 'nombre_pagina').exec()
        
    Args:
        driver (driver): Driver web o mobile
        page_name (str): Nombre de pagina, modal, pantalla a escanear
    """

    def __init__(self, driver, page_name):
        self.driver = driver
        self.page_name = page_name
        self.ENABLE_GET_IDS = True
        self.ONLY_INTERACTABLE_ELEMENTS = True
        self.INITIAL_DELAY = 3
        self.BASE_FOLDER = "ids/base/"
        self.MARKED_FOLDER = "ids/marked/"
        self.CLASS_FOLDER = "ids/class/"

    # ==========================================================
    # MÉTODO PRINCIPAL
    # ==========================================================
    def exec(self):
        if not self.ENABLE_GET_IDS:
            return
        # verifico si es web o mobile
        if self.driver.platform in ["android", "ios"]:
            if self.driver.platform == "ios":
                self._map_ios(self.page_name)
            elif self.driver.platform == "android":
                self._map_android(self.page_name)
            self.generate_poms_from_marked_ids_for_mobile()
        else:
            self._map_web(self.page_name)
            self.generate_poms_from_marked_ids_for_web()
        
    # ==========================================================
    # PARSER
    # ==========================================================
    
    # ANDROID — INTERACTABLE
    def _is_interactable_android(self, node):
        cls = node.attrib.get("class", "").lower()
        clickable = node.attrib.get("clickable", "false") == "true"
        focusable = node.attrib.get("focusable", "false") == "true"
        long_clickable = node.attrib.get("long-clickable", "false") == "true"
        enabled = node.attrib.get("enabled", "false") == "true"
        has_identifier = (
            node.attrib.get("resource-id") or
            node.attrib.get("content-desc") or
            node.attrib.get("text")
        )
        INTERACTABLE_CLASSES = [
            "button",
            "edittext",
            "imageview",
            "checkbox",
            "radiobutton",
            "switch",
            "textview"
        ]
        if clickable or focusable or long_clickable:
            return True
        if enabled and has_identifier:
            return True
        return any(c in cls for c in INTERACTABLE_CLASSES)

    # ANDROID PARSER
    def _map_android(self, page_name):
        time.sleep(self.INITIAL_DELAY)
        os.makedirs(self.BASE_FOLDER, exist_ok=True)
        os.makedirs(self.MARKED_FOLDER, exist_ok=True)
        screenshot_file = f"{self.BASE_FOLDER}{page_name}.png"
        marked_file = f"{self.MARKED_FOLDER}{page_name}.png"
        txt_file = f"{self.MARKED_FOLDER}{page_name}.txt"
        self.driver.save_screenshot(screenshot_file)
        source = self.driver.page_source
        root = etree.fromstring(source.encode("utf-8"))
        raw_elements = []
        unique = set()
        EXCLUDED_CLASSES = [
            "android.view.ViewGroup",
            "ViewGroup",
            "androidx.compose.ui.platform.ComposeView"
        ]
        def build_xpath(node, index):
            cls = node.attrib.get("class") or node.tag
            text = node.attrib.get("text", "").strip()
            cd = node.attrib.get("content-desc", "").strip()
            rid = node.attrib.get("resource-id")
            if cd:
                return f"//*[@content-desc='{cd}']"
            if text:
                return f"//*[@text='{text}']"
            if rid:
                return f"//*[@resource-id='{rid}']"
            return f"(//{cls})[{index}]"
        def walk(node, index=1):
            node_class = node.attrib.get("class", "")
            rid = node.attrib.get("resource-id")
            cd = node.attrib.get("content-desc")
            text = node.attrib.get("text")
            if any(x in node_class for x in EXCLUDED_CLASSES) and not rid and not cd and not text:
                for i, c in enumerate(node):
                    walk(c, i + 1)
                return
            identifier = (
                f"accessibility_id:{cd}"
                if cd else
                f"xpath:{build_xpath(node, index)}"
            )
            bounds = node.attrib.get("bounds")
            if bounds:
                if not self.ONLY_INTERACTABLE_ELEMENTS or self._is_interactable_android(node):
                    raw_elements.append({
                        "identifier": identifier,
                        "bounds": bounds
                    })
            for i, c in enumerate(node):
                walk(c, i + 1)
        walk(root)
        final = []
        for el in raw_elements:
            if el["identifier"] not in unique:
                unique.add(el["identifier"])
                final.append(el)
        with open(txt_file, "w", encoding="utf-8") as f:
            for el in final:
                f.write(el["identifier"] + "\n")
        self._draw_elements_for_mobile(screenshot_file, marked_file, final)
        return final

    # iOS — INTERACTABLE
    def _is_interactable_ios(self, node):
        enabled = node.attrib.get("enabled", "").lower() == "true"
        accessible = node.attrib.get("accessible", "").lower() == "true"
        visible = node.attrib.get("visible", "").lower() == "true"
        node_type = node.attrib.get("type", "").lower()
        INTERACTABLE_TYPES = [
            "xcuiElementtypebutton",
            "xcuiElementtypetextfield",
            "xcuiElementtypesecuretextfield",
            "xcuiElementtypecell",
            "xcuiElementtypeswitch",
            "xcuiElementtypelink"
        ]
        if enabled or accessible:
            return True
        return node_type in INTERACTABLE_TYPES and visible

    # iOS PARSER
    def _map_ios(self, page_name):
        time.sleep(self.INITIAL_DELAY)
        os.makedirs(self.BASE_FOLDER, exist_ok=True)
        os.makedirs(self.MARKED_FOLDER, exist_ok=True)
        screenshot_file = f"{self.BASE_FOLDER}{page_name}.png"
        marked_file = f"{self.MARKED_FOLDER}{page_name}.png"
        txt_file = f"{self.MARKED_FOLDER}{page_name}.txt"
        self.driver.save_screenshot(screenshot_file)
        win = self.driver.get_window_size()
        img = cv2.imread(screenshot_file)
        h, w = img.shape[:2]
        ratio = ((w / win["width"]) + (h / win["height"])) / 2
        source = self.driver.page_source
        root = etree.fromstring(source.encode("utf-8"))
        raw_elements = []
        unique = set()
        def bounds(node):
            try:
                x = float(node.attrib.get("x", 0)) * ratio
                y = float(node.attrib.get("y", 0)) * ratio
                w = float(node.attrib.get("width", 0)) * ratio
                h = float(node.attrib.get("height", 0)) * ratio
                return f"[{int(x)},{int(y)}][{int(x+w)},{int(y+h)}]"
            except:
                return None
        def walk(node):
            name = node.attrib.get("name")
            label = node.attrib.get("label")
            value = node.attrib.get("value")
            if name:
                identifier = f"accessibility_id:{name}"
            elif label:
                identifier = f"label:{label}"
            elif value:
                identifier = f"value:{value}"
            else:
                identifier = f"xpath://{node.attrib.get('type','XCUIElementTypeOther')}"
            b = bounds(node)
            if b:
                if not self.ONLY_INTERACTABLE_ELEMENTS or self._is_interactable_ios(node):
                    raw_elements.append({
                        "identifier": identifier,
                        "bounds": b
                    })
            for c in node:
                walk(c)
        walk(root)
        final = []
        for el in raw_elements:
            if el["identifier"] not in unique:
                unique.add(el["identifier"])
                final.append(el)
        with open(txt_file, "w", encoding="utf-8") as f:
            for el in final:
                f.write(el["identifier"] + "\n")
        self._draw_elements_for_mobile(screenshot_file, marked_file, final)
        return final
    
    # WEB PARSER
    def _is_interactable_web(self, el):
        return el["visible"] and el["enabled"]

    def _map_web(self, page_name):
        time.sleep(self.INITIAL_DELAY)
        os.makedirs(self.BASE_FOLDER, exist_ok=True)
        os.makedirs(self.MARKED_FOLDER, exist_ok=True)
        screenshot = f"{self.BASE_FOLDER}{page_name}.png"
        marked = f"{self.MARKED_FOLDER}{page_name}.png"
        txt = f"{self.MARKED_FOLDER}{page_name}.txt"
        self.driver.save_screenshot(screenshot)
        script = """
        const MAX_TEXT = 30;
        const INTERACTABLE_TAGS = ['button','input','select','textarea','a'];

        return Array.from(document.querySelectorAll('*')).map(el => {
            const r = el.getBoundingClientRect();
            const text = (el.innerText || '').trim();

            return {
                tag: el.tagName.toLowerCase(),
                id: el.id || null,
                name: el.name || null,
                aria: el.getAttribute('aria-label'),
                placeholder: el.getAttribute('placeholder'),
                text:
                    INTERACTABLE_TAGS.includes(el.tagName.toLowerCase()) &&
                    text.length > 0 &&
                    text.length <= MAX_TEXT &&
                    !text.includes('\\n')
                    ? text
                    : null,
                x: r.x,
                y: r.y,
                w: r.width,
                h: r.height,
                visible: r.width > 0 && r.height > 0,
                enabled: !el.disabled
            };
        });
        """
        dom = self.driver.execute_script(script)
        elements = []
        unique = set()
        for el in dom:
            if el["w"] <= 0 or el["h"] <= 0:
                continue
            if self.ONLY_INTERACTABLE_ELEMENTS and not (el["visible"] and el["enabled"]):
                continue
            identifier = None
            # PRIORIDAD ABSOLUTA (ESTABLE)
            if el["id"]:
                identifier = f"css:#{el['id']}"
            elif el["name"]:
                identifier = f"css:[name='{el['name']}']"
            elif el["aria"]:
                identifier = f"xpath://*[@aria-label='{el['aria']}']"
            elif el["placeholder"]:
                identifier = f"xpath://*[@placeholder='{el['placeholder']}']"
            elif el["text"]:
                identifier = f"xpath://{el['tag']}[normalize-space(text())='{el['text']}']"
            if not identifier:
                continue
            if identifier in unique:
                continue
            unique.add(identifier)
            bounds = (
                f"[{int(el['x'])},{int(el['y'])}]"
                f"[{int(el['x']+el['w'])},{int(el['y']+el['h'])}]"
            )
            elements.append({
                "identifier": identifier,
                "bounds": bounds
            })
        with open(txt, "w", encoding="utf-8") as f:
            for e in elements:
                f.write(e["identifier"] + "\n")
        self._draw_elements_for_web(screenshot, marked, elements)
        return elements

    # ==========================================================
    # RENDER
    # ==========================================================
    def _draw_elements_for_mobile(self, screenshot_file, marked_file, elements):
        img = cv2.imread(screenshot_file)
        used = []
        def color():
            return random.randint(60,255), random.randint(60,255), random.randint(60,255)
        def overlap(x,y,w,h):
            for ux,uy,uw,uh in used:
                if not (x+w < ux or x > ux+uw or y+h < uy or y > uy+uh):
                    return True
            return False
        for i, el in enumerate(elements, start=1):
            coords = el["bounds"].replace("][", ",").replace("[","").replace("]","").split(",")
            x1,y1,x2,y2 = map(int, coords)
            c = color()
            cv2.rectangle(img, (x1,y1), (x2,y2), c, 2)
            text = f"{i}: {el['identifier'][:45]}"
            tw,th = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)[0]
            tx,ty = x1,y1-th-5
            if ty < 0:
                ty = y2 + th + 5
            while overlap(tx,ty,tw,th):
                ty += th + 5
            used.append((tx,ty,tw,th))
            cv2.rectangle(img, (tx-3,ty-th-4), (tx+tw+4,ty+4), c, -1)
            cv2.putText(img, text, (tx,ty), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255,255,255), 1)
        cv2.imwrite(marked_file, img)
        
    def _draw_elements_for_web(self, screenshot, marked, elements):
        img = cv2.imread(screenshot)
        used = []
        def color():
            return random.randint(60,255), random.randint(60,255), random.randint(60,255)
        for i, el in enumerate(elements, 1):
            x1,y1,x2,y2 = map(int, el["bounds"].replace("][",",").replace("[","").replace("]","").split(","))
            c = color()
            cv2.rectangle(img, (x1,y1), (x2,y2), c, 2)
            text = f"{i}: {el['identifier'][:45]}"
            cv2.putText(img, text, (x1, max(15,y1-5)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, c, 1)
        cv2.imwrite(marked, img)

    # ==========================================================
    # GENERAR POMs
    # ==========================================================
    
    # GENERAR POMs Mobile
    def generate_poms_from_marked_ids_for_mobile(self):
        output_folder = self.CLASS_FOLDER
        os.makedirs(output_folder, exist_ok=True)
        INPUT_KEYWORDS = [
            "edittext",
            "textfield",
            "securetextfield",
            "xcuiElementtypetextfield",
            "xcuiElementtypesecuretextfield"
        ]
        def is_input(value):
            value = value.lower()
            return any(k in value for k in INPUT_KEYWORDS)
        def sanitize(text):
            text = text.lower()
            text = re.sub(r"[¿?¡!]", "", text)
            text = re.sub(r"[^a-z0-9]+", "_", text)
            return text.strip("_")
        def to_class(name):
            return "".join(x.capitalize() for x in name.split("_")) + "Page"
        for txt in glob.glob(f"{self.MARKED_FOLDER}*.txt"):
            page_key = Path(txt).stem
            class_name = to_class(page_key)
            output = f"{output_folder}{page_key}_page.py"
            locators = []
            with open(txt, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip()]
            for line in lines:
                if line.startswith("xpath:"):
                    val = line.replace("xpath:", "")
                    name = "element"
                    if "@text='" in val:
                        m = re.search(r"@text='([^']+)'", val)
                        if m:
                            name = sanitize(m.group(1))
                    locators.append({
                        "name": name.upper(),
                        "by": "XPATH",
                        "value": val,
                        "is_input": is_input(val)
                    })
                elif line.startswith("accessibility_id:"):
                    val = line.replace("accessibility_id:", "")
                    locators.append({
                        "name": sanitize(val).upper(),
                        "by": "ACCESSIBILITY_ID",
                        "value": val,
                        "is_input": False
                    })
            with open(output, "w", encoding="utf-8") as f:
                f.write("from appium.webdriver.common.appiumby import AppiumBy\n")
                f.write("from utils.actions_util import Actions\n\n\n")
                f.write(f"class {class_name}(Actions):\n\n")
                f.write("    def __init__(self, driver):\n")
                f.write(f"        super().__init__(driver, \"{page_key.capitalize()}\")\n\n")
                for loc in locators:
                    f.write(
                        f"    {loc['name']} = "
                        f"(AppiumBy.{loc['by']}, \"{loc['value']}\")\n"
                    )
                f.write("\n")
                for loc in locators:
                    n = loc["name"].lower()
                    f.write(f"    def click_{n}(self):\n")
                    f.write(f"        self.do_click(self.{loc['name']}, '{n}')\n\n")
                    if loc["is_input"]:
                        f.write(f"    def set_{n}(self, text):\n")
                        f.write(f"        self.set_text(self.{loc['name']}, text, '{n}')\n\n")
                    f.write(f"    def get_{n}(self):\n")
                    f.write(f"        return self.get_text(self.{loc['name']}, '{n}')\n\n")
                    f.write(f"    def assert_{n}_is_visible(self):\n")
                    f.write(
                        f"        self.assert_that_have_element(self.{loc['name']}, '{n}')\n\n"
                    )
            print(f"POM Mobile Generado: {output}")

    # GENERAR POMs Mobile
    def generate_poms_from_marked_ids_for_web(self):
        output_folder = self.CLASS_FOLDER
        os.makedirs(output_folder, exist_ok=True)
        INPUT_KEYWORDS = [
            "input",
            "textarea",
            "password"
        ]
        def is_input(value):
            value = value.lower()
            return any(k in value for k in INPUT_KEYWORDS)
        def sanitize(text):
            text = text.lower()
            text = re.sub(r"[¿?¡!]", "", text)
            text = re.sub(r"[^a-z0-9]+", "_", text)
            return text.strip("_")
        def to_class(name):
            return "".join(x.capitalize() for x in name.split("_")) + "Page"
        for txt in glob.glob(f"{self.MARKED_FOLDER}*.txt"):
            page_key = Path(txt).stem
            class_name = to_class(page_key)
            output = f"{output_folder}{page_key}_page.py"
            locators = []
            with open(txt, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip()]
            for line in lines:
                if line.startswith("css:"):
                    val = line.replace("css:", "")
                    name = sanitize(val.split("#")[-1] or "element")
                    locators.append({
                        "name": name.upper(),
                        "by": "CSS_SELECTOR",
                        "value": val,
                        "is_input": is_input(val)
                    })
                elif line.startswith("xpath:"):
                    val = line.replace("xpath:", "")
                    name = "element"
                    if "text()" in val:
                        m = re.search(r"text\(\)\s*=\s*'([^']+)'", val)
                        if m:
                            name = sanitize(m.group(1))
                    locators.append({
                        "name": name.upper(),
                        "by": "XPATH",
                        "value": val,
                        "is_input": is_input(val)
                    })
            with open(output, "w", encoding="utf-8") as f:
                f.write("from selenium.webdriver.common.by import By\n")
                f.write("from utils.actions_util import Actions\n\n\n")
                f.write(f"class {class_name}(Actions):\n\n")
                f.write("    def __init__(self, driver):\n")
                f.write(f"        super().__init__(driver, \"{page_key.capitalize()}\")\n\n")
                # ===== LOCATORS =====
                for loc in locators:
                    f.write(
                        f"    {loc['name']} = "
                        f"(By.{loc['by']}, \"{loc['value']}\")\n"
                    )
                f.write("\n")
                # ===== METHODS =====
                for loc in locators:
                    n = loc["name"].lower()
                    f.write(f"    def click_{n}(self):\n")
                    f.write(f"        self.do_click(self.{loc['name']}, '{n}')\n\n")
                    if loc["is_input"]:
                        f.write(f"    def set_{n}(self, text):\n")
                        f.write(f"        self.set_text(self.{loc['name']}, text, '{n}')\n\n")
                    f.write(f"    def get_{n}(self):\n")
                    f.write(f"        return self.get_text(self.{loc['name']}, '{n}')\n\n")
                    f.write(f"    def assert_{n}_is_visible(self):\n")
                    f.write(
                        f"        self.assert_that_have_element(self.{loc['name']}, '{n}')\n\n"
                    )
            print(f"POM WEB Generado: {output}")
