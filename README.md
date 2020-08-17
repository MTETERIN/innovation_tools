# innovation_tools

It's the only repository I can show.

This service is implemented with django-material and allows you to perform semantic tweet analysis using the BERT model, do CRUD stuff with data and build dashboards for services with different kind of input parameters.
The model is trained on 1600,000 tweets and shows an accuracy near 93%. and allows you to predict the types of tweets: neutral, negative and positive.

TODO:

1. DRY
2. Caching must be added because page loading takes 1.5 minutes in some cases
3. Remove Database from repository
4. Add Script with twitter api crawling
