from requests.utils import default_user_agent


WD = 'http://www.wikidata.org/entity/'
WDS = 'http://www.wikidata.org/entity/statement/'
WDQS_USER_AGENT = f'{default_user_agent()} (Wikidata bot; mailto:mister.synergy@yahoo.com)'
WDQS_ENDPOINT = 'https://query.wikidata.org/bigdata/namespace/wdq/sparql'