import os
from jinja2 import Template

class VisualTestReport():
    """
    Genera el reporte html de las pruebas visuales hechas
    
    Responsabilidades:
    - Toma las imagenes generadas durante las pruebas visuales
    - Toma el template html y asocia los valores de las imagenes al template
    - Genera el reporte en formato html con nombre: visual_test.html
        
    Prerrequisitos:
        En el conftest.py dentro de la funcion driver() y despues del driver.quit(), se
        debe ubicar:
        
        from xlavm_lib import VisualTestReport
        VisualTestReport().exec()
        
    Uso:
        from xlavm_lib import VisualTest
        VisualTest(self.driver, 'nombre_pagina').exec()
    """
    
    # Directorio base de los screenshots
    base_dir = "ui"

    # Plantilla HTML para el reporte
    html_template = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visual Test Report</title>

    <style>
    /* ==========================
       GLOBAL
    ========================== */
    body {
        font-family: Arial, sans-serif;
        margin: 20px;
        background: #fafafa;
        line-height: 1.6;
    }
    h1 {
        text-align: center;
        margin-bottom: 10px;
    }
    table {
        width: 100%;
        border-collapse: collapse;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 10px;
        text-align: center;
    }
    th {
        background: #f4f4f4;
    }

    /* ==========================
       SUMMARY
    ========================== */
    .summary {
        display: flex;
        justify-content: center;
        gap: 16px;
        margin: 10px 0 20px;
        flex-wrap: wrap;
    }
    .summary-item {
        padding: 6px 14px;
        border-radius: 6px;
        font-weight: bold;
        background: #eee;
    }
    .summary-item.failed {
        background: #fdecea;
        color: #b00020;
    }
    .summary-item.passed {
        background: #e8f5e9;
        color: #1b5e20;
    }

    /* ==========================
       META INFO
    ========================== */
    .report-meta {
        display: flex;
        justify-content: center;
        gap: 14px;
        font-size: 13px;
        color: #666;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }

    /* ==========================
       ACCORDION
    ========================== */
    .accordion {
        margin-bottom: 12px;
    }
    .accordion-header {
        display: flex;
        justify-content: space-between;
        padding: 12px;
        cursor: pointer;
        border-radius: 6px;
        border: 1px solid #ccc;
        font-weight: bold;
        align-items: center;
    }
    .accordion-header.success {
        background: #f1f8f4;
        border-left: 6px solid #2e7d32;
        color: #2e7d32;
    }
    .accordion-header.failed {
        background: #fdecea;
        border-left: 6px solid #c62828;
        color: #c62828;
    }
    .accordion-arrow {
        transition: transform 0.3s ease;
    }
    .accordion-header.active .accordion-arrow {
        transform: rotate(180deg);
    }
    .accordion-content {
        display: none;
        background: white;
        padding: 15px;
        border: 1px solid #ddd;
        border-top: none;
    }

    /* ==========================
       IMAGES
    ========================== */
    .image-wrapper {
        position: relative;
    }
    .image-label {
        position: absolute;
        top: 8px;
        left: 8px;
        background: rgba(0,0,0,0.6);
        color: white;
        font-size: 12px;
        padding: 4px 8px;
        border-radius: 4px;
    }
    img {
        max-width: 100%;
        height: auto;
        cursor: pointer;
    }

    /* ==========================
       BADGES
    ========================== */
    .badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    .badge.success {
        background: #e8f5e9;
        color: #1b5e20;
    }
    .badge.error {
        background: #fdecea;
        color: #b00020;
    }

    /* ==========================
       LIGHTBOX
    ========================== */
    .lightbox {
        display: none;
        position: fixed;
        z-index: 999;
        inset: 0;
        background: rgba(0,0,0,0.85);
    }
    .lightbox img {
        margin: auto;
        display: block;
        max-width: 90%;
        max-height: 90%;
        transform-origin: center;
    }
    .close {
        position: absolute;
        top: 20px;
        right: 30px;
        color: white;
        font-size: 40px;
        cursor: pointer;
    }

    /* ==========================
       RESPONSIVE
    ========================== */
    @media (max-width: 768px) {
        th, td {
            padding: 5px;
        }
    }
    </style>
    </head>

    <body>

    <h1>Visual Test Report</h1>

    <div class="summary">
        <span class="summary-item">Total: {{ total_test_failed + total_test_passed }}</span>
        <span class="summary-item failed">Fallidas: {{ total_test_failed }}</span>
        <span class="summary-item passed">Exitosas: {{ total_test_passed }}</span>
    </div>

    <!-- ==========================
         FAILED TESTS
    ========================== -->
    {% for folder, images in report_data_failed.items() %}
    <div class="accordion">
        <div class="accordion-header failed">
            {{ folder }}
            <span class="accordion-arrow">▼</span>
        </div>
        <div class="accordion-content">
            <table>
                <thead>
                    <tr>
                        <th>Esperaba</th>
                        <th>Obtuvo</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>
                            <div class="image-wrapper">
                                <span class="image-label">Esperado</span>
                                <img src="../{{ images['ref'] }}" class="clickable-image">
                            </div>
                        </td>
                        <td>
                            <div class="image-wrapper">
                                <span class="image-label">Diff</span>
                                <img src="../{{ images['diff'] }}" class="clickable-image">
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
            <p class="badge error">❌ Prueba visual fallida </p>
        </div>
    </div>
    {% endfor %}

    <!-- ==========================
         PASSED TESTS
    ========================== -->
    {% for folder, images in report_data_passed.items() %}
    <div class="accordion">
        <div class="accordion-header success">
            {{ folder }}
            <span class="accordion-arrow">▼</span>
        </div>
        <div class="accordion-content">
            <table>
                <thead>
                    <tr>
                        <th>Esperaba</th>
                        <th>Obtuvo</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>
                            <div class="image-wrapper">
                                <span class="image-label">Esperado</span>
                                <img src="../{{ images['ref'] }}" class="clickable-image">
                            </div>
                        </td>
                        <td>
                            <div class="image-wrapper">
                                <span class="image-label">Obtuvo</span>
                                <img src="../{{ images['test'] }}" class="clickable-image">
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
            <p class="badge success">✔ Prueba visual exitosa</p>
        </div>
    </div>
    {% endfor %}

    <!-- ==========================
         LIGHTBOX
    ========================== -->
    <div id="lightbox" class="lightbox">
        <span class="close">&times;</span>
        <img id="lightbox-img">
    </div>

    <script>
    /* ==========================
       LIGHTBOX + ZOOM
    ========================== */
    const lightbox = document.getElementById("lightbox");
    const lightboxImg = document.getElementById("lightbox-img");
    const closeBtn = document.querySelector(".close");

    document.querySelectorAll(".clickable-image").forEach(img => {
        img.addEventListener("click", () => {
            lightbox.style.display = "block";
            lightboxImg.src = img.src;
            lightboxImg._scale = 1;
            lightboxImg.style.transform = "scale(1)";
        });
    });

    closeBtn.onclick = () => lightbox.style.display = "none";
    lightbox.onclick = e => { if (e.target === lightbox) lightbox.style.display = "none"; };

    lightboxImg.addEventListener("wheel", e => {
        e.preventDefault();
        const scale = e.deltaY < 0 ? 1.1 : 0.9;
        lightboxImg._scale *= scale;
        lightboxImg.style.transform = `scale(${lightboxImg._scale})`;
    });

    /* ==========================
       ACCORDION UX
    ========================== */
    document.querySelectorAll(".accordion-header").forEach(header => {
        header.addEventListener("click", () => {
            document.querySelectorAll(".accordion-content").forEach(c => {
                if (c !== header.nextElementSibling) c.style.display = "none";
            });
            document.querySelectorAll(".accordion-header").forEach(h => h.classList.remove("active"));

            const content = header.nextElementSibling;
            content.style.display = content.style.display === "block" ? "none" : "block";
            header.classList.toggle("active");
        });
    });
    </script>

    </body>
    </html>
    """
    total_test_failed = 0
    total_test_passed = 0
    # Función para buscar imágenes en carpetas con pruebas fallidas
    def collect_images_for_failed(self):
        report_data = {}
        for root, _, files in os.walk(self.base_dir):
            filtered_imgs = {file.split('.')[0]: os.path.join(root, file) for file in files if file.endswith(".png")}
            if "ref" in filtered_imgs and "test" in filtered_imgs and "diff" in filtered_imgs:
                folder_name = os.path.basename(root)
                if os.path.exists(f"{root}/error"):
                    with open(f"{root}/error", 'r') as error_file: # Leo el archivo con la descripcion del error
                        error_text = error_file.read()
                else:
                    error_text = ''
                report_data[folder_name] = {
                    "ref": filtered_imgs.get("ref"),
                    "test": filtered_imgs.get("test"),
                    "diff": filtered_imgs.get("diff"),
                    "error": error_text.replace('\n', '<br>')# Sacar el error con salto de linea en html
                }
                self.total_test_failed = self.total_test_failed + 1 
        return report_data
    
    # Función para buscar imágenes en carpetas con pruebas exitosas
    def collect_images_for_passed(self):
        report_data = {}
        for root, _, files in os.walk(self.base_dir):
            filtered_imgs = {file.split('.')[0]: os.path.join(root, file) for file in files if file.endswith(".png")}
            if "ref" in filtered_imgs and "test" in filtered_imgs and not "diff" in filtered_imgs: # no diff
                folder_name = os.path.basename(root)
                report_data[folder_name] = {
                    "ref": filtered_imgs.get("ref"),
                    "test": filtered_imgs.get("test"),
                }
                self.total_test_passed = self.total_test_passed + 1 
        return report_data

    # Generar el reporte
    def exec(self):
        output_file = "visual_test.html"
        report_data_failed = self.collect_images_for_failed()
        report_data_passed = self.collect_images_for_passed()        
        html_template = Template(self.html_template)
        rendered_html = html_template.render(report_data_failed=report_data_failed, report_data_passed=report_data_passed, total_test_failed=self.total_test_failed, total_test_passed=self.total_test_passed )
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(rendered_html)
        print(f"\nReporte del visual test generado")
