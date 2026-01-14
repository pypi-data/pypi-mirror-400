import abc

from stairval import Auditor
from phenopackets.schema.v2.phenopackets_pb2 import Family, Cohort, Phenopacket


class PhenopacketAuditor(Auditor[Phenopacket], metaclass=abc.ABCMeta):
    """
    Audits a phenopacket.
    """

    @abc.abstractmethod
    def id(self) -> str:
        """
        Get the unique identifier for the phenopacket auditor.
        """
        ...


class CohortAuditor(Auditor[Cohort], metaclass=abc.ABCMeta):
    """
    Audits a cohort.
    """

    @abc.abstractmethod
    def id(self) -> str:
        """
        Get the unique identifier for the cohort auditor.
        """
        ...


class FamilyAuditor(Auditor[Family], metaclass=abc.ABCMeta):
    """
    Audits a family.
    """

    @abc.abstractmethod
    def id(self) -> str:
        """
        Get the unique identifier for the family auditor.
        """
        ...
