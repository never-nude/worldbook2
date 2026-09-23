# Duryodhana evidence packet

## Assignment and disposition

- **Trail ID:** `duryodhana` (canonical URL: `?trail=duryodhana`).
- **Type:** documented civil case with disputed allegations and a confirmed return.
- **Question:** How did a temple statue reach the art market and find its way home?
- **Lesson:** a paper trail can connect an object across institutions without establishing its complete physical itinerary.
- **Scope:** one sandstone statue; Cambodia, Thailand, United Kingdom, Belgian collection, New York; approximately 1972–2014, with a 2021 museum confirmation.
- **Reuse:** `WEEKLY_FLOW_REGISTRY.weekly_duryodhana_trail` in `index.html`; original six stops, five edges, coordinates, and source set preserved in normalized form.
- **Deliverable:** [`data/trails/duryodhana.json`](../../v2/data/trails/duryodhana.json).
- **Status:** source-checked; bounded independent review completed 2026-09-22 with one accepted wording correction. Ready for implementation within the documented qualifications and access limits below.
- **Researcher:** Codex statue-evidence subagent. **Last checked:** 2026-09-22.
- **Independent reviewer:** Codex inventory/release subagent, separately reading the cited primary material; reviewed 2026-09-22.
- **Stopping condition:** verify existing primary sources, attach them to the six-stop sequence, preserve uncertainty; no additional route reconstruction or publishing.

## Reader outline

Follow an object through six kinds of evidence: physical traces, an alleged dealer handoff, a sale intermediary, collection history, a contested auction, and repatriation. At each stop, show its date, role, evidence status, sources, and limits. The map is a diagram of the records, not a freight map. The final explanation asks readers to distinguish a relationship from a route and a settlement from a verdict.

## Stops and claim register

The full reader copy lives in JSON; this table records the support for each stop without duplicating it.

| Stop / claim ID | Event or claim checked | Evidence status | Source locator | Geographic precision |
| --- | --- | --- | --- | --- |
| `koh-ker` / `c-origin` | Temple attribution, surviving feet, comparison, approximate removal year | Expert assessment and allegation reported in complaint | `doj-amended-complaint-2013`, printed pp. 5–6, paragraphs 11–13; p. 8, paragraph 18 | Approximate temple-site marker |
| `bangkok` / `c-dealer` | Separate movement of head/torso and dealer destination | Allegation | Same complaint, pp. 7–8, paragraphs 17–18; `doj-return-2014`, case summary | Bangkok only; premises unknown |
| `uk-auction-house` / `c-auction-house` | Consignment and 1975 sale | Case-record chronology | Complaint, pp. 8–9, paragraphs 19–20; `doj-civil-action-2012`, complaint summary | Country only; no city inferred |
| `belgian-collection` / `c-collection` | Collector/heir possession until consignment | Prosecutorial account of ownership history | `doj-civil-action-2012`, final paragraph of complaint summary; complaint p. 9, paragraph 20 adds corporate transfers | Schematic association, not a verified storage address |
| `new-york` / `c-case` | 2010 import, 2011 withdrawal, subsequent settlement | Reported auction chronology and documented settlement | `doj-civil-action-2012`, final paragraph of complaint summary; `court-settlement-2013`, pp. 1–3 | City only; coordinate is not Sotheby’s address |
| `phnom-penh` / `c-return` | 2014 return and presence in museum in 2021 | Institutional confirmation | `unesco-museum-2021`, Duryodhana section | Approximate museum-site marker; no current-display claim |

## Connections and continuity

Every connection concerns the same named Duryodhana, not a combination of unrelated country-pair flows. That object continuity does not establish geographic continuity between every marker.

| Leg ID | Relationship | Geometry and limits |
| --- | --- | --- |
| `koh-ker-to-bangkok` | Alleged physical movement | Schematic endpoints; no border crossing or complete road route. Parts travelled separately in the allegation. |
| `bangkok-to-uk-auction-house` | Chronology and consignment | A collector participates between dealer and auction house but is not assigned an invented geographic stop. |
| `uk-auction-house-to-belgian-collection` | Sale/ownership | Country associations do not prove shipment, payment, or storage. |
| `belgian-collection-to-new-york` | Consignment and reported import | The Belgian marker is not evidence of the shipment’s export country. |
| `new-york-to-phnom-penh` | Legal handover followed by physical return | These are separate events; no intermediate transport stops claimed. |

Each JSON leg carries its own `sourceIds`, `relationship`, `geometryBasis`, and `limitations`. No numerical flow, sale amount, rate, or money route is asserted. Lines must have equal, uncalibrated width; movement animation must not imply an observed transport journey.

## Primary sources checked

| Stable ID | Source | Publication / filing date | Locator checked | Verification |
| --- | --- | --- | --- | --- |
| `doj-amended-complaint-2013` | [Amended complaint, Document 47](https://www.justice.gov/usao/nys/pressreleases/May14/CambodianSculptureReturn/Duryodhana%20-%20Cambodian%20Scupture%20-%20Amended%20Complaint.pdf) | 2013-04-09 | Printed pp. 4–10, especially paragraphs 11–13 and 17–21 | Official PDF downloaded; relevant page images read because browser text extraction contained only docket headers. |
| `doj-civil-action-2012` | [DOJ civil-action announcement](https://www.justice.gov/archive/usao/nys/pressreleases/April12/duryodhanastatueforfeiture.html) | 2012-04-04 | Paragraphs under complaint-summary introduction | Official HTML opened and checked; early allegations qualified by later settlement. |
| `court-settlement-2013` | [Executed settlement, Document 76](https://www.justice.gov/usao/nys/pressreleases/May14/CambodianSculptureReturn/Duryodhana%20-%20Cambodian%20Sculpture%20-%20Settlement%20Stipulation%20and%20Order%20%28Executed%29.pdf) | Filed 2013-12-13 | All five pages; material terms pp. 2–3 | Official PDF downloaded and visually read. Browser initially failed on encoded URL, then succeeded through DOJ link. |
| `doj-return-2014` | [DOJ return announcement](https://www.justice.gov/usao-sdny/pr/manhattan-us-attorney-announces-return-10th-century-sandstone-sculpture-kingdom) | 2014-05-07; site update 2015-05-18 | Opening announcement and complaint summary | Official HTML opened and checked. It describes physical departure as imminent, so it is not used as evidence of arrival on May 7. |
| `unesco-museum-2021` | [UNESCO National Museum anniversary](https://www.unesco.org/en/articles/cambodia-commemorates-101st-anniversary-national-museum-cambodia) | 2021-04-21; updated 2023-04-20 | Duryodhana section | Opened and checked; confirms 2014 return and museum presence as of its account. |

All sources accessed 2026-09-22. DOJ releases are primary accounts of the government’s case, not independent corroboration of the complaint. UNESCO is an additional institutional record of return and museum presence. No source passage is quoted in the reader.

## Material corrections and conflicts

1. **Settlement qualifications must travel with the story.** Page 2 records the respondents’ position that Ruspoli held legal title. It also states that the United States did not contend Sotheby’s or Ruspoli knew Cambodia owned the statue or knowingly supplied false provenance. Do not carry the 2012 announcement’s accusations about knowledge forward as established findings. The reader’s New York limitation states this explicitly.
2. **The legal handover occurred in a different geographic context from repatriation.** Settlement p. 3, paragraphs 1–3, provides for delivery to a Cambodian representative in New York and dismissal after transfer. UNESCO supplies confirmation of physical return. Do not describe the court order as specifying a New York-to-Phnom Penh shipment.
3. **Settlement dates differ between official records.** The executed PDF is dated December 12, 2013, and docket-stamped December 13; the 2014 release says approval was December 16. Reader copy says December 2013. JSON source metadata uses the explicitly identified filing date. Resolving the docket date is optional enrichment, not a reason to invent precision.
4. **Removal date:** paragraph 18 says approximately 1972. Normalized copy retains that qualification.
5. **Belgium:** preserve the collection’s association without implying continuous storage in Belgium, each heir’s residence, or Belgian export in 2010.
6. **May 7, 2014:** the DOJ release announces return while referring to imminent physical departure. Use only the supported year for repatriation, not a fabricated arrival day.
7. **Present tense:** UNESCO’s museum statement is dated 2021. It supports the historical museum record, not verified display status in 2026.

The legacy registry is retained intact by this research task. These revisions belong to the normalized reader content; migration should preserve the original research as provenance rather than silently rewriting it.

## Display requirements

- Retain an always-visible notice that the lines connect evidence, not a verified shipping route.
- Show each stop’s evidence status, location precision, and limitations, plus the outgoing leg’s relationship.
- Use country-level UK geometry and schematic Belgian association. The two precise-looking coordinate pairs are display anchors, not researched locations.
- `coordinates` and `displayCoordinates` are different: the latter reproduce existing displaced numbered badges for legibility and must never feed route geometry.
- Avoid automatic dots travelling along the full case chain; that would overstate physical-route evidence. Selecting stops in order is appropriate.
- No guilt or legal-status classification may be inferred from country color. The case ends in settlement, not a verdict.
- Sources attach to individual stops/legs and remain accessible from the reader.

## Remaining gaps and optional enrichment

Unknown: transport carriers and intermediate storage; UK city; complete collection-location history; prices and payments; exact arrival date; current display status. None blocks the bounded paper-trail story. They would block a claimed complete shipping or money trail.

If extending the story, prioritize accession/return records for exact arrival, original sale records for price and terms, and documentary support for any extra location. Do not add three more stops merely because the interface supports them.

## Independent review

**Outcome:** bounded independent source review complete on 2026-09-22. No unresolved consequential factual issue was found within the six-stop scope after the legal-title wording correction below. This is a second review of source support, not independent corroboration of the complaint's allegations or a review of every historical fact about the object.

**Method:** the reviewer read the amended complaint's cover and printed pp. 5–9, all five pages of the settlement, both DOJ HTML announcements, and the indexed full text of the cited UNESCO article. The court page images were inspected directly; the scratch PDFs were independently downloaded again from the official DOJ URLs and matched byte-for-byte. SHA-256: complaint `10894ded5caa1882e1adf5f2d324d80e2aff61e952215341f2193fd8e58495b8`; settlement `bc96d8860cab787ac498d588ba0ccb737e0b4ff44c96675b96dbeeda114e550b`. Neither the first researcher's conclusions nor agreement between models substituted for reading sources.

| Consequential check | Primary support read | Review result |
| --- | --- | --- |
| Allegations versus findings | Amended complaint p. 1 expressly frames the case as allegations; pp. 5–6, paragraphs 11–13 describe the archaeological comparison; pp. 7–9, paragraphs 17–20 describe alleged removal, intermediaries and sale. Settlement pp. 1–3 records the dispute and settlement. | The JSON qualifies the early journey as alleged, identifies the expert assessment as reported in a filing, and does not label settlement as a trial verdict. The 1975 sale/ownership summaries are attributed to the case record. |
| Belgian collection versus shipment origin | Complaint p. 9, paragraph 20 describes purchase through a Belgian corporation and subsequent transfers, ultimately to Ruspoli. The 2012 release describes possession until consignment; the 2014 release reports U.S. import without identifying Belgium as the export origin. | The Belgian stop's storage-location caveat and the `belgian-collection-to-new-york` leg correctly avoid asserting a Belgium-origin shipment. This review does not establish where the object was physically stored. |
| Legal title, knowledge and handover | Settlement p. 2 records the parties' title positions and the U.S. non-contention regarding knowledge and false provenance; p. 3, paragraphs 1–3 specifies delivery to Cambodia's representative in New York and subsequent dismissal. | One wording correction was requested and accepted: the New York limitation now says Sotheby's and Ruspoli maintained **that Ruspoli held clear legal title**, avoiding an implication that both held title. The knowledge qualification is a fair concise paraphrase. The New York handover remains separate from later repatriation. |
| Historical museum record versus present-day status | UNESCO's article is dated April 21, 2021, with an April 20, 2023 update. Its Duryodhana section states return in 2014 and museum presence in that account. The May 7, 2014 DOJ release describes physical return as imminent. | The final stop dates the museum account and expressly leaves present-day display and exact transport/arrival unestablished. No arrival on May 7 is asserted. |

**Correction verification:** the integration owner changed `stops[new-york].limitations` in the JSON, and the reviewer reread the corrected field. No other JSON change was made or requested by this review.

**Access and scope limits:** direct UNESCO article opens timed out during this review; its complete indexed official-page text, including the date/update labels and Duryodhana paragraph, was read through search. This establishes support in the dated account, not an in-person inventory check or confirmed 2026 display. The amended complaint PDF also contains exhibits; this review inspected the cited complaint pages, not every exhibit. No full court-docket audit or additional transport research was conducted.

**Unresolved but nonblocking:** the executed settlement bears December 12 signatures and a December 13 filing header, whereas the 2014 DOJ release gives December 16 approval. The JSON appropriately uses December 2013 for the event and explicitly labels December 13 as filing metadata. Exact storage sites, UK city, transport itinerary, payments and current display status remain unknown.

**Implementation-ready scope:** six evidence-linked stops and five unweighted schematic connections with the existing qualifications visible. This review does not authorize expanding the chain into an exact physical itinerary, payment trail or quantified flow.
