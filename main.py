import pywikibot as pwb

from covibot.Constraint import Constraint
from covibot.SingleBestValueConstraint import SingleBestValueConstraint


SITE = pwb.Site('wikidata', 'wikidata')
SITE.login()


def write_to_wiki(constraint:Constraint) -> None:
    page = pwb.Page(SITE, constraint.report_page)
    page.text = constraint.get_report_section()
    page.save(summary='update report')


def print_report(constraint:Constraint) -> None:
    print(constraint.get_report_section())


def main() -> None:
    properties = {
        'P227' : [
            SingleBestValueConstraint,
        ]
    }

    for prop, constraints in properties.items():
        for constraint_class in constraints:
            constraint = constraint_class(prop)
            write_to_wiki(constraint)


if __name__=='__main__':
    main()
