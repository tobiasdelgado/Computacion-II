# Trabajo Práctico 1 - Blockchain

¡Hola profe! Aquí está el trabajo práctico número uno.

![Pizza Time](assets/pizza-time.webp)

## Características del Proyecto

### Cambios realizados
- **Nomenclatura en inglés**: Se modificaron los nombres de los keys de los diccionarios para mantener todo el proyecto en inglés.
- **Arquitectura modular por entidades**: El proyecto está organizado en módulos independientes basados en entidades.

### Estructura del Proyecto
- **Generador, Analizador y Verificador**: Cada uno es un módulo independiente con sus funciones dentro del `main` de cada módulo.
- **Definición de procesos**: Los procesos específicos están definidos en el archivo `process` de cada módulo.
- **Funciones generales**: Se encuentran en el módulo `common` (generación de data, encriptación, etc.).

## Cómo Ejecutar

### Ejecutar la aplicación principal
```bash
python main.py
```
- Cada ejecución limpiará la blockchain automáticamente, así que no hay problema en ejecutarlo múltiples veces.

### Verificar la blockchain
```bash
python verify_chain.py
```

## Personalización

Si desea generar bloques de data con alertas, puede modificar los valores aleatorios de las funciones dentro del módulo `generator`.