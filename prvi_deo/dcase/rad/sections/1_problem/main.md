# 1. Uvod

## 1.1 Definicija problema

Automatsko opisivanje audio-sadržaja je problem generalnog opisivanja audio sadržaja tekstom. To je inter-modalni zadatak prevođenja, gde cilj nije vršiti direktno speech-to-text tj odrediti šta je tačno rečeno na snimku, već je cilj odrediti deskripciju zvučnog signala. Na primer kod razgovora dvoje ljudi, cilj nije odrediti šta je tačno rečeno već dati opis nalik "dvoje ljudi pričaju u maloj prostoriji". Po definiciji problema sa DCASE 2024, model treba biti u stanju da prepozna kako i generalne koncepte (npr. prigušen zvuk) tako i fizičke osobine okoline (zvuk velikog automobila) kao i high-level koncepte (sat je zvonio tri puta).

\begin{figure}[h]
\centering
\includegraphics[width=6cm]{figures/aac.png}
\caption{Automatsko opisivanje audio-sadržaja} 
\label{fig:aac}
\end{figure}

Po opisu problema, dozvoljeno je takmičarima da koriste eksterne skupove podataka koji su prigladni za dat problem kao i druge pre-trained modele kao što su Word2Vec, BER itd.

## 1.2 Skup podataka za evaluaciju

Za ovaj zadatak autori su za evaluaciju performanse modela izabrali Clotho V2 skup podataka, koji predstavlja proširenje originalnog skupa podataka Clotho v1 i sadrži 6972 audio zapisa trajanja od 15 do 30 sekundi, pri čemu je svaki zapis opisan sa pet tekstualnih opisa dužine od 8 do 20 reči. Ukupno obuhvata 34860 opisa. Skup podataka je kreiran od audio zapisa sa platforme Freesound, dok su opisi prikupljeni putem platforme Amazon Mechanical Turk od govornika engleskog jezika. Tokom obrade uklonjeni su vlastita imena, jedinstvene reči i transkripti govora kako bi se naglasak stavio na opis zvučnog sadržaja.

Clotho v2 sadrži oko 4.500 različitih reči i podeljen je na četiri dela: razvojni (development), validacioni (validation), evaluacioni (evaluation) i test (testing) skup.

Audio zapisi traju od 10 do 30s, dobrog kvaliteta (44.1 kHz i 16b). Sadržaj snimaka dosta varira, od zvukova u prirodi (tok reke preko kamenja, zvuk životinja), ljudskog govora do zvuk rada mašina i različitih uređaja.

Raspodela trajanja je data na sledećoj slici

\begin{figure}[h]
\centering
\includegraphics[width=6cm]{figures/distrib.png}
\caption{Raspodela trajanja snimaka u Clotho skupu podataka} 
\label{fig:distrib}
\end{figure}

Clotho V2 je podeljene na sledeći način

- Razvojni podskup - sa 3839 klipova i 19195 opisa
- Validacioni podskup - sa 1045 klipova i 5225 opisa
- Evaluacioni skup - sa 1045 klipova i 5225 opisa
- Test skup - sa 1043 klipova i 5215 opisa.

Prva 3 podskupa možemo koristiti za trening modela dok je test skup za konačnu evaluaciju.

## 1.3 Evaluacija i baseline performanse

Za merenje performansi modela koriste se 7 metrike

1. ***METEOR***\
    Poredi generisani оpis sa referetnim tekstovima na nivou reči, uzimajući u obzir tačna poklapanja, sinonime, korene reči i parafraze. Zatim računa harmonijsku sredinu precision i recall uz penal za pogrešan redosled reči. Računa se kao
    $$
    F_{mean} = \dfrac{10PR}{R+9P}
    $$
    stavljajući više fokusa na recall nego na precision.
    Zatim se računa kazna
    $$
    Pen = 0.5 \cdot \left(\dfrac{m}{u}\right)^3
    $$
    kao odnos $m$ poklopljenih delova teksta i $u$ ukupno poklopljenih reči.
    Konačni score je
    $$
    Score = F_{mean} x (1-Pen)
    $$
2. ***CIDERr***\
    Za razliku METEOR metrike, CIDEr meri koliko generisan opis (CIDEr je prvenstveno pravljen za opis slika) i pravi opis imaju slično značenje i gramatiku. Radi u par koraka
    - U originalnom i referentnom zapisu sve reči mapira na njihove korene (npr fishing u fish).
    - Svaka rečenica se zatim predstavlja kao skup n-grama prisutnih u rečenici (n-gram je skup od par reči, kod ove metrike 1 do 4 reči)
    - Mera preklapanja treba da enkodira koliko često se n-gram u generisanoj rečenici javlja u referetnoj rečenici. Pored toga, n-gram koji nije prisutan u generisanoj rečenici ne bi trebao da se javi u referentnoj. Česti n-grami dobijaju manju težinu (kao što je the u engleskom jeziku). Za enkodiranje ovoga se koristi TF-IDF težine.
    - Na osnovu ove težine dobijamo CIDER score korišćenjem TF-IDF težina za svaku kombinaciju izvornih i generisanih opisa.
3. ***SPICE***\
    Umesto poređenja reči ili n-grama, ovde se parsira generisani i referentni tekst u tzv *scene* grafove i zatim se grafovi porede. Ova metrika bolje opisuje semantički sadržaj opisa i manje meri tačno poklapanje opisa.
4. ***SPIDEr***\
    Nastao kao kombinacija *SPICE* i *CIDEr*, gde je cilj bio da se iskoristi prednost *CIDEr*-a (dobra korelacija sa ljudskom procenom tačnosti fraza) i *SPICE*-a koji dobro hvata sadržaj opisa.
5. ***SPIDEr-FL*** (*SPIDEr* with Fluency Error detection)\
    Modifikuje *SPIDEr* tako što prvenstveno proverava da li generisani opis ima ozbiljne greške, kao što su ponavljanje reči ili gramatičke greške, najčešće pomoću posebnog klasifikatora. Ako se detektuje greška opis dobija skor 0.
6. ***FENSE***\
    Koristi S-BERT da izmeri semantičku sličnost između generisanih i referentnih opisa (kosinusna sličnost embedding vektora) a onda dodaje i detektor grešaka, slično kao kod prethodne metrike.
7. ***Vocabulary***\
    Meri raznovrsnost izlaza modela, obično kao broj jedinstvenih reči ili n-grama, kako bi se detektovalo ako model uvek koristi iste fraze.

U DCASE2024, problemu 6, korišćen je FENSE za rangiranje metoda. Baseline arhitektura (koju ćemo obraditi u sledećem poglavlju) postiže sledeće rezultate

| Metric | Value |
|---|---|
| METEOR | 0.1897 |
| CIDEr | 0.4619 |
| SPICE | 0.1335 |
| SPIDEr | 0.2977 |
| SPIDEr-FL | 0.2962 |
| FENSE | 0.5040 |
| Vocabulary | 551 |

\newpage
## 1.3 Pokretanje modela

Samo pokretanje modela je bilo relativno prosto. Nakon povlačenja repozitorijuma sa GitHub-a je potrebno

1. **Kreirati virtuelni environment**, najbolje u Python 3.11 s obirom na pakete koje treba instalirati.
2. **Instalirati pakete**\
    Ovde je najviše problema nastalo. Ako se projekat pokreće na CUDA grafičkama, instalacija je jednostavna. Kod AMD kartica može se koristiti ROCm, gde je podrška najbolja na Linuxu. Na Windows-u je na kraju najlakše bilo izbaciti `DeepSpeed` paket koji je svakako za trening i inferenciju na distribuiranim i multi-gpu uređajima kao i podesiti `torch` na CPU verziju, što je za inferenciju sasvim prihvatljivo.
3. **Pokretanje modela**\
    U okviru repozitorijuma je dato uputsvo kako pokrenuti model, međutim dat primer ne funkcioniše na Windowsu. Primer pokretanja se može naći u `test.py` skripti.
