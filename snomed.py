import os
import file_utils
from singleton import Singleton
from typing import List
import text_utils
from pandas import DataFrame
from config import data_path, search_index_path

ignored_domains = ['concepto no activo']
default_qualifier_attribute = '47429007'
qualifier_attributes = {'24028007': '272741003',  # Derecho : lateralidad
                        '7771000': '272741003',  # Izquierdo : lateralidad
                        '51440002': '272741003',  # Ambos/Bilateral : lateralidad

                        '90734009': '263502005',  # Crónico : Curso clínico
                        '373933003': '263502005',  # Agudo : Curso clínico
                        '19939008': '263502005',  # Subagudo : Curso clínico
                        '255314001': '263502005',  # Progresivo : Curso clínico
                        '7087005': '263502005',  # Intermitente : Curso clínico
                        '255227004': '263502005',  # Recurrente : Curso clínico
                        '263730007': '263502005',  # Duradero : Curso clínico
                        '14803004': '263502005',  # Transitorio : Curso clínico

                        '24484000': '246112005',  # Severo : Severidad
                        '255604002': '246112005',  # Leve : Severidad
                        '6736007': '246112005',  # Moderado : Severidad

                        '26643006': '410675002',  # Via oral : Método de administración de fármaco

                        '385644000': '408730004',  # Solicitado : Contexto de procedimiento
                        '385655000': '408730004',  # Suspendido : Contexto de procedimiento
                        '410535002': '408730004',  # Indicado : Contexto de procedimiento
                        '385643006': '408730004',  # Pendiente (Por realizar) : Contexto de procedimiento

                        '70232002': '370134009',  # Frecuente : Aspecto temporal
                        '27789000': '370134009',  # Infrecuente : Aspecto temporal

                        '10828004': '363713009',  # Positivo : Tiene interpretación
                        '260385009': '363713009',  # Negativo : Tiene interpretación
                        '17621005': '363713009',  # Normal : Tiene interpretación
                        '263654008': '363713009',  # Anormal : Tiene interpretación
                        '75540009': '363713009',  # Elevado : Tiene interpretación
                        '62482003': '363713009',  # Bajo : Tiene interpretación
                        '442777001': '363713009',  # En el límite superior : Tiene interpretación
                        '442779003': '363713009',  # En el límite inferior : Tiene interpretación
                        '263865001': '363713009',  # Escaso : Tiene interpretación
                        '260370003': '363713009',  # Disminución : Tiene interpretación
                        '260366006': '363713009',  # Aumento : Tiene interpretación
                        '260372006': '363713009',  # Deficiencia : Tiene interpretación
                        '20572008': '363713009',  # Bueno : Tiene interpretación
                        '18307000': '363713009',  # Alterado : Tiene interpretación
                        '371928007': '363713009',  # No significativo : Tiene interpretación
                        '2667000': '363713009',  # Ausencia de : Tiene interpretación
                        '371157007': '363713009',  # Dificultad de/para : Tiene interpretación

                        '263678003': '704326004',  # En reposo : Precondición
                        '255214003': '704326004',  # Luego del ejercicio : Precondición
                        '309604004': '704326004',  # Durante el ejercicio : Precondición

                        '410516002': '408729009',  # Ausencia de (Se sabe que está ausente): Contexto de un hallazgo
                        '410513005': '408731000',  # Antecedente de (En el pasado): Contexto temporal

                        '361684008': '363698007',  # Antecedente de (En el pasado): Sitio del hallazgo
                        '444148008': '408732007'  # Antecedente familiar de (persona en la familia del sujeto) : contexto de relación con el sujeto

                        }


class SnomedTerm():
    def __init__(self, code: str, description: str, domain: str, synonyms=[], parentcode: str = None):
        self.code = code
        self.description = description
        self.domain = domain
        self.parentcode = parentcode
        if synonyms != synonyms:  # Nan
            synonyms = []
        self.synonyms = synonyms

    @property
    def to_snomed(self):
        return '{} |{}|'.format(self.code, self.description)


@Singleton
class Snomed():

    def __init__(self):
        self.terms = file_utils.load_from_file(os.path.join(data_path, search_index_path))
        self.terms = self.terms[~self.terms['Domain'].isin(ignored_domains)]

    def search_by_description(self, description: str, exact_match=False, limit=50, domains=None) -> List[SnomedTerm]:
        description = text_utils.remove_tildes(description).lower()

        if exact_match:
            exact_matches = self.terms[self.terms['Search'] == description]
            return self.results_to_terms(exact_matches.head(limit))
        words = description.split()

        result = self.terms
        for word in words:
            result = result[result['Search'].str.contains(word, regex=False)]

        if domains is not None and len(domains) > 0:
            result = result[result['Domain'].isin(domains)]

        result = result.head(limit)
        result['StartsWith'] = result['Search'].str.startswith(description)
        result = result.sort_values(by=['StartsWith', 'Length'], ascending=[False, True])
        return self.results_to_terms(result)

    def search_by_code(self, code: str) -> SnomedTerm:
        term = self.terms.loc[[code], ['Synonyms', 'Description', 'Domain', 'Is_Synonym']].sort_values(by='Is_Synonym').iloc[0]
        return SnomedTerm(term.name, term['Description'], term['Domain'], term['Synonyms'])

    def results_to_terms(self, results: DataFrame) -> List[SnomedTerm]:
        terms = []
        for index, row in results.iterrows():
            terms.append(SnomedTerm(index, row['Description'], row['Domain'], row['Synonyms']))
        return terms

    def get_attribute_for_pair(self, term1, term2) -> SnomedTerm:
        attribute_code = None

        if term2.domain == 'calificador' or term2.code in qualifier_attributes.keys():
            attribute_code = qualifier_attributes.get(term2.code, default_qualifier_attribute)

        # Ausencia de
        elif term2.code == '410516002':
            if term2.domain in ['hallazgo', 'trastorno', 'anomalía morfológica']:
                attribute_code = 408729009  # Contexto de un hallazgo
            elif term2.domain == 'procedimiento':
                attribute_code = 408730004  # Contexto de un procedimiento

        elif term2.domain == 'atributo':
            return None

        elif term1.domain in ['hallazgo', 'trastorno', 'anomalía morfológica']:

            if term2.domain == 'estructura corporal':
                attribute_code = '363698007'  # Sitio del hallazgo
            elif term2.domain in ['sustancia', 'producto', 'producto medicinal']:
                tratado_con_qualifier = [x for x in term2.qualifiers if x.code == '28995006']  # Tratado con
                if len(tratado_con_qualifier) > 0:
                    attribute_code = '28995006'

        elif term1.domain == 'procedimiento' and term2.domain == 'estructura corporal':
            attribute_code = '363704007'  # Sitio del procedimiento

        elif term2.code == '28995006':  # Tratado con
            return None

        if attribute_code is None:
            attribute_code = default_qualifier_attribute

        return self.search_by_code(attribute_code)
