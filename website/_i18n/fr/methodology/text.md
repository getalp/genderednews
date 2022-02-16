Le projet GenderedNews vise à mettre à disposition du public des mesures régulières des inégalités de représentation de genre dans les sources d’information les plus utilisées en France. La méthode que nous employons consiste à mesurer dans chaque article la part des hommes et des femmes mentionnées (ceux et celles dont le nom apparaît) et celle des hommes et des femmes citées (c’est-à-dire à qui la parole est donnée). Deux indices quotidiens sont calculés pour chaque source, un pour les mentions et un pour les citations.

<h4>Comment nous avons choisi les journaux que nous analysons ?</h4>

Nous analysons chaque jour les contenus en accès libre sur le web des six principaux journaux de la presse quotidienne nationale généraliste en France. Le classement de l'ACPM nous a servi de base de référence (<a href="https://www.acpm.fr/Les-chiffres/Diffusion-Presse/Presse-Payante/Presse-Quotidienne-Nationale">https://www.acpm.fr/Les-chiffres/Diffusion-Presse/Presse-Payante/Presse-Quotidienne-Nationale</a>). À l'avenir nous proposerons une analyse similaire d'autres journaux de la presse locale, spécialisée ou à parution moins régulière. Nous envisageons aussi de fournir des mesures similaires pour les contenus publiés sur le web par d'autres médias  (radio, télévision et pure players du web).

<h4>Comment nous accédons à leurs contenus ?</h4>

Les sources que nous analysons sont parcourues chaque jour sur le web. Nous n'accédons de ce fait qu'au contenu gratuit (en général quelques paragraphes de texte pour chaque nouvel article de la journée). Pour trouver les URL de ces articles nous utilisons pour l’instant les fils Twitter de chaque source, sur lesquels sont publiés des liens vers la plupart des articles. Nous collectons cette liste d’articles et leurs URL sur Twitter et accédons ensuite au texte disponible librement en ligne (tout l’article s’il s’agit d’un article gratuit, ou les premiers paragraphes disponibles s’il s’agit d’un article payant).

<h4>Qu'est-ce qu'une mention et une citation?</h4>

L'algorithme qui parcourt les contenus des sites d'information cherche deux choses différentes. D'une part il cherche les prénoms cités dans l'article que nous considérons comme des « mentions ». Dans la majorité des cas il s'agit d'une personne que mentionne le ou la journaliste parce qu'il ou elle l'a rencontré•e dans un reportage ou qu'elle est un des sujets de son article. Mais il peut aussi s'agir de personnes mentionnées par d'autres personnes dans l'article ou encore, plus rarement, de la mention de prénoms désignant d'autres choses comme des lieux ou des institutions nommé•es d'après des personnes.

D'autre part il cherche les citations présentes dans l'article, c'est-à-dire les propos rapportés par le ou la journaliste, qu'ils soient entre guillemets ou pas. L'algorithme se fonde pour cela sur des règles linguistiques établies à l’aide de la littérature et de l'observation des données. Les citations peuvent être directes (c’est le cas le plus fréquent et elles sont alors souvent marquées par des guillemets), indirectes (on les reconnaît parce qu’elles sont introduites par des mots significatifs comme « selon » ou par des verbes de parole mais sans guillemets), ou mixtes (un mélange des deux).

<h4>Comment est calculée la masculinité des mentions de personnes dans les articles ?</h4>

Pour calculer le niveau de masculinité des personnes mentionnées dans les articles nous utilisons une méthode très simple. Nous avons constitué à partir des données de l'INSEE un fichier de prénoms pour lesquels nous connaissons le nombre d'enfants filles et garçons à qui il est attribué chaque année et donc la probabilité que son porteur soit un garçon. Ce fichier contient plus de 11  000 prénoms non ambigus, c'est-à-dire qu'ils ne désignent rien d'autre que des personnes.

Notre algorithme attribue cette probabilité à chaque prénom qu'il rencontre dans le texte puis en fait la moyenne pour chaque article. C'est ce chiffre que nous appelons la masculinité des mentions d'un article. On peut illustrer à partir de l’exemple suivant : le prénom Jean-Michel a un taux de masculinité de 1 selon l'INSEE alors que Loïs a un taux de 0.69, Camille de 0.25 et Maëva de 0. Un article qui mentionnerait un Jean-Michel et deux Camille aurait donc un taux de masculinité des mentions de (1 + 2x0,25)/3 = 0,5.

Nous avons évalué cet algorithme sur un échantillon de 100 articles que nous avons annoté à la main (nous avons pour chaque article annoté les prénoms à identifier et le genre déduit par un·e lecteur·ice humain·e). L’algorithme a une précision de 0.77 sur les prénoms, ce qui signifie que 77% des prénoms trouvés par l’algorithme sont effectivement des prénoms. Le taux de rappel est de 0.87, ce qui signifie que 87% des prénoms à trouver dans les articles sont effectivement trouvés. Nous avons également calculé la valeur <i>p</i> de l’algorithme, à savoir la probabilité que notre algorithme donne effectivement le taux de masculinité correspondant à celui que nous avons calculé à la main pour chaque article de l’échantillon. La valeur <i>p</i> obtenue sur le taux de masculinité des mentions est de environ 0,748.

<h4>Comment est calculée la distribution genrée des  citations de personnes dans les articles ?</h4>

Nous utilisons actuellement une méthode à base de règles développée par le <a href="http://www.sfu.ca/discourse-lab.html">Discourse Lab</a> de l'Université Simon Fraser (Vancouver, Canada) que nous avons adaptée et améliorée.

Nous attribuons à chaque citation (identifiée selon les règles précédemment décrites) un·e auteur·ice, à partir de règles grammaticales (par exemple, le sujet grammatical du verbe introductif) ou de proximité dans le texte (la·e locuteur·ice cité·e précédemment).

Nous attribuons ensuite un genre aux auteur•ices des citations. Il peut s’agir de noms ("Doanna Joe"), de groupes nominaux ("la directrice de l'agence »), de pronoms ("elle ») ou de combinaisons de ces trois catégories ("Doanna Joe, la championne du monde"). Le genre de chaque auteur·ice d’une citation est déterminé à partir d'un ou plusieurs des indices suivants : 
<ul>
<li>la présence d'un titre genré (par exemple, "Madame »)</li>
<li>la présence d’un nom de métier. Pour cela, nous nous aidons d’un dictionnaire de noms de métiers ou de fonctions en version masculine et féminine constitué à partir du guide Femme, j'écris ton nom … Guide d'aide à la féminisation des noms de métiers, titres, grades et fonctions  (Institut national de la langue française, 1999)</li>
<li>la reconnaissance du genre du pronom ("il, "elle", etc)</li>
<li>la reconnaissance d'entités nommées : d’abord, le système identifie automatiquement s’il y a un nom de personne dans chaque auteur·ice de citations identifié·e (par exemple, le système reconnaîtra « Doanna Joe » comme une personne si l’auteur·ice est « Doanna Joe, championne du monde »). A partir de ce nom de personne, nous pouvons identifier le prénom et son genre à partir de deux dictionnaires qui attribuent un genre à chaque prénom (un inclus dans la librairie python gender-guesser et un autre construit à partir de la base INSEE des prénoms).</li>
</ul>

Cette méthode a été évaluée sur un corpus test annoté par des lecteur·ice·s humain·e·s. Sa précision est de 0.85, ce qui signifie que 85% des citation détectées sont effectivement des citations, et son taux de rappel de 0.5, ce qui signifie que 50% des citations contenues dans les articles ne sont pas trouvées. Nous arrivons à déterminer le genre de l’auteur•ice des citations dans 50% des cas (les 50% restants correspondent souvent à des pronoms impersonnels, des noms d'organisations, ou encore à des inconnues (prénom non connu, métier non genré, erreur d'extraction, ...).

Le code de l’algorithme que nous utilisons peut être consulté à cette adresse: <a href="https://gricad-gitlab.univ-grenoble-alpes.fr/getalp/genderednews/-/tree/master/gn_modules/processing/processings/quote_extractor">https://gricad-gitlab.univ-grenoble-alpes.fr/getalp/genderednews/-/tree/master/gn_modules/processing/processings/quote_extractor</a>

<h4>Comment déterminons-nous la catégorie d'un article ?</h4> 

Chaque journal possède ses propres dénominations de rubriques. Pour les harmoniser nous avons défini une liste de catégories thématiques générales à partir de l'observation des données collectées (par exemple: "Science et environnement", "Culture", "Politique", ...). Avec cette méthode, les rubriques propres à chaque journal sont associées à une catégorie correspondante dans notre liste. Par exemple, pour Le Monde, la rubrique "Culture" est associée avec CULTURE, "Sciences" avec SCIENCE_ET_ENVIRONNEMENT; pour Le Figaro les rubriques "Cinéma" et "Musique" sont regroupées dans CULTURE, etc. Les rubriques plus rares sont regroupées dans une catégorie "INDEFINI". Cette méthode nous permet de comparer nos mesures en fonction du thème de l'article dans plusieurs journaux aux dénominations de rubriques hétérogènes.

Le code de ce site est disponible sous licence GNU-AGPL v3.0 : <a href="https://gricad-gitlab.univ-grenoble-alpes.fr/getalp/genderednews">Git</a>
