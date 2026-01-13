"""Módulo principal de BCScraper"""
from typing import List, Optional

from bs4 import BeautifulSoup
from .classes import Curso, Modulo
from .utils import fetch_html, URL


def obtener_cursos(url: str) -> List[Curso]:
    """Obtiene una lista de cursos desde una URL de Buscacursos."""
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")

    cursos = []
    filas = soup.select(".resultadosRowPar") + soup.select(
        ".resultadosRowImpar"
    )

    for fila in filas:
        columnas = fila.find_all("td")
        if len(columnas) < 17:
            continue

        nrc = columnas[0].text.strip()
        sigla = columnas[1].text.strip()
        retirable = columnas[2].text.strip() == "SI"
        ingles = columnas[3].text.strip() == "SI"
        seccion = int(columnas[4].text.strip())
        aprobacion_especial = columnas[5].text.strip() == "SI"
        area = columnas[6].text.strip()
        formato = columnas[7].text.strip()
        categoria = columnas[8].text.strip()
        nombre = columnas[9].text.strip()
        profesor = [p.strip() for p in columnas[10].text.split(",")]
        campus = columnas[11].text.strip()
        creditos = int(columnas[12].text.strip())
        vacantes_totales = int(columnas[13].text.strip())
        vacantes_disponibles = int(columnas[14].text.strip())

        horario = []
        filas_horario = columnas[16].find_all("tr")
        for fila_h in filas_horario:
            cols_h = fila_h.find_all("td")
            dias_modulos = cols_h[0].text.strip().split(":")
            dias = [d or "SIN HORARIO" for d in dias_modulos[0].split("-")]
            modulos = [
                int(m) for m in dias_modulos[1].split(",") if m.isdigit()
            ]
            tipo = cols_h[1].text.strip()
            sala = cols_h[2].text.strip()
            for dia in dias:
                for mod in modulos:
                    horario.append(Modulo(tipo, dia, mod, sala))

        curso = Curso(
            nrc, sigla, retirable, ingles, seccion, aprobacion_especial,
            area, formato, categoria, nombre, profesor, campus, creditos,
            vacantes_totales, vacantes_disponibles, horario
        )
        cursos.append(curso)

    return cursos


def buscar_por_sigla(
    periodo: str, sigla: str, proxy_url: str = None
) -> List[Curso]:
    """Busca cursos por sigla en un período específico."""
    url = proxy_url if proxy_url else URL
    return obtener_cursos(f"{url}?cxml_semestre={periodo}&cxml_sigla={sigla}")


def buscar_por_profesor(
    periodo: str, profesor: str, proxy_url: str = None
) -> List[Curso]:
    """Busca cursos por profesor en un período específico."""
    url = proxy_url if proxy_url else URL
    return obtener_cursos(
        f"{url}?cxml_semestre={periodo}&cxml_profesor={profesor}"
    )


def buscar_por_nombre(
    periodo: str, nombre: str, proxy_url: str = None
) -> List[Curso]:
    """Busca cursos por nombre en un período específico."""
    url = proxy_url if proxy_url else URL
    return obtener_cursos(
        f"{url}?cxml_semestre={periodo}&cxml_nombre={nombre}"
    )


def buscar_por_nrc(
    periodo: str, nrc: str, proxy_url: str = None
) -> Optional[Curso]:
    """Obtiene un curso específico por su NRC en un período específico."""
    url = proxy_url if proxy_url else URL
    cursos = obtener_cursos(f"{url}?cxml_semestre={periodo}&cxml_nrc={nrc}")
    return cursos[0] if cursos else None


def buscar_curso(
    periodo: str, sigla: str = "", nrc: str = "",
    nombre: str = "", profesor: str = "", proxy_url: str = None
) -> Optional[List[Curso]]:
    """
    Busca un curso por sigla, NRC, nombre y profesor
    en un período específico.
    """
    if not any((sigla, nrc, nombre, profesor)):
        return None

    url = proxy_url if proxy_url else URL
    return obtener_cursos(
        f"{url}?cxml_semestre={periodo}&cxml_sigla={sigla}"
        f"&cxml_nrc={nrc}&cxml_nombre={nombre}&cxml_profesor={profesor}"
    )


def obtener_periodos(proxy_url: str = None) -> List[str]:
    """Obtiene la lista de períodos disponibles en Buscacursos."""
    url = proxy_url if proxy_url else URL
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    options = soup.select('select[name="cxml_semestre"] option')
    periodos = [
        o.text.strip().replace(" Primer Semestre", "-1")
        .replace(" Segundo Semestre", "-2")
        .replace(" TAV", "-3") for o in options
    ]
    return periodos
