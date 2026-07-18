# 2. Opis baseline rešenja

## 2.1 Arhitektura modela

Baseline model se zoveCNext-trans i to je klasična encoder-decoder arhitektura gde konvolucioni enkoder izvlači audio reprezentacije, a transformer dekoder ih koristi da generiše tekstualni opis reč po reč. Analiziramo svaku od komponenta posebno

### 2.1.1 ConvNeXt enkoder

Razvoj ConvNeXt mreža je bio inspirisan uspesima vizuelnih transformere, gde je ideja bila adaptirati ideje koje su učinile transformere uspešnim na konvolucione mreže. Autori su u radu `A ConvNet for the 2020s` uzeli ResNet-50 kao osnovu a zatim postepeno koristili tehnike transformera kako bi poboljšali performanse. Ovo je učinjeno u više koraka.

1. **Trening protokol**\
    Pre bilo kakvih arhitekturnih promena autori su prvo primenili modernije tehnike treniranja i to konkretno
    - Koristili su AdamW optimizator umesto SGD
    - Povećali broj epoha
    - Koristili nove augmentacione tehnike kao što su mixup i cutmix
    - Label smoothing, gde se ciljna labela "uglađuje", npr ako je ciljna labela bio vektor $[0, 1, 0, 0]$ on se transformise u $[0.1, 0.7, 0.1, 0.1]$.
    - Stochastic depth - slično kao dropout, međutim umesto isključivanja pojedinih neurona, ova tehnika preskače pojedine strukturne blokove.

2. **Promene u strukturi blokova**

    - Kod ResNet-50 se koristila takva arhitektura gde se na slici vrši standardna konvolucija (nad svim kanalima istovremeno) sa veličinom kernela 3x3. Kako je skupo primeniti 3x3 konvoluciju na svim kanalima, tehnika koju je ResNet koristio je da prvo se vrši 1x1 konvolucija, čime se veličina kanala zadržava a broj kanala smanjuje. To je onda praćeno 3x3 konvolucijom koja je sada jeftinija a zatim još jedna 1x1 konvolucija se vrši koja vraća broj kanala. Ovim model ne može da vidi dalje zavisnosti u podacima (s obzirom da je kernel mali), za razlika od transformera koji uče zavisnost svakog podatka od svih ostalih u ulazu.\
    Zbog ovoga je prva promena promeniti tip i redosled konvolucije. Prvo će se vršiti 7x7 dubinska konvolucija (svaki kanal se posebno konvolira), zatim se radi 1x1 konvolucija sa većim brojem kanala, nakon čega sledi GELU aktivacioni sloj i na kraju 1x1 konvolucija koja smanjuje broj kanala. Ovim sada model prvo uči prostorne zavisnosti i to sa većim filterom (perceptivnim poljem), zatim povećava dimenzionalnost kako bi mogao kompleksnije nelinearne transformacije da vrši a zatim vraća broj kanala. Ovakva metoda je sličnija transformerima - prvo se vrši prostorna transformacija a zatim po kanalima.
    - Druga promena, spomenuta gore je korišćenje GELU umesto ReLu kao i korišćenje aktivacije samo jednom u bloku umesto posle svake konvolucije. Ovo čini model opet sličnijim transformerima, koji imaju samo jedan nelinearan sloj (feed-forward network nakon attentiona koji je linearan)
    - Poslednja promena u okviru blokova je normalizacija. ResNet je koristio BatchNorm nakon svake konvolucije, što se loše ponaša kod manjih batcheve i fine-tuninga. Umesto toga ConvNext koristi jedan LazerNorm po bloku, slično transformeru.

3. **Promene u rasporedu blokova**

    - Kod SwinTransformera je korišćena raspored blokova 1:1:3:1, tj najveća računica je vršena u kasnijim slojevima, dok je ResNet koristion 3,4,6,3. Zbog ovoga ConvNeXt koristi raspored blokova (3,3,9,3).
    - Prvi sloj mreže kod ResNet koristi 7x7 konvoluciju sa stride 2 i maxpool, kako bi smanjio dimenzionalnost ulaza. Sa druge strane, transformeri dele sliku na patcheve i formiraju embeddinge. Zato ConvNeXt prvo radi 4x4 konvoluciju sa stride 4, efektivno deleći ulaz na 4x4 delove.
    - Umesto smanjivanja u prvom sloju sa stride 2, sada je odvojen LayerNorm sloj sa 2x2 konvolucijom kako bi se kombinovali patch-evi.

Kombinovanjem ovih tehnika je kreiran ConvNeXt, koji postiže praktično jednake rezultate sa vision transformerom, pri čemu koristi manje memorije, ima veći throughput i manje potrebnih FLOP-ova za inferenciju.

\begin{figure}[h]
\centering
\includegraphics[width=12cm]{figures/convnext.png}
\caption{ConvNext} 
\label{fig:convnext}
\end{figure}

### 2.1.2 Projekcija

Sledeći sloj je jednostavan - kako ConvNeXt daje na izlazu 768-dimenzione vektore a dekoder u sledećem korako koristi ulaz sa 256 dimenzija, dodat je projekcioni sloj
- Dropout(0.5)
- Linear (768 -> 256)
- ReLu
- Dropout(0.5)

### 2.1.3 Dekoder

Standardni PyTorch `TransformerDecoder` sa parametrima
- Veličina ulaza: `256`
- Broj attention head-ova: `8`
- Broj dekoder slojeva: `6`.
- Dimenzija feedforward mreže: `2048`.
- GELU
- Dropout: 0.2

Tok kroz dekoder je sledeći

1. Na ulaz dekodera se dovode audio frame embeddings iz projekcionog sloja kao i izlazi embedding sloja koji pretvara trenutno generisane tekst tokene u vektore, uz dodato poziciono kodiranje.

2. Unutar svakog od 6 slojeva dekodera, prvo se primenjuje self-attention nad tekst tokenima

3. Zatim se primenjuje cross-attention, gde svaki tekst token određuje koliko je važan svaki audio frame embedding za njegovu trenutnu reprezentaciju.

4. Poslednja tekst reprezentacija prolazi kroz linearni klasifikator verovatnoće za
   sledeću reč nad celim rečnikom.

## 2.2 Trening in inferencija

Kod treniranja modela su autori koristili sledeće tehnike za bolju generalizaciju

- Teacher forcing - tehnika kojom se izbegava poznat problem kod autoregresivnih modela. Ovaj tip modela predviđa sledeću reč na osnovu prethodnih, tako da svaka loše predviđena reč tokom treninga gomila grešku. Umesto toga se kao predhodno predviđena reč uvek daje tačna reč.

- Label smoothing, tehnika kojom se koriguje ciljni vektor koji model treba da predvidi. Ako su ciljne verovatnoće date sa 0 i 1, model se forsira da bude ekstremno samouveren, što dovodi do overfittinga.

- Mixup augmentacija, gde se model trenira nad instancama koje se mešaju sa drugim instancama iz batch-a. Ovakva augmentacija se primenjuje na audiu ali i na tekstu. Na ovaj način model uči ne samo da prepozna tačne primere već i njihove interpolacije.

- AdamW optimizator, sa $5\cdot 10^-4$ stopom učenja, weigh decay $2.0$ i kosinusnim decay scheduler-om koji glatko smanjuje learning rate od inicijalne vrednosti do 0 u toku 400 epohe.

- Batch size 64 i gradient accumulation 8, s obzirom da treniranje sa 512 batch size bi zahtevao previše GPU memorije. Umesto toga se vrši trening sa batch-evima od 64 podataka, pri čemu se vrši trening nad 8 batch-a bez menjanja težina. Nakon svih 8 batch-a se akumuliraju gradijenti i menjaju se težine.

Tokom inferencije se koriste sledeća poboljšanja

- Beam search sa veličinom 3\
Tokom klasične inferencije model bira jednu najverovatniju sledeću reč i nastavlja generisanje. Tu je problem što lokalno najbolji izbor sledeće reči ne vodi nužno do globalno najboljeg rezultat. Zato umesto toga model ide u $n$ (ovde 3) najbolja smera, tj bira 3 najbolje sledeće reči paralelno, zatim odredi 3 sledeće reči za svaku od 3 izabranih reči i od tih kombinacija bira one sa najboljom kumulativnom verovatnoćom. Na ovaj način se mnogo više potencijalnih opisa istražuje.

- Zabrana ponavljanja bitnih reči\
Tranformer dekoderi često ispoljavaju ponavljanje reči (npr dog is barking and dog is barking), tako da ova tehnika izbegava taj problem podešavanjem verovatnoće na 0 bitnim rečima (imenica, glagol, pridev) koje su već generisanje.

- Ograničenje dužine, kojom želimo da izbegnemo da model generiše prekratke ili predugačke opise.