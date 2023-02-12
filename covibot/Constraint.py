from typing import Protocol
from pandas import DataFrame


class Constraint(Protocol):
    # fields to hardcode
    constraint_item : str
    query_template : str
    report_page_template : str

    # fields to explicitly initialize
    prop : str
    report_header_extras : list[str]  # empty list when omitted during init

    # fields used after initializiation
    report_page : str
    query : str
    violations : DataFrame
    query_time : float

    def __init__(self, prop:str) -> None:
        ...

    def query_violations(self) -> None:
        ...

    def get_report_section(self) -> str:
        ...
