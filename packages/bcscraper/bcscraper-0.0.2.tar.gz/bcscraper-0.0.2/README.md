# BCScraper

**BCScraper** es un scraper ligero y fácil de usar que permite obtener información de cursos desde [buscacursos.uc.cl](https://buscacursos.uc.cl) sin necesidad de proxies.  
Ideal para estudiantes, desarrolladores o cualquier persona que necesite automatizar la extracción de datos de los cursos UC.

## Características

- Obtiene información completa de los cursos: NRC, sigla, nombre, profesor(es), campus, créditos, vacantes y horarios.
- Permite buscar cursos por:
  - Sigla
  - Nombre
  - Profesor
  - NRC específico
- Obtiene automáticamente los períodos disponibles.
- No requiere proxies ni autenticación.

## Instalación

> [!IMPORTANT]
> **Se requiere Python 3 o superior**

```bash
# Linux/macOS
python3 -m pip install -U bcscraper

# Windows
py -3 -m pip install -U bcscraper
```

## Ejemplos rápidos

### Obtener los períodos disponibles

```python
periodos = obtener_periodos()
```

### Buscar curso por sigla

```python
curso = buscar_por_sigla("2026-1", "MAT1610")
```

### Buscar curso por profesor

```python
curso = buscar_por_profesor("2026-1", "Nombre Apellido")
```

### Buscar curso por nombre

```python
curso = buscar_por_nombre("2026-1", "Cálculo I")
```

### Buscar curso por NRC

```python
curso = buscar_por_nrc("2026-1", "12345")
```

### Buscar curso por sigla, NRC, nombre y profesor.

```python
curso = buscar_curso("2026-1", "MAT1610", "12345", "Cálculo I", "Nombre Apellido")
```

## Licencia

Este proyecto es de código abierto y está licenciado bajo la licencia MIT.
