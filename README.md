# 🤖 LangGraph y Patrones de Diseño Agéntico

Este repositorio nace como una iniciativa educativa para la comunidad hispanohablante, con el objetivo de enseñar conceptos avanzados sobre LangGraph y arquitecturas multiagente a través de ejemplos prácticos y documentación en español.

## 🎯 Objetivo

La mayoría de la documentación y recursos sobre Patrones de Diseño Agéntico (Agentic Design Patterns) y LangGraph está disponible únicamente en inglés. Este proyecto busca:

1. Proporcionar ejemplos prácticos y documentados en español
2. Explicar los patrones de diseño fundamentales para agentes LLM
3. Demostrar implementaciones usando LangGraph
4. Servir como recurso de aprendizaje para la comunidad hispanohablante

## 🗂️ Estructura del Proyecto

### 📚 Core Patterns
Implementaciones de patrones de diseño fundamentales para agentes LLM:

- [`/core-patterns/tool-use`](./core-patterns/tool-use/): Patrón de uso de herramientas
  - Ejemplos prácticos con APIs del clima, ArXiv y calculadora
  - Documentación detallada del patrón
  - Guía de implementación

- `/core-patterns/reflection` (🚧 en progreso): Patrón de reflexión
  - Auto-evaluación y mejora de resultados
  - Ciclos de refinamiento
  
- `/core-patterns/planning` (🚧 en progreso): Patrón de planificación
  - Descomposición de tareas
  - Ejecución paso a paso
  
- `/core-patterns/multi-agent` (🚧 en progreso): Patrón multi-agente
  - Colaboración entre agentes especializados
  - Orquestación y coordinación

### 🛠️ Framework Demos
Ejemplos básicos de uso de frameworks:

- [`/framework-demos`](./framework-demos/): 
  - Comparación entre LangChain y LangGraph
  - Ejemplos síncronos y asíncronos
  - Patrones básicos de implementación

### 🔧 Tools
Herramientas reutilizables para los agentes:

- [`/tools`](./tools/):
  - Módulos independientes
  - Interfaces estandarizadas
  - Documentación de uso

## 📊 Comparación de Patrones

| Patrón | Fortaleza Principal | Mejor Para | Complejidad | Predictibilidad |
|---------|-------------|-----------|------------|----------------|
| Reflexión | Auto-mejora | Tareas de escritura/código | Baja | Alta |
| Tool Use | Capacidades externas | Investigación, datos | Media | Alta |
| Planning | Descomposición de tareas | Proyectos complejos | Alta | Media |
| Multi-Agent | Expertise especializado | Tareas grandes/diversas | Muy Alta | Baja |

## 🚀 Empezando

1. Clona el repositorio:
```bash
git clone https://github.com/A-PachecoT/agentic-patterns-es.git
cd agentic-patterns-es
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura las variables de entorno:
```bash
cp .env.example .env
# Edita .env con tus claves de API
```

4. Explora los ejemplos:
```bash
python core-patterns/tool-use/langchain_weather_demo.py
python core-patterns/tool-use/langchain_arxiv_research.py
```

## 📖 Documentación Adicional

- [Guía de Commits](./.cursorrules): Convenciones para contribuir al proyecto
- [Tool Use Pattern](./core-patterns/tool-use/README.md): Documentación detallada del patrón

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor, lee nuestra [guía de contribución](./CONTRIBUTING.md) antes de empezar.

## 📜 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo [LICENSE](./LICENSE) para más detalles.