from io import StringIO
from time import perf_counter

import pandas as pd
import requests

from .config import WD, WDS, WDQS_USER_AGENT, WDQS_ENDPOINT


class SingleBestValueConstraint:
    constraint_item : str = 'Q52060874'
    constraint_type : str = 'Single best value constraint'
    report_page_template : str = 'Property talk:{prop}/Constraint violations/Single best value constraint'

    query_template = """SELECT ?item ?identifier ?s ?separator ?separator_value WITH {{
  SELECT ?item WHERE {{
    ?item wdt:{prop} ?identifier
  }} GROUP BY ?item HAVING(COUNT(?identifier) > 1)
}} AS %subquery WHERE {{
  INCLUDE %subquery .
  ?item p:{prop} ?s .
  ?s ps:{prop} ?identifier; rdf:type wikibase:BestRank .
  OPTIONAL {{
    VALUES ?separator {{
      pq:{separators}
    }}
    ?s ?separator ?separator_value .
  }}
}}"""

    query_formatter_template = """SELECT DISTINCT ?formatter WHERE {{
  wd:{prop} wdt:P1630 ?formatter
}}"""
    query_separator_template = """SELECT DISTINCT ?separator WHERE {{
  wd:{prop} p:P2302 [ ps:P2302 wd:{constraint_item}; pq:P4155 ?separator ] .
}}"""

    prop : str
    query : str
    report_page : str

    violations : pd.DataFrame
    query_time : float

    formatter : str
    separators : list[str]

    def __init__(self, prop:str) -> None:
        self.prop = prop
        self.report_page = self.report_page_template.format(prop=self.prop)

        self.query_formatter()
        self.query_separators()

        self.query = self.query_template.format(
            prop=self.prop,
            separators=' pq:'.join(self.separators)
        )

        self.query_violations()

    def query_formatter(self) -> None:
        query_formatter = self.query_formatter_template.format(
            prop=self.prop
        )
        response = requests.post(
            url=WDQS_ENDPOINT,
            data={
                'query' : query_formatter,
                'format' : 'json'
            },
            headers={
                'User-Agent': WDQS_USER_AGENT,
            }
        )

        payload = response.json()
        formatters = []
        for row in payload.get('results', {}).get('bindings', {}):
            formatter = row.get('formatter', {}).get('value')
            if formatter is None:
                continue
            formatters.append(formatter)

        if len(formatters) > 0:
            self.formatter = formatters[0]  # TODO: report if more than one formatter is found
        else:
            self.formatter = '$1'


    def query_separators(self) -> None:
        query_separator = self.query_separator_template.format(
            prop=self.prop,
            constraint_item=self.constraint_item
        )

        response = requests.post(
            url=WDQS_ENDPOINT,
            data={
                'query' : query_separator,
                'format' : 'json'
            },
            headers={
                'User-Agent': WDQS_USER_AGENT,
            }
        )

        payload = response.json()
        self.separators = []
        for row in payload.get('results', {}).get('bindings', {}):
            separator = row.get('separator', {}).get('value')
            if separator is None:
                continue
            self.separators.append(separator[len(WD):])


    def query_violations(self) -> None:
        columns = {
            'item' : str,
            'identifier' : str,
            'statement' : str,
            'separator' : str,
            'separator_value' : str
        }

        query_start_time = perf_counter()
        query_result = requests.post(
            url=WDQS_ENDPOINT,
            data={
                'query' : self.query
            },
            headers={
                'User-Agent': WDQS_USER_AGENT,
                'Accept' : 'text/csv'
            }
        ).text
        self.query_time = perf_counter() - query_start_time

        self.violations = pd.read_csv(
            StringIO(query_result),
            header=0,
            names=list(columns.keys()),
            dtype=columns
        )

        self.violations['item'] = self.violations['item'].str.slice(len(WD))
        self.violations['separator'] = self.violations['separator'].str.slice(len(WD))
        self.violations['statement'] = self.violations['statement'].str.slice(len(WDS))

        self.violations = self.violations.loc[self.violations['item'].str.startswith('Q')]

        self.violations['num'] = self.violations['item'].str.slice(1).astype(int)
        self.violations.sort_values(by='num', inplace=True)


    def separator_saves_it(self, df:pd.DataFrame) -> bool:
        separators = df['separator'].unique().tolist()
        statements = df['statement'].unique().tolist()

        for separator in separators:
            statements_with_separator = df.loc[df['separator']==separator, 'statement'].unique().tolist()
            if sorted(statements) != sorted(statements_with_separator):
                continue

            separator_values = df.loc[(df['separator']==separator) & df['statement'].isin(statements_with_separator), 'separator_value'].tolist()
            if len(separator_values) == len(list(set(separator_values))):
                return True

        return False


    def get_report_section(self) -> str:
        items = self.violations['item'].unique().tolist()

        separator_saves = 0
        report_lines = []
        for item in items:
            subset = self.violations.loc[self.violations['item']==item]
            if self.separator_saves_it(subset) is True:
                separator_saves += 1
                continue

            identifiers = sorted(subset['identifier'].tolist())
            identifiers_linked = [ f'[{self.formatter.replace("$1", identifier)} {identifier}]' for identifier in identifiers ]

            report_lines.append(f'# {{{{Q|{item}}}}}: {", ".join(identifiers_linked)}')

        report = [
            f'Query time: {self.query_time:.1f} sec<br>',
            f'Defined separators: {{{{Property|{"}}, {{Property|".join(self.separators)}}}}}<br>',
            f'Violations count: {len(items)-separator_saves} items',
        ]

        return '\n'.join([ *report, *report_lines ])
