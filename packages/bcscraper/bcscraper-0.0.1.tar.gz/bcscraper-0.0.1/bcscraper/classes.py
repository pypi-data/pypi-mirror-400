"""Clases básicas como Modulo y Curso"""
from typing import List


class Modulo:
    """Clase que define un módulo de clases."""
    def __init__(self, tipo: str, dia: str, modulo: int, sala: str) -> None:
        self.tipo = tipo
        self.dia = dia
        self.modulo = modulo
        self.sala = sala

    def __repr__(self) -> str:
        return f"{self.dia} {self.modulo} {self.tipo} {self.sala}"


class Curso:
    """Clase que define un curso."""
    def __init__(
        self, nrc: str, sigla: str, retirable: bool, ingles: bool,
        seccion: int, aprobacion_especial: bool, area: str, formato: str,
        categoria: str, nombre: str, profesor: List[str], campus: str,
        creditos: int, vacantes_totales: int, vacantes_disponibles: int,
        horario: List[Modulo]
    ) -> None:
        self.nrc = nrc
        self.sigla = sigla
        self.retirable = retirable
        self.ingles = ingles
        self.seccion = seccion
        self.aprobacion_especial = aprobacion_especial
        self.area = area
        self.formato = formato
        self.categoria = categoria
        self.nombre = nombre
        self.profesor = profesor
        self.campus = campus
        self.creditos = creditos
        self.vacantes_totales = vacantes_totales
        self.vacantes_disponibles = vacantes_disponibles
        self.horario = horario

    def __repr__(self):
        return f"{self.sigla}-{self.seccion} {self.nombre} ({self.nrc})"
