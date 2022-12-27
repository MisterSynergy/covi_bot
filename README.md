# covi_bot
Wikidata bot that writes constraint violation reports

This is a bot that writes constraint violation reports to wiki pages. It does not yet support all constraint violations, and is only used for select properties.

## Technical requirements
The bot is currently scheduled to run daily on [Toolforge](https://wikitech.wikimedia.org/wiki/Portal:Toolforge) from within the `msynbot` tool account. It depends on the [shared pywikibot files](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Pywikibot#Using_the_shared_Pywikibot_files_(recommended_setup)) and is running in a Kubernetes environment using Python 3.9.2.