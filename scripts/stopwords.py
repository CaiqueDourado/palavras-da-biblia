"""Function words of Portuguese (and of the Almeida's older Portuguese) left out of the "most frequent
words" study: articles, prepositions and their contractions, pronouns, conjunctions, common adverbs and
the forms of ser, estar, ter, haver. Verbs with meaning (disse, fez, ouvir) stay in."""

STOPWORDS = set("""
a à ao aos as às o os um uma uns umas de do da dos das no na nos nas num numa nuns numas em por pelo pela pelos
pelas para pra com sem sob sobre entre até contra desde perante ante após trás diante dentro fora junto
e ou mas porém pois porque que se como quando onde quanto quantos quanta quantas qual quais quem cujo cuja
cujos cujas nem também ainda já então assim logo porquanto conforme segundo enquanto todavia contudo senão
eis eu tu ele ela nós vós eles elas me te se lhe lhes nos vos o a os as mim ti si comigo contigo consigo
conosco convosco dele dela deles delas nele nela neles nelas meu minha meus minhas teu tua teus tuas seu
sua seus suas nosso nossa nossos nossas vosso vossa vossos vossas este esta estes estas esse essa esses
essas aquele aquela aqueles aquelas isto isso aquilo neste nesta nestes nestas nesse nessa nesses nessas
naquele naquela naqueles naquelas deste desta destes destas desse dessa desses dessas daquele daquela
daqueles daquelas disto disso daquilo nisto nisso naquilo àquele àquela àqueles àquelas todo toda todos
todas tudo outro outra outros outras mesmo mesma mesmos mesmas cada algum alguma alguns algumas nenhum
nenhuma qualquer quaisquer muito muita muitos muitas mais menos tão tanto tanta tantos tantas só somente
não sim bem mal aqui ali lá cá aí agora hoje sempre nunca jamais também ora pois lo la los las no na nos
ser sou és é somos sois são era eras éramos éreis eram fui foste foi fomos fostes foram fora seja sejas
sejamos sejais sejam fosse fossem for formos forem será serás seremos sereis serão seria seriam sendo sido
estar estou estás está estamos estais estão estava estavam esteve estiveram esteja estejam estando
ter tenho tens tem temos tendes têm tinha tinhas tínhamos tinham teve tiveram tenha tenham tendo tido terá
terão haver hei há havemos haveis hão havia haviam houve houvesse haja hajam havendo
""".split())
