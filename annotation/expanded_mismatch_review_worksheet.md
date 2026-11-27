# Source-grounded annotation review worksheet

All 21 selected detail labels were user-confirmed after assistant-guided review in chat. These are AI-assisted, user-reviewed annotations, not independent human gold. No model rerun was required.

For each selected detail, confirm its label against the saved source. For an unsupported detail, a contextual quote is not proof of absence: the full saved source can be retrieved by example ID using load_split.

## test_00398

Original claim: She has accumulated **10,585 points** and holds the No. 1 position in the Women's Tennis Association rankings.

1. **contradicted** — Iga Swiatek has 10,585 WTA ranking points.

   Evidence: |1||-||Iga Swiatek||8,975|

   Reason: The saved ranking table gives 8,975, not 10,585. This evaluates the source snapshot, not current rankings.

   Human review: user confirmed after assisted review

2. **supported** — Iga Swiatek is ranked No. 1 in the WTA rankings.

   Evidence: Iga Swiatek remains the current world No.1 after replacing the retired Ashleigh Barty early in 2022.

   Reason: The source explicitly identifies the top-ranked player; she is resolved to Iga from source context.

   Human review: user confirmed after assisted review

## test_00963

Original claim: This brings the total number of high schools in Tracy to six.

1. **unsupported** — The total number of high schools in Tracy is six.

   Evidence: An excellent education for every child

   Reason: The entire saved source is a 353-character GreatSchools boilerplate; it gives no school count. This is missing saved evidence, not proof that the real-world count is wrong.

   Human review: user confirmed after assisted review

## test_00995

Original claim: The 2022 Great New York State Fair will take place from August 24 to September 5.

1. **unsupported** — The 2022 Great New York State Fair takes place from August 24 to September 5.

   Evidence: People from across New York State will come together next year to experience an affordable, 13-day celebration of delicious food, eye-opening exhibits, captivating entertainment, and great fun.

   Reason: The saved 399-character source states a 13-day duration but does not establish the year or exact dates.

   Human review: user confirmed after assisted review

## test_01088

Original claim: "Let's Get This Party Started" was originally recorded by the American band The Black Eyed Peas and released in 2003 as the lead single from their album Elephunk.

1. **unsupported** — The Black Eyed Peas originally recorded Let's Get This Party Started.

   Evidence: This disambiguation page lists articles associated with the title Let's Get This Party Started .

   Reason: The source lists several different works with this title, but does not establish this artist attribution. Multiple works mean omission is not direct contradiction.

   Human review: user confirmed after assisted review

2. **unsupported** — The claimed recording was released in 2003.

   Evidence: This disambiguation page lists articles associated with the title Let's Get This Party Started .

   Reason: The saved page does not establish 2003 for this claimed recording.

   Human review: user confirmed after assisted review

3. **unsupported** — The claimed recording was the lead single from Elephunk.

   Evidence: This disambiguation page lists articles associated with the title Let's Get This Party Started .

   Reason: The saved page does not identify Elephunk or establish the lead-single relationship.

   Human review: user confirmed after assisted review

## test_00887

Original claim: The fiscal year can begin and end on any month except December, and is used for accounting purposes to prepare financial statements.

1. **unsupported** — A fiscal year can begin and end in any month except December.

   Evidence: At UCI, the fiscal year begins on July 1 and ends on June 30.

   Reason: The institution-specific source does not establish this general rule. The December restriction is also separately localized below; these reference targets overlap.

   Human review: user confirmed after assisted review

2. **unsupported** — December is excluded as a possible fiscal-year boundary month.

   Evidence: At UCI, the fiscal year begins on July 1 and ends on June 30.

   Reason: The source never establishes the December exclusion; a December fiscal period is not a fiscal-year boundary.

   Human review: user confirmed after assisted review

3. **supported** — Fiscal years are used for accounting and preparing annual financial statements.

   Evidence: A fiscal year is important for accounting purposes and for preparing annual financial statements.

   Reason: Direct statement.

   Human review: user confirmed after assisted review

## test_00983

Original claim: Hamilton's last Grey Cup win was in 2021 when the Winnipeg Blue Bombers defeated the Hamilton Tiger-Cats 33-25 in overtime at Tim Hortons Field in Hamilton.

1. **contradicted** — Hamilton won the Grey Cup in 2021.

   Evidence: |2021||Winnipeg Blue Bombers (12)||33-25||Hamilton Tiger-Cats|

   Reason: The table explicitly identifies Winnipeg as champion and Hamilton as runner-up.

   Human review: user confirmed after assisted review

2. **supported** — Winnipeg defeated Hamilton 33-25 in the 2021 Grey Cup.

   Evidence: |2021||Winnipeg Blue Bombers (12)||33-25||Hamilton Tiger-Cats|

   Reason: The year, winner, runner-up and score are explicit table fields. Model alignments containing overtime are contextual target matches only: the saved table does not independently establish overtime.

   Human review: user confirmed after assisted review

## test_01032

Original claim: If you are referring to the French thriller-romance series created and written by Guillaume Nicloux, it was released on Netflix on December 19, 2019.

1. **supported** — Twice Upon a Time is a French series created by Guillaume Nicloux.

   Evidence: |Created by||Guillaume Nicloux|

   Reason: The creator is explicit; the title and country are established by the surrounding source.

   Human review: user confirmed after assisted review

2. **supported** — Guillaume Nicloux contributed to writing Twice Upon a Time.

   Evidence: |Written by|| Guillaume Nicloux |

   Reason: The source lists Nicloux with a co-writer. The claim does not state he was the only writer.

   Human review: user confirmed after assisted review

3. **supported** — Twice Upon a Time was released on Netflix on December 19, 2019.

   Evidence: It was released in the United States on Netflix on 19 December 2019.

   Reason: The date and platform are supported for the US release. No worldwide-release interpretation is assumed.

   Human review: user confirmed after assisted review

## test_00471

Original claim: Washing machines account for a quarter of domestic wastewater, so reusing this water can save a lot of water.

1. **unsupported** — Washing machines account for a quarter of domestic wastewater.

   Evidence: One wash cycle in a washing machine can easily take up about 30% of the total water consumed in one house per day.

   Reason: The source measures household water consumed, not the share of wastewater; 30% versus 25% is not a direct numerical contradiction because denominators differ.

   Human review: user confirmed after assisted review

2. **supported** — Reusing washing-machine water can substantially reduce fresh-water requirements.

   Evidence: By using this system, we (a family of two) have been able to offset most of our flushing requirements.

   Reason: The source gives a concrete water-reuse example. This does not imply all households have the same savings.

   Human review: user confirmed after assisted review

## test_00958

Original claim: Precision is the accuracy of a measurement or prediction, and can be calculated by subtracting the lowest measured value from the highest measured value.

1. **contradicted** — Measurement precision is the same as measurement accuracy.

   Evidence: Precision is not the same as accuracy. Accuracy measures how close experimental values come to the true or theoretical value, while precision measures how close the measured values are to each other.

   Reason: The source explicitly distinguishes the concepts. This is an additional relation category, not relabeled as a number error.

   Human review: user confirmed after assisted review

2. **supported** — A precision measure can be calculated by subtracting the lowest measured value from the highest.

   Evidence: The range of a set of data is the difference between the highest and lowest measurements. Just subtract one from the other.

   Reason: The article permits reporting range as a precision measure; it does not call range the only precision measure.

   Human review: user confirmed after assisted review

## test_00252

Original claim: They are 33 cm (13 in) in height and 43 cm (17 in) in length and have an average lifespan of 6.5 years.

1. **unsupported** — Little penguins are 43 cm (17 inches) in length.

   Evidence: Eudyptula species typically grow to between 30 and 33 cm (12 and 13 in) tall and on average weigh 1.5 kg (3.3 lb).

   Reason: The saved article gives height and weight, but does not establish the claimed length. Height is not treated as a conflicting length.

   Human review: user confirmed after assisted review

2. **supported** — Little penguins have an average lifespan of 6.5 years.

   Evidence: The average for the species is 6.5 years, but flipper ringing experiments show that in very exceptional cases they may live up to 25 years in captivity.

   Reason: The average is explicitly stated and distinguished from an exceptional maximum.

   Human review: user confirmed after assisted review

