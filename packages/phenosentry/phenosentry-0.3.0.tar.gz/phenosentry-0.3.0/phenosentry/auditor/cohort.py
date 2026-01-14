import typing

from collections import Counter, defaultdict

from phenopackets.schema.v2.phenopackets_pb2 import Cohort
from stairval.notepad import Notepad

from ._api import CohortAuditor, PhenopacketAuditor


class CohortMetaAuditor(CohortAuditor):
    """
    Cohort meta auditor audits a cohort with a sequence of cohort auditors.
    Each cohort member (a :class:`Phenopacket`) is then audited with a sequence of phenopacket auditors.
    """

    def __init__(
        self,
        auditors: typing.Iterable[CohortAuditor],
        phenopacket_auditors: typing.Optional[typing.Iterable[PhenopacketAuditor]] = (),
    ):
        self._auditors = tuple(auditors)
        if phenopacket_auditors:
            self._pp_auditors = tuple(phenopacket_auditors)
        else:
            self._pp_auditors = ()
        self._id = f"[{','.join(a.id() for a in self._auditors + self._pp_auditors)}]"

    def id(self) -> str:
        return self._id

    def audit(
        self,
        item: Cohort,
        notepad: Notepad,
    ):
        for auditor in self._auditors:
            auditor.audit(item, notepad)

        if self._pp_auditors:
            members_pad = notepad.add_subsection("members")
            for i, member in enumerate(item.members):
                member_pad = members_pad.add_subsection(i)
                for auditor in self._pp_auditors:
                    auditor.audit(member, member_pad)


class UniqueIdsAuditor(CohortAuditor):
    """
    A check to ensure that all phenopacket IDs within a cohort are unique.
    """

    def id(self) -> str:
        return "unique_pp_ids_in_cohort_check"

    def audit(
        self,
        item: Cohort,
        notepad: Notepad,
    ):
        id_counter = Counter()
        pp_id2cohort = defaultdict(set)
        for pp in item.members:
            pp_id2cohort[pp.id].add(item.id)
            id_counter[pp.id] += 1

        repeated = {pp_id: count for pp_id, count in id_counter.items() if count > 1}

        for pp_id, count in repeated.items():
            notepad.add_error(f"`{pp_id}` is not unique in the cohort")

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__module__}.{self.__class__.__qualname__}()"
