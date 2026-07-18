# 3. Potencijalna unapređenja

Ideja za potencijalno unapređenje rešenja je koristiti JEPA model kako bi dobili bolje latentne reprezentacije ulaznih audio signala kao i trenirati dekoder sa dva cilja - bolje predvideti latentne reprezentacije tekstualnog opisa kao i generisati opis.

## 3.1 JEPA arhitektura

Joint-Embedding Predictive Architecture ili JEPA je self-supervised learning arhitektura kojom se vrši predviđanje latentne reprezantcije maskiranih delova ulaza. Kod slika JEPA je korišćena za generisanje kvalitetnijih latentnih reprezentacija slika, tj embedding vektora koji bi bolje očuvali značenje odnosno kontekst slike. U opštem slučaju JEPA funkcioniše na sledeći način

1. Deo ulaza (slika, audio) se maskira, tj sakrije.
2. Maskirani ulaz se dovodi na context encoder koji nemaskirani deo procesira i generiše njegovu reprezentaciju.
3. Target encoder uzima originalni, nemaskirani ulaz i generiše njegovu reprezentaciju.
4. Imamo manji prediktor koji koristi reprezentaciju dostupnog dela ulaza kako bi predvideo latentnu reprezentaciju maskiranog dela koju generiše target encoder.
5. Cilj je da se originalna i rekonstruisana latentna reprezentacija poklope

U više radova pokazano je da ovakav način self-supervised učenja može dovesti do kvalitetnijih latentnih reprezentacija koje se uspešno koriste u različitim downstream zadacima.

Audio JEPA može naučiti reprezentacije koje bolje opisuju semantički sadržaj audio signala, nezavisno od konkretnog zadatka. Takve reprezentacije mogu predstavljati kvalitetniji ulaz dekoderu, naročito kada je količina označenih podataka ograničena. Koristićemo pre-trenirani Audio JEPA model i dodatno ga trenirati na Clotho skupu.

\begin{figure}[h]
\centering
\includegraphics[width=12cm]{figures/ajepa.png}
\caption{Audio JEPA} 
\label{fig:ajepa}
\end{figure}

## 3.2 Treniranje sa auxiliary loss

S obzirom da se dekoder trenira sa ciljem da što bolje predvidi sledeću reč u opisu na osnovu ciljnog opisa, model se podstiče da reprodukuje tačan niz tokena iz referentnog opisa. Na primer ukoliko je ciljni opis "glasan zvuk automobila", validan je i opis "bucan zvuk vozila/kola", koje bi model smatrao pogrešnim. Zato je potencijalno unapređenje trenirati model sa dva cilja
- Standardni cross-entropy gubitak koji sada koristi baseline model.
- Pored standardnog cross-entropy gubitka, može se uvesti dodatni semantički gubitak kojim se minimizuje rastojanje između embeddinga generisanog opisa i embeddinga referentnog opisa dobijenog pomoću prethodno istreniranog tekstualnog enkodera kao što je SBERT.

## 3.3 Potencijalni nedostaci

Dodavanjem Audio JEPA se povećava računska složenost sistema i zahteva ili dodati fazu pretreniranja ili koristiti već treniran model. Pored toga, dodavanje semantičkog gubitka zahteva pažljivo izabrati težine ova dva gubitka, koje se potencijalno mogu i učiti.