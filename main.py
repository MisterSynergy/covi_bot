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
    prop = 'P227'

    sbv_constraint = SingleBestValueConstraint(prop)
    write_to_wiki(sbv_constraint)


if __name__=='__main__':
    main()
