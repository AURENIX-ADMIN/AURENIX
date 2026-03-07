# 🚀 AURENIX Web: Manual de Despliegue y Traspaso

Este documento acompaña la carpeta `public-web` y contiene las directrices técnicas para levantar, modificar y desplegar la web pública oficial de AURENIX.

## 1. Estructura del Proyecto
El proyecto está construido usando **Next.js 15 (App Router)** + **React** + **Tailwind CSS**.
* **Directorio principal:** `_PROJECTS/WEB/public-web`

## 2. Requisitos Previos (Para el Socio)
* **Node.js**: Versión 18.17 o superior.
* **Gestor de paquetes**: Recomendamos `npm` (o `pnpm`/`yarn`).

## 3. Instrucciones de Desarrollo Local
Para levantar la web en tu propia máquina y ver los cambios en tiempo real:

1. Abre tu terminal (ej. Cursor o VSCode) y navega a la carpeta:
   ```bash
   cd ruta/hacia/_PROJECTS/WEB/public-web
   ```
2. Instala todas las dependencias:
   ```bash
   npm install
   ```
3. Ejecuta el servidor de desarrollo:
   ```bash
   npm run dev
   ```
4. Abre tu navegador en [http://localhost:3000](http://localhost:3000).

## 4. Estándares B2B AURENIX (Reglas de Edición)
Si vas a modificar textos o componentes, recuerda el ethos de AURENIX:
- **No hablamos de "Hacer flujos", hablamos de "Transformar Negocios".**
- El copy debe centrarse en el **ROI (Retorno de Inversión)**, reducción de costes operativos y la eliminación del error humano mediante agentes autónomos.
- Mantén la estética "Dark Mode" premium y los márgenes limpios de Tailwind.

## 5. Instrucciones de Despliegue a Producción (Coolify)
Cuando la web esté lista para salir al mundo real bajo el dominio de Aurenix:

1. Asegúrate de que los cambios estén puleados en la rama `main` de nuestro repositorio corporativo de GitHub.
2. Desde tu panel de **Coolify**, crea un nuevo recurso tipo "Application".
3. Vincula el repositorio de GitHub.
4. Configuraciones clave:
   - **Build Command:** `npm run build`
   - **Install Command:** `npm install`
   - **Start Command:** `npm run start`
   - **Base Directory:** `/` (o `/public-web` si despliegan desde un monorepo).
5. Asigna el dominio oficial y despliega.

---
*Producido por AURENIX IT Agent.*
