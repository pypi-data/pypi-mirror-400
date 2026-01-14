import typing

from hpotk import MinimalOntology, TermId
from hpotk.constants.hpo.base import PHENOTYPIC_ABNORMALITY

from phenopackets.schema.v2.phenopackets_pb2 import Phenopacket
from stairval.notepad import Notepad

from ._api import PhenopacketAuditor


class PhenopacketMetaAuditor(PhenopacketAuditor):
    """
    `PhenopacketMetaAuditor` applies several phenopacket auditors in a sequence.
    """

    # TODO: this could arguably be generified even further, to support auditing any `T`,
    # given a sequence of `Auditor[T]`...

    def __init__(
        self,
        auditors: typing.Iterable[PhenopacketAuditor],
    ):
        self._auditors = tuple(auditors)
        self._id = "[" + ",".join(check.id() for check in self._auditors) + "]"

    def id(self) -> str:
        return self._id

    def audit(
        self,
        item: Phenopacket,
        notepad: Notepad,
    ):
        for auditor in self._auditors:
            auditor.audit(
                item=item,
                notepad=notepad,
            )


class NoUnwantedCharactersAuditor(PhenopacketAuditor):
    """
    A check to ensure that phenopacket identifiers do not include unwanted characters (e.g., whitespace).

    The following phenopacket fields are checked:

    * id
    * subject > id
    * diseases > # > term > label
    * interpreattions > # > id
    * interpreattions > # > diagnosis > disease > label
    * meta_data > external_references > # > description
    """

    @staticmethod
    def no_whitespace(
        whitespaces: typing.Iterable["str"] = ("\t", "\n", "\r\n"),
    ) -> "NoUnwantedCharactersAuditor":
        return NoUnwantedCharactersAuditor(whitespaces)

    def __init__(
        self,
        unwanted: typing.Iterable[str],
    ):
        self._unwanted = set(unwanted)

    def id(self) -> str:
        return "unwanted_characters_check"

    def audit(
        self,
        item: Phenopacket,
        notepad: Notepad,
    ):
        self._check_unwanted_characters(item.id, notepad.add_subsection("id"))
        _, subject_id_pad = notepad.add_subsections("subject", "id")
        self._check_unwanted_characters(item.subject.id, subject_id_pad)

        # Disease name in diseases and variant interpretations
        diseases_pad = notepad.add_subsection("diseases")
        for i, disease in enumerate(item.diseases):
            _, _, label_pad = diseases_pad.add_subsections(i, "term", "label")
            self._check_unwanted_characters(disease.term.label, label_pad)

        interpretations_pad = notepad.add_subsection("interpretations")
        for i, interpretation in enumerate(item.interpretations):
            itp_pad = interpretations_pad.add_subsection(i)
            id_pad = itp_pad.add_subsection("id")
            self._check_unwanted_characters(interpretation.id, id_pad)
            _, _, label_pad = itp_pad.add_subsections("diagnosis", "disease", "label")
            self._check_unwanted_characters(interpretation.diagnosis.disease.label, label_pad)

        # PubMed title
        _, ers_pad = notepad.add_subsections("meta_data", "external_references")
        for i, er in enumerate(item.meta_data.external_references):
            _, er_pad = ers_pad.add_subsections(i, "description")
            self._check_unwanted_characters(er.description, er_pad)

    def _check_unwanted_characters(
        self,
        value: str,
        notepad: Notepad,
    ):
        reported = set()
        for ch in value:
            if ch in self._unwanted and ch not in reported:
                notepad.add_error("includes an unwanted character '" + ch + "'")
                reported.add(ch)

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__module__}.{self.__class__.__qualname__}(unwanted={sorted(self._unwanted)})"


class DeprecatedTermIdAuditor(PhenopacketAuditor):
    """
    Checks that no HPO term id is deprecated.
    """

    def __init__(
        self,
        hpo: MinimalOntology,
    ):
        self._hpo = hpo

    def id(self) -> str:
        return "deprecated_term_id_check"

    def audit(
        self,
        item: Phenopacket,
        notepad: Notepad,
    ):
        pf_pad = notepad.add_subsection("phenotypic_features")
        for i, phenotype in enumerate(item.phenotypic_features):
            term = self._hpo.get_term(phenotype.type.id)
            if term is not None and (term.is_obsolete or term.identifier.value != phenotype.type.id):
                _, _, id_pad = pf_pad.add_subsections(i, "type", "id")
                id_pad.add_error(f"`{phenotype.type.id}` has been deprecated")

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f'{self.__class__.__module__}.{self.__class__.__qualname__}(hpo="{self._hpo.version}")'


class PhenotypicAbnormalityAuditor(PhenopacketAuditor):
    """
    Checks that all phenotypic feature ontology classes
    are descendants of the `Phenotypic abnormality <https://hpo.jax.org/app/browse/term/HP:0000118>`_ [HP:0000118]).
    """

    def __init__(
        self,
        hpo: MinimalOntology,
    ):
        self._hpo = hpo

    def id(self) -> str:
        return "phenotypic_abnormality_descendant_auditor"

    def audit(
        self,
        item: Phenopacket,
        notepad: Notepad,
    ):
        pfs_pad = notepad.add_subsection("phenotypic_features")
        for i, pf in enumerate(item.phenotypic_features):
            if pf.type.id.startswith("HP:"):
                if not self._hpo.graph.is_descendant_of_or_equal_to(pf.type.id, PHENOTYPIC_ABNORMALITY):
                    _, pf_pad = pfs_pad.add_subsections(i, "type")
                    pf_pad.add_error(
                        f"{pf.type.label} [{pf.type.id}] is not a descendant of Phenotypic abnormality [HP:0000118]"
                    )


class PresentAnnotationPropagationAuditor(PhenopacketAuditor):
    """
    Checks that the phenotypic feature ontology classes
    does not contain a present term and its present ancestor.
    """

    def __init__(
        self,
        hpo: MinimalOntology,
    ):
        self._hpo = hpo

    def id(self) -> str:
        return "present_annotation_propagation_auditor"

    def audit(
        self,
        item: Phenopacket,
        notepad: Notepad,
    ):
        pfs_pad = notepad.add_subsection("phenotypic_features")
        present2idx = {
            TermId.from_curie(pf.type.id): i for i, pf in enumerate(item.phenotypic_features) if not pf.excluded
        }
        for pf in present2idx:
            for anc in self._hpo.graph.get_ancestors(pf):
                if anc in present2idx:
                    term_label = self._hpo.get_term_name(pf)
                    anc_label = self._hpo.get_term_name(anc)
                    pfs_pad.add_error(
                        f"annotation to {anc_label} [{anc.value}] (#{present2idx[anc]}) is redundant due to annotation to {term_label} [{pf.value}] (#{present2idx[pf]})"
                    )


class ExcludedAnnotationPropagationAuditor(PhenopacketAuditor):
    """
    Checks that the phenotypic feature ontology classes
    does not contain an excluded term and its excluded descendant.
    """

    def __init__(
        self,
        hpo: MinimalOntology,
    ):
        self._hpo = hpo

    def id(self) -> str:
        return "excluded_annotation_propagation_auditor"

    def audit(
        self,
        item: Phenopacket,
        notepad: Notepad,
    ):
        excluded2idx = {
            TermId.from_curie(pf.type.id): i for i, pf in enumerate(item.phenotypic_features) if pf.excluded
        }

        pfs_pad = notepad.add_subsection("phenotypic_features")
        for pf in excluded2idx:
            for anc in self._hpo.graph.get_ancestors(pf):
                if anc in excluded2idx:
                    term_label = self._hpo.get_term_name(pf)
                    anc_label = self._hpo.get_term_name(anc)
                    pfs_pad.add_error(
                        f"exclusion of {term_label} [{pf.value}] (#{excluded2idx[pf]}) is redundant due to exclusion of its ancestor {anc_label} [{anc.value}] (#{excluded2idx[anc]})"
                    )


class AnnotationInconsistencyAuditor(PhenopacketAuditor):
    """
    Checks that the phenotypic feature ontology classes
    does not contain a present term and its excluded ancestor.
    """

    def __init__(
        self,
        hpo: MinimalOntology,
    ):
        self._hpo = hpo

    def id(self) -> str:
        return "annotation_inconsistency_auditor"

    def audit(
        self,
        item: Phenopacket,
        notepad: Notepad,
    ):
        present2idx = {}
        excluded2idx = {}
        for i, pf in enumerate(item.phenotypic_features):
            if pf.excluded:
                excluded2idx[TermId.from_curie(pf.type.id)] = i
            else:
                present2idx[TermId.from_curie(pf.type.id)] = i

        pfs_pad = notepad.add_subsection("phenotypic_features")
        for pf in present2idx:
            for anc in self._hpo.graph.get_ancestors(pf):
                if anc in excluded2idx:
                    term_label = self._hpo.get_term_name(pf)
                    anc_label = self._hpo.get_term_name(anc)
                    pfs_pad.add_error(
                        f"presence of {term_label} [{pf.value}] (#{present2idx[pf]}) is logically inconsistent with exclusion of {anc_label} [{anc.value}] (#{excluded2idx[anc]})"
                    )
