# Guía de Sincronización al Drive Corporativo (Filebrowser)

Para trabajar como expertos y tener todo centralizado en el servidor (nuestro Drive en Filebrowser), debemos subir la carpeta actual `c:\Users\Usuario\Desktop\AURENIX` (que ya hemos limpiado y estructurado) al servidor.

## Método Recomendado: SFTP (FileZilla / WinSCP / Cursor)
Como ya tenemos acceso SSH al VPS (`76.13.9.238`) con el usuario `root` o `aurenix_it_agent`, la forma más segura y rápida de volcar gigabytes de información es usar SFTP.

### Paso 1: Localizar la carpeta destino en el VPS
Filebrowser está sirviendo un volumen montado. Según nuestros scripts anteriores, el volumen compartido de la agencia suele estar en:
`/data/agencia`  (o el path exacto que hayas configurado en Coolify para Filebrowser).

### Paso 2: Usar un Cliente SFTP (Ej. FileZilla)
1. Descarga y abre [FileZilla](https://filezilla-project.org/) o WinSCP.
2. **Servidor:** `sftp://76.13.9.238`
3. **Usuario:** `root`
4. **Contraseña/Clave:** Usa tu clave RSA o la contraseña del servidor.
5. **Puerto:** `22` (o el que uses para SSH).

### Paso 3: Arrastrar y Soltar
1. En el panel izquierdo (Local), navega hasta `c:\Users\Usuario\Desktop\AURENIX`.
2. En el panel derecho (Servidor), navega hasta `/data/agencia/` (la raíz de tu Filebrowser).
3. Arrastra las carpetas `_KNOWLEDGE_BASE`, `_INFRA`, `_PROJECTS` y `_CLIENTS` de izquierda a derecha.

*Ventaja:* Al subirlo por SFTP directamente a la carpeta montada, Filebrowser lo detectará instantáneamente en la interfaz web para ti y para tu socio.

---

## Método Alternativo: Interfaz Web de Filebrowser
Si la carpeta no pesa demasiados GBs y prefieres no usar SFTP:
1. Entra a la URL de tu Filebrowser corporativo con tu usuario administrador.
2. Crea una carpeta raíz llamada `AURENIX_AGUA_CERO` o similar.
3. Entra en ella, presiona el botón de subir (Upload) -> Subir Carpeta (Upload Directory).
4. Selecciona tu carpeta local `AURENIX`.
*(Nota: Este método puede fallar si intentas subir archivos individuales de más de 2GB dependiendo de la configuración del proxy de Filebrowser).*

> **Misión Táctica para hoy:** Enséñale a tu socio a conectarse al Filebrowser web (dale sus credenciales) y explícale que ese es el único lugar donde vivirán los documentos del cliente (`_CLIENTS`) y la base de conocimientos (`_KNOWLEDGE_BASE`) a partir de ahora. Nada de documentos sueltos en WhatsApp o en locales.
