# xlavm-lib

Librería de Visual Testing y Get Elements Ids para Selenium y Appium.

## Instalación

```bash
pip install xlavm-lib
```

## Visual Testing

En cualquier parte donde se quiera realizar una prueba visual:

```bash
from xlavm_lib import VisualTest
VisualTest(self.driver, 'nombre_pagina').exec()
```

En conftest.py:

```bash
@pytest.fixture
def driver():

    driver.quit()
    from xlavm_lib import VisualTestReport
    VisualTestReport().exec()
```

## Get Ids

En cualquier parte donde se quiera obtener los elements ids de una pagina:

```bash
from xlavm_lib import GetIds
GetIds(self.driver, 'nombre_pagina').exec()
```
