---
author: geosc
year: 2024
title: 0011 Correction Proof  v2
source: geosc_2024_0011_Correction_Proof__v2.pdf
---

# 0011 Correction Proof  v2

**Author:** geosc
**Year:** 2024
**Source:** geosc_2024_0011_Correction_Proof__v2.pdf

---

## Content

### Page 1

ORIGINALPAPER
Does land price affect housing prices?
Evidence from Santiago, Chile 2008-2019
José Francisco
Vergara-Perucich1(cid:12)
1FacultaddeArquitectura,Animación,DiseñoyConstrucción,UniversidaddeLasAméricas,Santiago,Chile
(cid:12)jvergara@udla.cl
Abstract Keywords
This study embarks on an exploration of the intricate relationship between land prices Granger,
and housing prices within the dynamic urban landscape of Santiago, Chile, spanning LandPrice,
HousingPrice,
from2008to2019. Amidstanescalatinghousingaffordabilitycrisisandtheburgeoning
Chile,
prevalence of informal settlements, this research seeks to elucidate the underlying fac-
RealEstate,
torscontributingtohousingpricedynamics,withaparticularemphasisontheroleofland Housing
prices. Utilizingarobustdatasetencompassingover556,400transactions,meticulously
compiledfromtheSantiagoRealEstateRegistrar,thisinvestigationemploysarigorous
multi-criteriaevaluationmethodology,incorporatingGrangercausalityanalysistodissect
the complex interplay between various economic indicators. At the heart of this analy-
Received:
sis lies the innovative application of weekly data transformations and the Augmented
5March2024
Dicky-Fullertesttoensurethestationarityofvariables,therebylayingasolidfoundation
Receivedinrevisedform:
for the Granger causality assessment. The study’s findings illuminate a nuanced land-
28August2024
scapewhere,contrarytoprevailingassumptions,landpricesdonotexhibitauniversally
Accepted:
significantimpactonhousingprices. Instead,theinfluenceoflandpricesonhousingaf-
19October2024
fordabilityisintricatelylinkedtootherpivotalfactors,includingmortgageinterestrates,
inflation, and market indices such as the Santiago Stock Exchange IPSA. This research
not only challenges conventional wisdom regarding the primacy of land prices in hous-
ingmarketdynamicsbutalsooffersvaluableinsightsintothemultifacetednatureofreal
estateeconomicsinSantiago. Byunravelingthelimitedcausalitybetweenlandandhous-
ingprices,thisstudycontributesacriticalperspectivetotheongoingdiscourseonurban
developmentandhousingpolicyinChile. Itunderscorestheimperativeforpolicymakers
toadoptamoreholisticapproach,consideringabroaderspectrumofeconomicvariables
inaddressingthehousingaffordabilitycrisisandfosteringsustainableurbangrowth.
Highlightsforpublicadministration,managementandplanning:
• Land value has traditionally been considered a fundamental variable in housing
prices;however,theevidenceprovidedarguesthatthisconditionisnotunequivo-
cal.
• Itiscrucialformacroeconomicpolicymakerstoconsiderthatinflationcontrolmea-
suresimpacthousingprices.
• Theperformanceofstocksinlocalstockmarketshasastatisticallysignificantim-
pactonhousingprices,creatingroomtoincorporatefinancializationasaproblem
tobeaddressedthroughpublicpolicy.
• The mortgage rate is a determining factor in ensuring housing affordability,
forwhichcentralbankscantakemeasuresaimedatimprovinghousingtenurese-
curitythroughdifferentiatedmonetarypolicyoptionsbyproducts.
1 Introduction exacerbatedbythepresenceofastructuralhousing
deficit, which since 1998 has remained at around
In Chile, there has been an increase in hous- 500,000 households that still do not have access
ing prices, which has been declared unaffordable to quality housing with secure tenure (Hidalgo-
forthemajority(CNN2019;Vergara-Perucich2021; Dattwyler et al. 2017; Vergara-Perucich 2021). Re-
Vergara-Perucich1 &Aguirre-Nunez2020). Thisis cently, the housing access crisis has been accom-
150 ©JanEvangelistaPurkyněUniversityinÚstínadLabem

### Page 2

GeoScape18(2)—2024: 150—0 doi: 10.2478/geosc-2024-0011 Availableonlineatcontent.sciendo.com
panied by a drastic increase in informal settle- era 2016; CChC 2015; Correa et al. 2022; Encinas
ments in Chile’s major cities (Flores 2018; TECHO et al. 2016, 2019). Other approaches, meanwhile,
2021, 2023-03-14). According to the national sur- focustheirattentiononmarketflawsandstateomis-
vey on informal settlements conducted by the Min- sions,leavingtheproductionandallocationofhous-
istry of Housing and Urbanism, many households ing to economic power, mainly occupied by actors
decide to leave the formal city for economic rea- with financial purposes (Hidalgo-Dattwyler et al.
sons, with housing prices being the triggering fac- 2017; Hidalgo 2011; Janoschka & Hidalgo 2014).
tor(Flores2016;MINVU2020;Vergara-Perucich & These arguments align with other econometric ap-
Boano2019). Regardinghousingprices,specialized proachesthatfocusonpurelyfinancialfactors,asso-
literature has indicated that land prices are a key ciated with banking entities through interest rates
factor in explaining such formation (CNDU 2015; or even with the participation of real estate com-
Encinas et al. 2016; Forray & Castillo 2014; Saba- panies in the stock market (Silva & Vio 2015;
tini 2000; Sabatini et al. 2017); however, the ev- Vergara-Perucich 2022a,b). Unlike existing studies
idence used to argue this stance does not come for the case of Chile, this article shares the results
fromstudiesexploringcausalrelationshipsbetween of a dynamic causality analysis between housing
variables. Aiming to contribute to understanding pricesandlandprices,addingothercontrolandver-
the reasons behind the increase in housing prices ification variables that emerge from the literature.
and to complement the literature, this study ana- The Granger causality study applied to the rela-
lyzes the causal relationship in the Granger sense tionshipbetweenlandvalueandrealestatemarket
between land prices and housing prices in Greater in Chile has not yet been published, and therefore
Santiago, where nearly half of Chile’s population theresultspresentedareofgreatvalueforaheated
lives. discussion in that nation. The main finding is
In the case of Chile, different efforts have been im- that the causal relationship between land prices
plemented to try to explain the economic rationale andhousingpricesisnotassignificantasindicated
in the formation of housing prices. In this regard, in much of the literature, which implies that new
the technique generally used to explore housing approaches should be developed to better under-
prices is based on ordinary least squares regres- stand the fundamentals of housing prices in Chile,
sions with the hedonic pricing method. From its includinghousingpoliciesthatincorporatethisfind-
application, in 1992 it was identified that socioe- ingintotheirdesign.
conomic homogeneity and housing density in each
sector are good explanatory factors for housing
2 Materials and methods
pricesinChile(Figueroa &Lever1992). However,
this study is based on a market study for a real-
ity very different from the one that eventually set- The source of the data is the daily transaction
tled in 2001, when, through the reform of the cap- records identified at the Santiago Real Estate Reg-
ital market, new investment actors began to par- istrar, collected by Inciti SpA. These data were ac-
ticipate in the production and marketing of hous- quired for this research in July 2019. In total,
ing,especiallyreferringtofinancialinstitutions,in- the analysis is based on 556,400 transactions with
surance companies, and investment groups (Cat- daily records between March 2008 and Septem-
taneo Pineda 2011). One of the explanatory vari- ber 2019. The records show differences by ad-
ables that recurs in different studies is the im- dress, commune, typology, buyers, sellers, and ma-
portance of land in forming housing prices, both terial quality of the houses when applicable. Due
in terms of location and the land’s own price. That tothehighfrequencyofdata,itwasdecidedtocon-
is, a neighborhood with good attributes and good struct weekly time series with moving averages
land value can project the price of housing (Par- every three weeks as suggested by James Hamil-
rado et al. 2009; Quiroga 2013; Sagner 2010). ton to smooth time series (Hamilton 2018). The
The weight of land on housing prices has even unit of measure is the value of transactions ex-
been indicated in legislative projects as a key fac- pressed in UF/m2. In Chile, the UF or Unidad
tor to help make housing more affordable (Ban- de Fomento is an inflation-indexed unit, which al-
nen et al. 2019; MINVU 2018). Both for its price lows for the comparison of values by eliminating
and for its location value or even for the actors the noise that the Consumer Price Index (CPI)
participating in the land market, the literature might introduce in such measurements. Nonethe-
onthecaseofChilegivesprominencetolandprice less, as indicated later, to achieve the stationar-
when it comes to seeking explanations for high ity of the variables, some transformations are ap-
housing prices (Aguirre-Núnez et al. 2020; Bagn- plied. In summary, time series were constructed
with470observationseach,withweeklyfrequency
©JanEvangelistaPurkyněUniversityinÚstínadLabem 151

### Page 3

Availableonlineatcontent.sciendo.com GeoScape18(2)—2024: 150—0 doi: 10.2478/geosc-2024-0011
Table1Descriptivestatistics
Mean Median Min Max Std. Dev.
Landvalue(UF/m2) 15.5850 13.7150 6.6626 110.4900 9.1129
Houseprices(UF/m2) 28.3620 27.6290 11.9300 45.7880 5.6430
Apartmentprices(UF/m2) 71.5320 63.6220 35.1580 172.3400 25.8950
IPSA(Bluechipindex) 3.6414 3.5000 1.1667 5.2500 1.0077
Cashflow 2045300 2161000 1258200 2762400 486040
Inflation 0.0006 0.0005 −0.0366 0.0394 0.0032
Mortgageinterestrate 3.8484 3.7762 2.5300 4.5409 0.4577
andsmoothedbyathree-weekmovingaverage. The astheprimaryfinancingmechanismforpurchasing
descriptive statistics of the included variables can housinginChile,andtheIPSA,toreviewtheimpact
bereviewedinTable1. of the stock market on housing prices, were added
In this data source, different searches were con- as explanatory variables. The same transformation
ducted to construct the time series. First, an ag- toweeklyvaluessmoothedbyathree-pointmoving
gregated search was made for the entire Greater averagewasappliedtothedailyseries.
Santiago area covering prices and transactions Upon an initial review of the variables (Fig. 1),
for apartments, houses, lots, parcels, and indus- itwasobservedthattheywerenotstationary,lead-
tries. For the purposes of this study, it was cru- ing to the application of a differencing transforma-
cialtohavewhatcouldbeinterpretedaslandprice. tion for each variable to create a time series with
Greater Santiago is a highly urbanized territory, observations suitable for accurate analysis, which
meaning the land that real estate developers of- specifically requires the variables to be analyzed
ten pay for corresponds to houses and not nec- in their stationary form. As a result of the trans-
essarily to lots or parcels. They also acquire in- formation(Fig. 2),theAugmentedDicky-Fullertest
dustries. For this reason, the data were cleaned wasruntocheckforstationarity,andtheresultwas
in this order. Only properties with more than 300 optimal,asindicatedinTable2.
m2 of land and that were also purchased by com-
panies were considered for evaluating the land
price, as key filters. To avoid repetition of rela- Table2AugmentedDicky-FullerTestbasedonAkaike
criterionforstationaritytest
tionshipsandpreventcollinearity,housesthatwere
included in the land price sampling were then ex-
cluded from the house price analysis database. On Variable p-value
the other hand, all values are expressed in UF/m2, Landvalue(UF/m2) 4.914x10-15
both for the land value and for the data related Houseprices(UF/m2) 2.267x10-9
to housing transaction prices (specifically houses Apartmentprices(UF/m2) 2.171x10-7
orapartments). TheuseofUFasareferencevalue IPSA(Bluechipindex) 7.184x10-21
allows the price to be comparable over time, since Cashflow 0.0003532
in Chile, the UF is an inflation-indexed monetary Inflation 4.725x-8
unit that is adjusted daily, meaning variations re- Mortgageinterestrate 0.000723
flect direct price changes over time and not price-
inflation.
To decide which variables to incorporate into With the assurance of working with stationary
the model, the process began with basic ones variables, the number of lags needed to evaluate
to check if the land price influences the housing intheGrangercausalitymodelforeachvariablewas
price, namely, land price, house prices, and apart- reviewed, according to the Akaike, Hannan-Quinn,
ment prices. Then, based on a literature re- and Schwarz criteria. Initially, 26 lags were ap-
view, other control variables were included to test pliedastheresultofthehighestamountaccording
whether the housing price is more causally influ- to the Akaike criterion, however, the initial explo-
enced by variables other than land price. Using rationofthejointmodelindicatedthattheCashflow
dailyfrequencyinformationavailablefromtheCen- was not statistically significant, and then 19 lags
tral Bank of Chile, inflation, monetary liquidity were chosen, as indicated by the Akaike criterion
as an indication that wages and cash flow influ- for the mortgage interest rate, expressed in Table
ence housing prices, the mortgage interest rate 3.
152 ©JanEvangelistaPurkyněUniversityinÚstínadLabem

### Page 4

GeoScape18(2)—2024: 150—0 doi: 10.2478/geosc-2024-0011 Availableonlineatcontent.sciendo.com
Fig.1Variableswithouttransformation
Fig.2Variablesaftertransformation
©JanEvangelistaPurkyněUniversityinÚstínadLabem 153

### Page 5

Availableonlineatcontent.sciendo.com GeoScape18(2)—2024: 150—0 doi: 10.2478/geosc-2024-0011
Table3OrderselectionbyAkaike’sCriterion(AIC), ThemodelwasoriginallyproposedbyCliveGranger
Hannan-QuinnCriterion(HQ),andSchwarzCriterion in 1969, who sought to deepen the analysis
(SC) of regression that only establishes relationships
with causal possibilities (Granger 1969). How-
Mortgage ever, despite its name, it has been indicated
Crite- Land House Dept. Infla- Cash
rion value prices prices IPSA tion flow Int. that the Granger causality test is not directly
Rate
amodelthatclearlyidentifiescausalitybetweentwo
variables, but rather allows predicting the varia-
15 9 15 10 3 26 19
AIC(n) tionsofonevariablefromtheinformationprovided
HQ(n) 12 7 8 9 3 20 12
byanothervariable(Bahmani-Oskooee &Wu2018;
SC(n) 7 7 8 8 2 13 8
Emirmahmutoglu et al. 2016; Gao et al. 2021). Ac-
cording to Hamilton, the Granger causality model
identifies whether one variable A predicts another
Withthedatareviewedfollowingthementionedcri-
B,thatis,whetheritestablishesamechanismtover-
teria, a second set of data was made, separating
ifytheprecedenceofonevariableoveranother(Gu-
land and housing prices by sectors of Greater San-
jarati & Porter 2009; Trapletti & Hornik 2022).
tiago. Santiago city is highly segregated by pur-
For the purposes of this study, the analysis seeks
chasing power (Agostini et al. 2016; Borsdorf et al.
toverifythepotentialcausalrelationshipsbetween
2016; Sabatini et al. 2017; Truffello & Hidalgo
housing prices and land prices, as has been pro-
2015). This observation is relevant since the city
posed in the literature on the case of Chile. Addi-
can be classified according to these segregation
tionally,toaddrichnesstothestudy,othervariables
factors. For this study, the criterion of separation
are evaluated to explain housing prices, to identify
is taken from the proposal by Luis Fuentes et al.,
whetherlandpriceiscomparativelymoreimportant
whosuggeststheexistenceofaNorth,South,West,
than other variables in relation to projecting varia-
East,South-East,South-West,andCenter-EastSan-
tionsonhousingprices.
tiago(Fuentesetal.2017). Fromtheavailabledata,
As a summary, this research embarked on an in-
a second table of land and housing price informa-
depth exploration of the real estate dynamics
tion was created with divisions for North, South,
inGreaterSantiago,leveragingtransactionrecords
Center-East, and West. There was not enough data
from the Santiago Real Estate Registrar. The pri-
for South-East and South-West in this evaluation,
mary objective was to discern the intricate rela-
sotheywereexcluded. Table4presentsthedescrip-
tionship between land prices and housing prices,
tivestatisticsforeachsector.
accounting for the influence of key economic indi-
Forthisstatisticalanalysis,aGrangercausalitytest
cators such as inflation, monetary liquidity, mort-
isapplied,whichisawidelyusedstrategyinecono-
gageinterestrates,andstockmarketperformance.
metrics to analyze dynamic relationships between
The methodological approach involved construct-
variables(Altuzarra &Esteban2011). Thistestem-
ing weekly time series from the raw daily transac-
pirically evaluates the behavior of one time series
tion data, employing a three-week moving average
in relation to another time series. The mathemat-
to smooth out fluctuations. These time series were
ical definition of the Granger causality test states
then meticulously transformed to ensure stationar-
that a variable X is said to Granger cause another
ity, a prerequisite for accurate analysis. The core
variableYifYcanbebetterpredictedfromthepast
of the statistical analysis was the Granger causal-
of X and Y together than from the past of Y alone
ity test, employed to investigate potential cause-
(Chee-Yin & Hock-Eam 2014). In other words,
and-effect relationships between housing prices
ifthelagsofavariableXtcanpredictfuturevalues
and land prices, as well as other control variables.
of a variable Yt, while including lags of both vari-
Theanalysisalsodelvedintothespatialdimension,
ables, then Xt Granger causes Yt (Fernandois et al.
examining these relationships across different sec-
2020). In the results of the Granger tests, the F-
tors of Greater Santiago, acknowledging the city’s
statistics and p-value will be presented. To iden-
socio-economic segregation. In essence, this study
tify a causal relationship, it is required that the p-
sought to provide a comprehensive understanding
valuebelessthan0.05,whiletheF-statisticsshould
ofthefactorsdrivinghousingpricesinGreaterSan-
be greater than the p-value. For the Granger test
tiago, with a particular focus on the role of land
to be applied, two stationary time series are stud-
prices.
ied in pairs to check if the lags of one variable
X can predict the time variations of the other Y.
The null hypothesis states that X does not cause Y
intheGrangersense.
154 ©JanEvangelistaPurkyněUniversityinÚstínadLabem

### Page 6

GeoScape18(2)—2024: 150—0 doi: 10.2478/geosc-2024-0011 Availableonlineatcontent.sciendo.com
Table4Descriptivestatisticsoflandpriceandhousingpriceforeachsub-sectorofGreaterSantiago
Mean Median Min Max Std. Dev.
Centre-east Landvalue 26.34 22.99 8.25 211.97 17.54
Housingprices 39.66 39.04 26.29 57.72 7.13
North Landvalue 8.97 7.61 2.61 46.99 5.88
Housingprices 28.68 27.29 19.63 47.97 4.63
West Landvalue 7.65 6.74 2.31 42.63 4.05
Housingprices 28.97 28.32 18.74 47.89 5.77
South Landvalue 9.56 8.15 3.10 30.74 4.41
Housingprices 31.61 30.45 21.57 45.22 5.67
Table5Grangercausalitybetweenlandprice,houseprice,andapartmentprice
NullHypothesis Observations F-Statistic Probability Lag(s)
Apartmentprice(-1)doesnotGrangercauseHouseprice(-1) 454 1.87 0.0189 17
Apartmentprice(-1)doesnotGrangercauseHouseprice(-1) 456 1.84 0.0275 15
Apartmentprice(-1)doesnotGrangercauseHouseprice(-1) 455 1.72 0.0409 16
Landprice(-1)doesnotGrangercauseApartmentprice(-1) 465 2.25 0.0373 6
Landprice(-1)doesnotGrangercauseApartmentprice(-1) 467 2.42 0.0475 4
3 Results wouldonlyapplytoaspecifictypeofhousing(apart-
ments)intwolags,oneat6weeksandanotherat4
weeks.
To organize the Granger causality tests, two ap-
Table6presentstheresultsofthepairwisecausality
proaches were taken: one separating relevant ur-
test between land prices, house prices, and apart-
ban zones (center-east, north, south, west) and an-
ment prices, adding possible explanatory variables
otherdistinguishingbetweentypesofhousingunits,
in this analysis such as the relationship with mort-
such as houses and apartments. While the first
gage interest rates, inflation, and the IPSA from
strategy aimed to determine if the causal relation-
the Santiago Stock Exchange. From this analysis,
ship between land price and housing price varies
isolating only the factors that present a Granger
depending on the city sector, the second strategy
causality relationship with housing prices, among
sought to evaluate the causality between house
theexploredvariables,onlyhousesshowcausalin-
or apartment prices and to compare these causal
fluence from inflation, mortgage rates, and IPSA
influences with other variables that literature has
for the 19 lags studied. These results are striking
indicated as relevant for defining housing prices
andcertainlycallintoquestionpartoftheliterature
inChile.
that attributes a leading value to land price in ex-
When examining causal relationships considering
plainingtheformationofhousingprices.
onlyhousingandlandpriceswith19lags,veryspe-
Santiago is a highly segregated city, with clear
cific causal relationships are observed in relation
socio-spatial differences between districts (Correa
totheothervariablesinthestudy. Table5indicates
et al. 2022, 2023; Ulloa-Leon et al. 2023). As part
only the Granger causality relationships between
of this exploration, it was examined whether sepa-
land prices, house prices, and apartment prices.
rating the city by socioeconomically homogeneous
Among the main findings, there is no sustained
zones could affect the causal relationships. The re-
causal relationship between land price and house
sultsofthisexercisearepresentedinTable7,where
price in time. However, a causal relationship does
it is checked whether the land price has causal re-
appear between land price and apartment prices
lationships on the housing price in each of the re-
forlagsof6and4weekswithstatisticalsignificance
viewed sectors. Again, the result for 19 lags per
justabove5%. Ontheotherhand,thereisacausal
pair is much scarcer than expected. The impact
relationshipfromapartmentpricestohouseprices.
of land price variation on housing price only oc-
Thisinitialfindingindicatestheneedtofurthercom-
curs in the first lag. The housing price in the west-
plexify the analysis of the possible causal relation-
ern zone of the city has a significant causal re-
ship between land price and housing price, which
©JanEvangelistaPurkyněUniversityinÚstínadLabem 155

### Page 7

Availableonlineatcontent.sciendo.com GeoScape18(2)—2024: 150—0 doi: 10.2478/geosc-2024-0011
Table6Grangercausalitybetweenlandprice,houseprice,andapartmentprice
Nullhypothesis: Obs F-Stat. p-value Lag
Inflation(-1)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 468 5.8278 0.0006 3
Inflation(-1)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 467 4.7825 0.0009 4
Inflation(-1)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 469 6.8071 0.0012 2
Inflation(-1)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 466 3.9661 0.0016 5
Inflation(-1)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 465 3.3571 0.0030 6
Inflation(-1)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 464 3.1006 0.0033 7
Inflation(-1)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 463 2.7511 0.0057 8
Inflation(-1)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 462 2.5146 0.0081 9
Inflation(-1)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 461 2.2628 0.0138 10
Inflation(-1)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 460 2.0847 0.0203 11
IPSA(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 465 3.9295 0.0017 5
IPSA(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 468 6.3416 0.0019 2
IPSA(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 466 4.2749 0.0021 4
IPSA(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 467 4.8535 0.0025 3
IPSA(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 464 3.3746 0.0029 6
IPSA(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 463 2.8454 0.0065 7
IPSA(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 462 2.5099 0.0112 8
IPSA(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 461 2.2249 0.0196 9
IPSA(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 458 2.0056 0.0224 12
MortgageRate(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 458 2.6612 0.0019 12
MortgageRate(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 459 2.7035 0.0022 11
MortgageRate(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 457 2.5161 0.0025 13
MortgageRate(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 465 3.6892 0.0028 5
MortgageRate(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 464 3.1671 0.0047 6
MortgageRate(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 463 2.9257 0.0053 7
MortgageRate(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 467 4.2743 0.0054 3
MortgageRate(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 455 2.1813 0.0064 15
MortgageRate(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 456 2.1634 0.0085 14
MortgageRate(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 454 2.0789 0.0085 16
MortgageRate(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 453 2.0371 0.0087 17
MortgageRate(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 462 2.5857 0.0091 8
MortgageRate(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 461 2.4755 0.0092 9
MortgageRate(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 460 2.2272 0.0155 10
MortgageRate(-2)doesnotcauseinthesenseofGrangeratthepriceofhouses(-1) 466 2.8957 0.0218 4
Table7GrangercausalitytesttoverifyifthelandpricebyeachsectorofGreaterSantiagoimpactsthehousingprice
NullHypothesis Obs. p-value Lag
WestLandPricedoesnotGrangercauseWestHousingPrice 469 0.0423 1
Center-EastLandPricedoesnotGrangercauseSouthHousingPrice 469 0.0492 1
SouthLandPricedoesnotGrangercauseWestHousingPrice 469 0.0164 1
lationship at the first lag with the housing price Circulating money was not statistically significant
in the west as well. It is noteworthy that other in explaining causal relationships with the housing
results cross zones of Greater Santiago: the hous- price or land price, leaving the main explanatory
ing price in the center-east has a causal relation- variables as the mortgage interest rate, inflation,
ship with housing on the south side, while the land and IPSA for the price of houses, while for apart-
price on the south side has a causal relationship ments,theirpriceiscausallyinfluencedbytheland
withthehousingpriceonthewestside. price for two lags, as previously indicated. Table 8
isasummaryofthemainfindingsofthisstudy.
156 ©JanEvangelistaPurkyněUniversityinÚstínadLabem

### Page 8

GeoScape18(2)—2024: 150—0 doi: 10.2478/geosc-2024-0011 Availableonlineatcontent.sciendo.com
Table8Summaryofresultsoftheresearch
Variable Lag(Weeks) p-value TypeofHousing Sector
4 0.0373
LandPrice-ApartmentPrice Apartments General: GreaterSantiago
6 0.0475
15 0.0189
ApartmentPrice-HousePrice 16 0.0275 Houses General: GreaterSantiago
17 0.0409
Inflation-HousePrice 2,11 0.05 Houses General: GreaterSantiago
IPSA-HousePrice 2to11 0.05 Houses General: GreaterSantiago
MortgageRate-HousePrice 3to17 0.05 Houses General: GreaterSantiago
WestLandPrice-WestHousingPrice 1 0.0423 Houses Specific: WesternSantiago
Center-EastLandPrice-SouthHousingPrice 1 0.0492 Houses Specific: CentralandSouthernSantiago
SouthLandPrice-WestHousingPrice 1 0.0164 Houses Specific: SouthernandWesternSantiago
The summarized results table highlights the main of quality of life and urban development, the value
findings from the Granger causality tests applied of land prevents the establishment of affordable
in the study. The results reveal specific causal housing for the majority, a point that is debatable
relationships between land prices, housing prices, basedontheresultsofthisstudy,wherethehousing
andothereconomicvariablesacrossdifferenthous- price,understoodinChileasthemainelementcon-
ing types and sectors within Greater Santiago. ditioning secure access to housing, does not show
Notably, land prices significantly influence apart- a direct causal relationship with land value. This
ment prices, but not so frequently in relation hadbeenpreviouslyindicatedinastudybyVergara
tohousepricesdirectly. However,apartmentprices andAguirre, whopresentedevidenceonthesignif-
do Granger cause house prices, indicating a com- icant difference between housing production costs
plex interplay between different housing market and real estate project profits, indicating that al-
segments. Moreover, inflation, stock market per- though the land value paid was a factor, the profits
formance(IPSA),andmortgageratesexhibitstrong oninvestmentwerehigherthanthisvalue(Vergara-
causal relationships with house prices, underscor- Perucich1 & Aguirre-Nunez 2020). The results
ing the importance of financial factors in hous- presented in this article indicate that while there
ing market dynamics. Spatially, the study found is a causal relationship between housing price
that the causal impact of land prices on housing and land price for apartments in Greater Santiago,
prices is sector-specific, with significant relation- thisrelationshipismuchweakerthanotherfactors
shipsidentifiedwithinthewestern,central-eastern, suchasmortgageinterestrates,IPSA,oreveninfla-
andsouthernpartsofSantiago. Thesefindingsem- tion.
phasizethemultifacetednatureofhousingpricefor- Among the causal relationships of land price
mation, suggesting that both economic and spatial onhousingprice,onlyastatisticallysignificantrela-
factorsmustbeconsideredinurbanhousingpolicy. tionshiponthepriceofapartmentsisobserved. The
interpretation of this result is that there is an ef-
fect of land on housing price when the purchased
4 Discusion land is useful for generating processes of vertical-
ization and densification in key urban areas. That
Differentliteraturecontributionshadpositthatland is, the real estate market depends on land value
price is perhaps the main factor defining housing toextractrentfromtheeconomyofscalethathigh-
prices in different contexts (Altuzarra & Esteban riseconstructionallowscomparedtohorizontalcon-
2011; Braakmann & McDonald 2020; Deng & struction. While a reference cost of high-rise hous-
Ma 2007). In the case of Chile, a national ur-
ingconstructioninSantiagois14UF/m2,thesame
ban policy of social integration was recently ap- value for horizontal housing is close to 25 UF/m2.
proved in Congress, centering its action strategies Thus, while the average price of high-rise housing
on the management of urban land as a mecha- is 71.53 and for houses is 28.36, profitability lies
nism to ensure universal access to housing. While inmakingthemostofthelandthatallowsforhigh-
this measure may yield optimal results, in its argu- rise construction, where each square meter sold
ment submitted to Congress on December 5, 2018, yields a much better investment return than hor-
itstatedthatincitysectorswithadequatestandards
©JanEvangelistaPurkyněUniversityinÚstínadLabem 157

### Page 9

Availableonlineatcontent.sciendo.com GeoScape18(2)—2024: 150—0 doi: 10.2478/geosc-2024-0011
izontal construction, allowing the company to as- stand the forces shaping housing markets. Tradi-
sumetheriskofpurchasinghigher-valueland. tionally, land-value theory has dominated discus-
Asignificantfindingofthisresearchisthattheland sions in real estate economics, positioning land
price in the western sector of the city has a causal prices as the central factor in housing price forma-
influenceonthehousingpricewithinthesamezone tion. However, this study reveals that land prices
for the first lag. This means that the land price may not play as significant a role as previously
in communes such as Pudahuel, Estación Central, thought, opening the door for further investigation
Quinta Normal, or Maipú does have a causal rela- into other economic variables. This critical chal-
tionship with the housing price. These communes lenge to established theory encourages a more nu-
haveseensignificantrealestatedevelopmentinre- anced understanding of housing market dynamics,
cent years. Other causal relationships indicate invitingresearcherstoexploretherolesoffinancial-
that the land price in the Center-East sector im- ization, macroeconomic policies, and socio-spatial
pacts the housing price in the South sector, while factors.
the same occurs with the land price in the South Thestudy’semphasisontheroleoffinancialization
sector impacting the housing price in the West in housing markets marks another significant the-
sector. This may indicate that homebuyers move oretical advancement. By empirically demonstrat-
from communes with high land prices to com- ing the impact of financial variables, such as mort-
munes where the average housing value is lower gageratesandstockmarketperformance,onhous-
(Vergara-Perucich 2022a; Vergara-Perucich et al. ing prices, this research aligns with and bolsters
2023). According to descriptive statistics, the av- the growing discourse on housing as a financial
erage housing value in the Center-East is 39.66 asset. This perspective is increasingly relevant
UF/m2,intheSouthis31.61UF/m2,andintheWest in global debates, where housing is often seen less
is 28.97 UF/m2, in a relationship that moves from asabasicneedandmoreasaninvestmentvehicle.
thehighestlandvalueintheCenter-Easttothelow- The study’s findings suggest that any comprehen-
est value in the West. While this is a valuable sivetheoryofrealestatedevelopmentmustaccount
observation, further analysis is needed to assert forthebroaderfinancialcontext,particularlyinun-
that there is a circulation of households and in- derstanding the challenges of housing affordability
vestors in this sense, seeking lower land and hous- and the implications of treating housing primarily
ingvalues. asafinancialasset.
A valuable finding is that financial variables such Moreover, the study’s analysis of spatial hetero-
asIPSAorthemortgageratehavesignificantcausal geneity across different sectors within Santiago
relationships with house prices. This could lead provides a vital contribution to real estate the-
to a more in-depth analysis of financialization pro- ory by highlighting the importance of local con-
cesses as causes of rising housing prices. The lit- text in price determination. Housing market dy-
eraturementionstheimportanceoffinancialization namicsareoftenoversimplifiedingeneralizedmod-
on access to secure housing tenure (Aalbers 2017; els that fail to account for variability across neigh-
Hidalgo Dattwyler et al. 2019; Rolnik 2012, 2013) borhoods and regions. This research underscores
and is a factor scarcely explored from the quan- theneedformorerefinedtheoreticalmodelsthatin-
titative perspective with econometric techniques corporatelocalfactors,suchasneighborhoodchar-
oncausalrelationships. Initially,thisfindingallows acteristicsandpatternsofsocio-spatialsegregation.
foradeepeningoftheseapproaches. The inclusion of these complex variables may pave
It is notable that circulating money is not a cause the way for more comprehensive policy interven-
of housing prices or land prices. This could tions tailored to the specificities of different urban
open a new line of interpretation from the fact areas. In this perspective, the use of big data may
that in the case of Chile, apparently, housing is no becomeanecessaryconsiderationforfuturestudies
longerpurchasedwithmoneybutalmostexclusively inthisfield.
with debt instruments, which would make sense Inadvocatingforaholisticapproachtohousingpol-
withthesignificantcausalrelationshiprevealedbe- icy, the study synthesizes its various contributions
tweenhousepricesandmortgagerates. into a broader call for integrated policymaking.
This research offers substantial contributions The findings suggest that focusing solely on land
to the theory of real estate development in Chile, prices is inadequate and that a comprehensive ap-
particularly by challenging the long-standing as- proach that considers a range of economic, so-
sumption that land prices are the primary determi- cial, and spatial factors is essential. This holis-
nant of housing prices. This finding has the poten- tic perspective is valuable as it encourages cross-
tial to initiate a paradigm shift in how we under- disciplinary research, bridging gaps between ur-
158 ©JanEvangelistaPurkyněUniversityinÚstínadLabem

### Page 10

GeoScape18(2)—2024: 150—0 doi: 10.2478/geosc-2024-0011 Availableonlineatcontent.sciendo.com
ban planning, sociology, and finance, and pushing propertypricesandimprovinghousingaffordability.
forpoliciesthatarebetteralignedwiththecomplex Nevertheless, the question on how to reduce hous-
realitiesofhousingmarkets. ingpricesremainsopentocontributions.
Additionally, while the study is centered on Santi- Furthermore,itseemspertinenttosuggestthatre-
ago, Chile, its findings have broader implications search should advance towards the study of causal
that could resonate globally. Drawing parallels relationshipsthatcanbeidentifiedataspatiallevel.
withsimilardynamicsinothercitiescouldenhance That is, combining Granger causality models, VAR
the theoretical contributions of this research, en- withgeostatisticaltechniquessuchasGWRorspa-
couraging comparative studies and the develop- tialstructuralequations, amongotheralternatives.
ment of more universally applicable theories. This Inthistypeofanalysis,thecityasacomplexanddy-
global contextualization would not only broaden namic entity can contribute other explanatory fac-
the impact of the study but also contribute tors that help to enhance the analysis presented
to a deeper understanding of how various global here.
andlocalfactorsinteractindifferentcontexts. Theseresultsfuelthediscussionontheimportance
of regulating the land market without examining
the fundamentals of housing prices. This discus-
5 Conclusions
sion has been part of the public agenda in Chile
in recent years; however, causality or predictive
This article has examined the causal relation- studies on the matter are not abundant and cer-
ships between land prices and housing prices tainly are not even cited by decision-makers when
in Greater Santiago, applying a Granger causality formulating public policies. This disconnection be-
test on weekly time series from 2008 to 2019. It tween evidence and public policy can lead to mis-
has been determined that the causal relationship takesthatwilltakeyearstocorrect. Whilethisarti-
between land and housing prices is not as signif- cledoesnotclaimtopresentabsolutetruthsorpro-
icant as other explored variables, such as mort- pose a general theory, the considerations that can
gage rates or the IPSA. This finding is valuable, arisefromtheseresultsdeservetobepartofthedis-
as such a study had not been conducted in Chile cussions on the housing access crisis that Chile is
before, and decision-makers had been attributing experiencing.
more weight to the relationship between housing
pricesandlandpricesthanithas. Onthecontrary,
References
theresultscompelthesedecision-makerstoexplore
other causal relationships, such as financial ones,
Aalbers MB, (2017), Corporate Financialization. In: Inter-
to improve the understanding of the high housing
national Encyclopedia of Geography: People, the Earth,
pricesinChile.
Environment and Technology, pp. 1–11. doi: 10.1002/
Given the findings of this study, it is evident 9781118786352.wbieg0598.
that the current regulatory approach, which fo-
AgostiniCA,HojmanD,RománA,ValenzuelaL,(2016), Segre-
cuses primarily on the management of urban land
gación residencial de ingresos en el Gran. Una estimación
through social integration policies, is insufficient robusta.
to address the complexities of housing affordabil-
Aguirre-Núnez C, Marmolejo-Duarte C, Vergara-Perucich JF,
ity in Chile. The government could have an ac-
(2020), Centralidad y subcentralidad en ciudades con baja
tive role to be more effective by broadening its fo-
regulación,elcasoAntofagastaylaSerenaenChile.XIIICTV
cusbeyondlandregulationtoaddresskeyfinancial Barcelona.
variablesthatsignificantlyinfluencehousingprices.
AltuzarraA,EstebanM,(2011),Landpricesandhousingprices:
Specifically, policies should be developed to com-
The case of Spain. JOURNAL OF HOUSING AND THE
plexify how mortgage interest rates are regulated BUILTENVIRONMENT(4,26,(ue4):397–409. doi: 10.1007/
and thus control housing price inflation, as these s10901-011-9235-8.
factorshavebeenshowntohaveamoresubstantial
BagneraP,(2016), Elderechoalaciudadenlaproduccióndel
impactonhousingcoststhanlandpricesalone. Ad-
suelourbano. 1–17.
ditionally, the government should consider the role
of the Santiago Stock Exchange (IPSA) in housing Bahmani-OskooeeM,WuTP,(2018),Housingpricesandrealef-
fectiveexchangeratesin18OECDcountries:Abootstrapmul-
price dynamics, which suggests that financial mar-
tivariatepanelGrangercausality. In: ECONOMICANALYSIS
kets play a critical role in real estate affordability. AND POLICY, volume 60, pp. 119–126. doi: 10.1016/j.eap.
Byincorporatingtheseeconomicfactorsintoamore 2018.09.005. ELSEVIER.
comprehensivehousingpolicy, thegovernmentcan
Bannen P, Rojas C, Ruiz-tagle J, Vicuna M, (2019), Observa-
create a more effective framework for stabilizing
ciones y propuestas al proyecto de ley de integración social
y urbana. Instituto de Estudios Urbanos y Territoriales
©JanEvangelistaPurkyněUniversityinÚstínadLabem 159

### Page 11

Availableonlineatcontent.sciendo.com GeoScape18(2)—2024: 150—0 doi: 10.2478/geosc-2024-0011
- Pontificia Universidad Católica de Chile. http://estu- Encinas F, Marmolejo C, Aguirre C, (2016), El impacto de los
diosurbanos.uc.cl/images/publicaciones/documentos-de- proyectosinmobiliariosysusatributosdesustentabilidadso-
trabajo/Doc_trabajo_ley_integracion.pdf. breelvalordelsuelo: ?causaoconsecuencia? Dosestudios
decasosparaSantiagodeChile.RevistaHábitatSustentable,
Borsdorf A, Hildalgo R, Vidal-Koppmann S, (2016), Social seg- 6,(2).
regation and gated communities in Santiago de Chile and
EncinasF,AguirreC,TruffelloR,HidalgoR,(2019),Speculation,
BuenosAires.Acomparison.HabitatInternational,54:18–27.
land rent and the neoliberal city. Or why free market is not
doi: 10.1016/j.habitatint.2015.11.033.
enough? RevistaARQ,1,(102).
BraakmannN,McDonaldS,(2020),Housingsubsidiesandprop- FernandoisA,MedelCA,FernandoisA,MedelCA,(2020),Geopo-
erty prices: Evidence from England. REGIONAL SCIENCE liticaltensions,opecnews,andtheoilprice:AGrangercausal-
AND URBAN ECONOMICS. doi: 10.1016/j.regsciurbeco. ity analysis. Revista de Análisis Económico, 35, (2). doi:
2018.06.002. 10.4067/S0718-88702020000200057.
CattaneoPinedaRA,(2011),RealEstateInvestmentTrustsand Figueroa E, Lever G, (1992), Determinantes del precio de la
privatehousingproductioninSantiagodeChile: Anewstep viviendaenSantiago: Unaestimaciónhedónica. Estudiosde
towardsthefinantiarizationofthecity? EURE-REVISTALATI- Economía,19,(1).
NOAMERICANADEESTUDIOSURBANOREGIONALES(112,
37,(ue112):5–22. FloresP,(2016),LosCampamentosenelChiledeHoy. Revista
CIS,1,(20).http://www.techo.org/paises/chile/wp-content/up-
loads/2016/12/CIS21-Editorial.pdf.
CChC,(2015). InformeMACh.CChC,137.
Flores P, (2018), Campamentos, la cara visible de la ex-
Chee-Yin Y, Hock-Eam L, (2014), The Opportune Time to In- clusión. In: Radio Universidad de Chile. http://ra-
vestInResidentialProperties—Engle-GrangerCointegration dio.uchile.cl/2017/10/23/aumento-de-campamentos-la-cara-
Test and Granger causality Test Approach. In: Ibrahim H, visible-de-la-exclusion-habitacional/.
Zulkepli J, Aziz N, Ahmad N, Rahman SA, (eds.) INTERNA-
TIONALCONFERENCEONQUANTITATIVESCIENCESAND ForrayR,CastilloMJ,(2014),Lavivienda,unproblemadeacceso
ITS APPLICATIONS (ICOQSIA 2014, volume 1635. AMER aLsuelo. Arq,86:48–57.
INSTPHYSICS,pp.948–955. doi: 10.1063/1.4903696.
FuentesL,Mac-ClureO,MoyaC,OlivosC,(2017),Santiagode
Chile: ?ciudaddeciudades? Desigualdadessocialesenzonas
CNDU, (2015), Política Nacional de Desarrollo Urbano. Min-
de mercado laboral local. Revista de la CEPAL, 1, (121):
isterio de Vivienda y Urbanismo. http://cndu.gob.cl/wp-
93–109. https://hdl.handle.net/11362/41146.
content/uploads/2014/10/L4-Politica-Nacional-Urbana.pdf.
GaoR,ZhaoY,ZhangB,(2021),Balticdryindexandglobaleco-
CNN, (2019), Presidente del CChC advierte “crisis social” por nomicpolicyuncertainty: Evidencefromthelinearandnon-
difícil acceso a viviendas: “Se está convirtiendo en un bien linearGrangercausalitytests.AppliedEconomicsLetters,0,
inalcanzable”. In: CNN Chile, pp. 1–3. https://www.cn- (0):0. doi: 10.1080/13504851.2021.1985720.
nchile.com/economia/presidente-del-cchc-advierte-crisis-
social-por-dificil-acceso -a-viviendas-se-esta-convirtiendo-en- Granger CW, (1969), Investigating Causal Relations by Econo-
un-bien-inalcanzable_20190510/. metricModelsandCross-spectralMethods.Econometrica,37,
(3). doi: 10.2307/1912791.
Correa J, Vergara-Perucich F, Truffello R, Aguirre-Nunez C,
(2022),DéficitdelaviviendaenelGranSantiago.Evidencia GujaratiDN,PorterDC,(2009),BasicofEconometric.In:Econo-
empírica sobre conflictos y argumentos para repensar la metrics,fifthedition.
planificaciónmetropolitana.URBE-REVISTABRASILEIRADE
Hamilton JD, (2018), Why you should never use the Hodrick-
GESTAOURBANA,14,(1).https://www.researchgate.net/pub-
Prescottfilter. ReviewofEconomicsandStatistics,100,(5).
lication/366311334_Deficit_de_la_vivienda_en_el_Gran_San-
doi: 10.1162/rest_a_00706.
tiago_Evidencia_empirica_sobre_conflictos_y_argumen-
tos_para_repensar_la_planificacion_metropolitana. HidalgoR,(2011).
Correa J, Ulloa-Leon F, Vergara-Perucich F, Aguirre-Nunez C, Hidalgo-Dattwyler R, Alvarado-Peterson V, Santana-Rivas D,
TruffelloR,(2023), Infrastructuralinequality: Exploringthe (2017), La espacialidad neoliberal de la producción de
emergenceofdigitalclassesintheMetropolitanAreaofSan- vivienda social en las áreas metropolitanas de Valparaíso y
tiago, Chile. Bulletin of Geography. Socio-Economic Series, Santiago (1990-2014): ?hacia la construcción idelógica de
62:107–122. doi: 10.12775/bgss-2023-0037. un rostro humano? Cadernos Metrópole, 19, (39):39. doi:
10.1590/2236-9996.2017-3907.
DengC,MaY,(2007),PricediscoverybetweenChineseland&
HidalgoDattwylerR,SantanaRivasLD,LinkF,(2019),Newne-
housing markets. In: Wang Y, Sun M, Shen QP, (eds.) PRO-
oliberalpublichousingpolicies:Betweencentralitydiscourse
CEEDINGS OF 2007 INTERNATIONAL CONFERENCE ON
and peripheralization practices in Santiago, Chile. HOUS-
CONSTRUCTION & REAL ESTATE MANAGEMENT, VOLS 1
INGSTUDIES(3,34,(ue3):489–518.doi:10.1080/02673037.
AND 2. CHINA ARCHITECTURE & BUILDING PRESS, pp.
2018.1458287.
1576–1578.
JanoschkaM,HidalgoR,(2014), LaCiudadNeoliberal: Estímu-
Emirmahmutoglu F, Balcilar M, Apergis N, Simo-Kengne BD, losdereflexióncrítica.EditorialUniversitaria.
Chang T, Gupta R, (2016), Causal Relationship between As-
setPricesandOutputintheUnitedStates:Evidencefromthe MINVU, (2018), Presidente Pinera firma proyecto de ley
State-LevelPanelGrangerCausalityTest. REGIONALSTUD- de Integración Social y Urbana que crea el Ministerio
IES(10,50,(ue10):1728–1741.doi:10.1080/00343404.2015. de Ciudad y Vivienda. MINVU. http://www.minvu.cl/open-
1055462. site_det_20181203172228.aspx.
160 ©JanEvangelistaPurkyněUniversityinÚstínadLabem

### Page 12

GeoScape18(2)—2024: 150—0 doi: 10.2478/geosc-2024-0011 Availableonlineatcontent.sciendo.com
MINVU, (2020), Minuta Boletin Bol.N° 12.288-14 Integracion Trapletti A, Hornik K, (2022), tseries: Time Series Analysis
Social.MINVU. andComputationalFinance.https://CRAN.R-project.org/pack-
age=tseries.
ParradoE,CoxP,FuenzalidaM,(2009),EvoluciondelosPrecios
deViviendasenChile. TruffelloR,HidalgoR,(2015),Polycentrisminthemetropolitan
area of Santiago de Chile: Business restructuring, mobility
QuirogaBF,(2013),HedonicEstimationwithUnobservedChar-
and sub-center typing [Policentrismo en el Área Metropoli-
acteristics:AnApplicationtotheHousingMarketinSantiago,
tanadeSantiagodeChile:Reestructuracióncomercial,movil-
Chile. SSRNElectronicJournal. doi: 10.2139/ssrn.2356019.
idad y tipificación de subcentros. Eure, 41, (122). doi:
10.4067/s0250-71612015000100003.
Rolnik R, (2012), The right to adequate housing. Naciones
Unidas.
Ulloa-Leon F, Correa-Parra J, Vergara-Perucich F, Cancino-
Rolnik R, (2013), Late Neoliberalism: The Financialization of ContrerasF,Aguirre-NunezC,(2023),15-MinuteCity”andEl-
Homeownership and Housing Rights. International Journal derlyPeople: ThinkingaboutHealthyCities. SmartCities,6,
of Urban and Regional Research, 37, (3). doi: 10.1111/ (2). doi: 10.3390/smartcities6020050.
1468-2427.12062.
Vergara-PerucichF,(2022a),Socio-economicdriversofincreas-
SabatiniF,(2000),ReformadelosmercadosdesueloenSanti- ingnumberofslumsinChile. GeoScape,16,(1):55–64.
ago, Chile: Efectossobrelospreciosdelatierraylasegre-
gaciónresidencial. EURE(Santiago,26,(77). doi: 10.4067/ Vergara-PerucichF,BoanoC,(2019),Elprecioporelderechoa
S0250-71612000007700003. laciudadanteelaugedecampamentosenChile. AUS,2019,
(26):26. doi: 10.4206/aus.2019.n26-09.
SabatiniF,RasseA,CáceresG,RoblesMS,TrebilcockMP,(2017),
Promotores inmobiliarios, gentrificación y segregación resi- Vergara-PerucichJF,(2021),Pricesandfinancialization: Empir-
dencialensantiagodeChile.RevistaMexicanadeSociologia. ical evidence of housing market in Greater Santiago [Pre-
doi: 10.22201/iis.01882503p.2017.2.57662. cios y financierización: Evidencia empírica en mercado de
laviviendadelGranSantiago. RevistaINVI,36, (103). doi:
Sagner A, (2010), Determinantes del Precio de Viviendas en
10.4067/S0718-83582021000300137.
Chile.
Vergara-PerucichJF,(2022b),IsThereFinancializationofHous-
Silva CG, Vio C, (2015), Los precios de vivienda y factores
ing Prices? Empirical Evidence from Santiago de Chile.
macroeconÓmicos: ElcasodeChile.EconomiaChilena.
Economies,10,(6). doi: 10.3390/economies10060125.
TECHO, (2021), Catastro Nacional de Campamentos
2020-2021 de TECHO-Chile: Histórica alza de fa- Vergara-Perucich JF, Aguirre-Nunez C, Marmolejo-Duarte C,
milias viviendo en campamentos - TECHO Chile. (2023),Investificationenelmercadodelavivienda: Estudio
https://cl.techo.org/blog/2021/04/05/catastro-nacional-de- exploratorioenSantiagodeChile. RevistaUrbano,26,(48):
campamentos-2020-2021-de-techo-chile-historica-alza-de- 56–67. doi: 10.22320/07183607.2023.26.48.05.
familias-viviendo-en-campamentos/.
Vergara-Perucich1JF,Aguirre-NunezC,(2020), Housingprices
TECHO,(2023-03-14),AUMENTANACERCADE114MILLAS in unregulated markets: Study on verticalised dwellings
FAMILIASQUEVIVENENCAMPAMENTOS-TECHOChile. in Santiago de Chile. Buildings, 10, (1). doi: 10.3390/
techo.org. buildings10010006.
©JanEvangelistaPurkyněUniversityinÚstínadLabem 161

