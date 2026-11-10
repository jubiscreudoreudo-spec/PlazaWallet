# Plaza Wallet

Panel local en Python para el dinero de **MILF's Plaza**, con interfaz oscura, recarga automática y selección de idioma al abrir.

[English](README.md) · [Português](LEIA-ME.md)

## Idiomas

Elige **Português (Brasil)**, **English** o **Español** al abrir. Tu última elección aparece seleccionada. Usa **Idioma** en la barra lateral para cambiar sin reiniciar el juego. Los botones, instrucciones, estados, errores de la aplicación y números siguen el idioma elegido. Los diálogos nativos de archivos y los detalles de errores del sistema siguen el idioma de Windows. Se traduce el panel, no el juego.

## Instalación y uso

La versión **EXE para Windows no necesita Python instalado**. Extrae el ZIP Windows y abre **PlazaWallet.exe**. El conector y las traducciones están incluidos. Guarda el EXE en una carpeta con permiso de escritura para recordar preferencias.

Para ejecutar el código fuente necesitas Windows y **Python 3.10+ con Tkinter**, sin paquetes pip adicionales. Ambas versiones requieren una instalación Ren'Py que permita scripts `.rpy` adicionales.

1. Extrae la descarga. Abre **PlazaWallet.exe**, o **Start.bat** / **Iniciar.bat** si usas el código fuente.
2. Elige el idioma y pulsa **Continuar**.
3. Pulsa **Elegir carpeta** y selecciona la instalación con `game` y `renpy`.
4. Con el juego cerrado, pulsa **Instalar conector**.
5. Abre el juego, carga una partida y pulsa **Leer juego** en el panel.
6. `money` se selecciona automáticamente. Elige el saldo mínimo y pulsa **Activar recarga ∞**. Espera la confirmación del juego.

El valor predeterminado es **3.000**, porque la versión **18b22** reduce los saldos mayores a ese límite. El conector repone el mínimo después de bloques Python y durante las interacciones, además de comprobarlo periódicamente. La activación y el saldo se verificaron en una partida real de 18b22, Ren'Py 8.3.7. La recarga tras gastar se cubre con pruebas de motor simulado. No se han verificado otras versiones.

## Preferencias y eliminación

El idioma, la carpeta y el saldo se guardan en **settings.local.json**, junto a la aplicación. Git ignora este archivo. `settings.example.json` muestra el formato; no necesitas editarlo. La carpeta debe permitir escritura para recordar preferencias. Si es de solo lectura, el panel funciona pero informa del error al guardarlas.

**Desactivar** detiene la recarga y mantiene el saldo. Cerrar solo el panel mantiene la recarga hasta cerrar el juego. Al reiniciar el juego, la recarga empieza desactivada.

El panel no modifica partidas guardadas directamente. Las partidas guardadas por el juego después de activar pueden contener el dinero cambiado; carga una partida anterior para recuperar el valor previo. Para eliminar el conector, cierra el juego y pulsa **Eliminar**. Sus archivos se mueven a `plaza_wallet_backups`, fuera de `game`. No se sustituyen los scripts originales.

## Solución de problemas

- Sin conexión: comprueba la carpeta, instala el conector y reinicia el juego por completo.
- Sin saldo: carga una partida y pulsa **Leer juego**. Solo aparece `money`.
- Error de escritura: el conector necesita permiso para escribir en `game/plaza_wallet`.
- Error al abrir tras instalar: cierra el juego y usa **Eliminar**, o mueve `zz_plaza_wallet.rpy` y `zz_plaza_wallet.rpyc` fuera de `game`.
- Actualizar el conector requiere reiniciar el juego. Para actualizar solo las traducciones, basta con reabrir el panel.

## Desarrollo y GitHub

Ejecuta `python plaza_wallet.py` para abrir. Desde la carpeta del proyecto, ejecuta `python -m unittest discover -v` para las pruebas. Las pruebas de interfaz necesitan una sesión gráfica con Tkinter.

Las traducciones están en **i18n.py**. `ROWS` contiene el original portugués y sus traducciones al inglés y español. Conserva `{path}`, `{count}` y `{detail}`. Las pruebas comprueban traducciones, formato, preferencias, cambio de idioma, estados y el conector.

Publica los archivos del ZIP limpio. No incluyas `settings.local.json`, archivos del juego, partidas, registros, `.rpyc` generados ni copias de seguridad. El `.gitignore` excluye esos archivos locales. No se incluyen recursos del juego.

Ejecuta `python build_release.py` para generar `dist/PlazaWallet.zip` con una lista explícita de archivos. Las preferencias personales y los archivos generados se excluyen automáticamente.

### Generar el EXE

En Windows con Python instalado, ejecuta `python -m pip install -r requirements-build.txt` y después `python build_exe.py`. El resultado es `dist/PlazaWallet.exe`. El conector está integrado; las preferencias personales y los archivos del juego quedan fuera del EXE. Git ignora las carpetas de compilación.

Ejecuta `PlazaWallet.exe --self-test report.json` para comprobar los idiomas, las preferencias y la instalación del conector en una carpeta temporal aislada, sin acceder al juego real.
