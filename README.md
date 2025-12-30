# Descargador Multimedia Local

Este proyecto está diseñado para **descargar contenido multimedia de forma rápida y organizada** directamente en tu servidor local.  
Permite gestionar descargas personalizadas, asignar nombre y categoría a los archivos, y cuenta con funcionalidades específicas para **anime y series**.  

---

## Características principales

- **Descarga de videos genéricos**  
  - Ingresa el link de descarga.  
  - Define el nombre del video.  
  - Asigna una categoría para mantener todo organizado.  

- **Descarga de Anime (AnimeFLV)**  
  - Sección dedicada para obtener episodios desde la página [AnimeFLV](https://www3.animeflv.net/).  
  - Descarga rápida y directa de capítulos.  

- **Descarga de Series mediante JSON**  
  - Proporciona un archivo JSON con los links de cada episodio.  
  - El sistema procesa automáticamente el listado y descarga todos los capítulos.  

- **Interfaz gráfica con Gradio**  
  - Interacción sencilla y amigable.  
  - Permite gestionar las descargas sin necesidad de usar la terminal.  

---

## Tecnologías utilizadas

- **Python** → Lenguaje principal del proyecto.  
- **Gradio** → Para la interfaz gráfica web.  
- **Requests** → Manejo de descargas HTTP.  
- **JSON** → Formato para definir listas de episodios de series.  
