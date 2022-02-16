The GenderedNews project is meant to make available a set of indexes to measure gender imbalance in the main news sources in France. 

<h4>How did we choose the sources for our analysis ?</h4>

The system analyses every day the freely available online content of the six main news titles of daily national general press in France. Our reference basis is the ranking by the ACPM (<a href="https://www.acpm.fr/Les-chiffres/Diffusion-Presse/Presse-Payante/Presse-Quotidienne-Nationale">https://www.acpm.fr/Les-chiffres/Diffusion-Presse/Presse-Payante/Presse-Quotidienne-Nationale</a>). In the future, we mean to make available similar analysis on local or specialist news titles or titles with a slower publlishing rate. We are also considering similar measures for online content published on other media formats (radio, television, web <i>pure play</i> companies).

<h4>How do we access the content ?</h4>

The system goes through these online sources every day. The content accessed is therefore only the parts that are freely available (in general, it is the first few paragraphs of text for each new article of the day). To find the URL adresses of these articles, at the moment, we use the Twitter feeds of each source, through which most articles are published. This list of articles and their URLs is collected through Twitter, which gives us access to the freely available parts of the text with the help of scrapping techniques (it can be the whole article if it is a free article, or the first few available paragraphs if it's paid content).

<h4>What is a mention and a quote?</h4>

Our algorithm searches for two different things when it goes through news articles. It locates all first names that are mentionned in the article; we call them "mentions". In most cases, it refers to a person whose name the journalist is mentioning because they met the journalist during a report, or because they are one of the subjects of the article. But it can also be a person mentioned by someone else in the article, or a mention of a place which name contains a first name -for example, a building.

It also locates the quotes in the article, meaning the words reported by the journalist, be that between quotation marks or not. The algorithm is based on linguistics rules established after observation of the litterature and of the data. Quotes can be direct (it is the most frequent case, they are then often flagged by quotation marks), indirect (they can be then introduced by significant words like "selon" or speech verbs but without quotation marks.), or mixed.


<h4> How is the masculinty rate of mentioned people in news articles measured?</h4>

The method used to calculate the level of masculinity of people mentioned in news articles is very simple. A database of first names has been gathered from data from the INSEE (National Institute for Statistcs and Economic Studies). This file contains each first name for which we know the number of girl children and boy children bearing this name, which gives us the probability for a person called by this name to be a boy. This file contains about 11 000 non-ambiguous first names, meaning that the name cannot refer to anything else than a person.

The algorithm assigns this probability for each first name located in the text, then calculates a mean for each news article. This means is what we call the mentions masculinity rate of an article. For example: "Jean-Michel" has a masculinity rate of 1 according to INSEE stats, whereas "Loïs" is equivalent to a rate of 0.69, "Camille" to a 0.25 rate and "Maëva" will be 0. An article mentioning once "Jean-Michel" and twice "Camille" would thus have a mentions masculinity rate of (1 + 2*0.25)/3 = 0.5.

This algorithm has been evaluated on a sample of 100 articles that were coded manually (for each article, we located all first names and the gender to be assigned to them by a human reader). The algorithm has a calculated precision of 0.77 on first names, which means that 77% of the first names found by the algorithm are effectively first names. The recall rate is 0.87, which means that 87% of the first names that should be found in the news articles are effectively extracted by the algorithm. A <i>p</i> value has also been calculated. The <i>p</i> value is the probability that the algorithm gives a masculinity rate that equals to the masculinity rate that was calculated manually for each articles of the sample. The <i>p</i> value obtained for the mentions masculinity rate is about 0,748.

<h4> How is the gendered distribution of quotes in articles measured ?</h4>

The method used as of today is a rule-based method first developped by the <a href="http://www.sfu.ca/discourse-lab.html">Discourse Lab</a> of Simon Fraser University (Vancouver, Canada), which we adapted and improved.

A speaker is assigned to each identified quote with the help of a set of grammar rules (for example, the subject of the speech verb will often be the speaker) and neighbouring rules within the text (the speaker that was quoted just before).

The algorithm then assigns a gender to each speaker. The speaker can have different formats: it can be names ("Doanna Joe"), noun phrases ("la directrice de l'agence"), pronouns ("elle") or a combination of all cases ("Doanna Joe, la championne du monde"). The gender of each speaker is identified from one or several of the following clues: 
<ul>
<li>A gendered title (for exemple, "Madame")</li>
<li>A job name. This is identified with the help of a dictionary of gendered job names, built from the guide <i>Femme, j'écris ton nom … Guide d'aide à la féminisation des noms de métiers, titres, grades et fonctions</i>  (Institut national de la langue française, 1999)</li>
<li>Identification of the gender of a pronoun ("il, "elle", etc)</li>
<li>Named entitiy recognition: first, the system automatically identifies if the identified speaker text contains a person name (for example, the system will identify "Doanna Joe" as a named entity in the speaker "Doanna Joe, championne du monde"). From this entity, we can identify the first name and its gender with the help of two dictionaries that assigns a gender to an extended list of first names (one is included in the python library <i>gender-guesser</i> and another one built from the INSEE first names database).</li>
</ul>

This method has been evaluated on a test corpus coded by human readers. It has a precision of 0.85, which means that 85% of quotes extracted by the algorithm are indeed quotes, and its recall rate is 0.5, which means that anout 50% of the quotes in a news article are not found. The gender of the speaker for each quote can be determined in 50% of cases (the remaining 50% are often impersonal pronouns, organization names or unknown cases (unknown first name, gender-neutral job name, errors, ...))

The full code of the algorithm can be found at: <a href="https://gricad-gitlab.univ-grenoble-alpes.fr/getalp/genderednews/-/tree/master/gn_modules/processing/processings/quote_extractor">https://gricad-gitlab.univ-grenoble-alpes.fr/getalp/genderednews/-/tree/master/gn_modules/processing/processings/quote_extractor</a>

<h4>How is the category for each article identified?</h4> 

Each collected source (Le Monde, Le Parisien, etc) has its own system of naming categories and themes. To harmonize these categories, we defined a list of general themes from the observation of collected data (for example: SCIENCE_AND_ENVIRONMENT, CULTURE, POLITICS, etc). With this method, each category for each source is associated to the corresponding homogeneous category of our list. For example, for Le Monde, the category "Culture" is associated with CULTURE, "Sciences" with SCIENCE_AND_ENVIRONMENT; for Le Figaro, we associate native categories "Cinema" and "Music" with CULTURE, etc. Categories that appears less often are associated with the "UNDEFINED" category. This method allows us to compare our metrics in relation to the theme of the article for all our sources that have heterogeneous category denominations.


This code is available under the License GNU-AGPL v3.0 : <a href="https://gricad-gitlab.univ-grenoble-alpes.fr/getalp/genderednews">Git</a>
