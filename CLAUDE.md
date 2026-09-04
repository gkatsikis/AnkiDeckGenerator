# Anki Deck Generator

JSON deck files in `decks/` are turned into `.apkg` files by `generate_deck.py` (see README for usage and the JSON format).

## Scaffolding rules for recall decks

These rules govern the *order and shape* of cards in an English-front recall deck. Anki handles spacing between sessions; the deck author controls everything else. Each rule names the finding it rests on (sources at the bottom).

### 1. Known before new (i+1)
Every word in a sentence card must already have been taught, by the prerequisite deck (Part 1 for a Part 2 deck) or by an earlier card in this deck. A sentence card adds **at most one** new item. If it needs two, split it into two cards. *(Krashen's i+1 / "one target" sentence mining; Wozniak: build upon the basics.)*

### 2. Ladders, not jumps: word → chunk → sentence
Introduce a word, then a 2–4 word chunk that uses it, then the full sentence. Example: 油 → 油腻 → 有点油腻 → 这道菜有点油腻。 Teach formulaic chunks (可以...吗, 比较喜欢, 的时候, 边...边) as units of their own, since learners retrieve stored chunks faster than they assemble words, and chunk use predicts fluency. *(Boers et al. 2006; formulaic-sequence research.)*

### 3. Small batches, used immediately
Do not front-load a section with a long vocabulary list. Teach **6–10** new words, then chunks and sentences that use them, then the next batch. Long lists exceed working memory and delay retrieval in context. *(Cognitive load theory; Nation recommends packs of 15–20 cards, never more than 50.)* The current Part 2 v2 deck still front-loads some sections (the food section opens with 54 vocab cards); the next revision should interleave batches.

### 4. Never stack a semantic set back to back
Words that share a category (all fruits, all belt colors, all four tastes), near-synonyms and opposites interfere with each other when learned together and take longer to learn. Group by **scenario** instead (ordering a dish: 菜, 道, 太咸了, 少放油), which helps rather than hurts. When a set is unavoidable, introduce members several cards apart, and use each in a sentence before the next member appears. Keep look-alike or sound-alike items apart (教/叫, 汤/糖, 买/卖). *(Tinkham 1993, 1997; Waring 1997; Erten & Tekin 2008; Nation 2000.)*

### 5. Interleave once the ladder is built
Blocked practice of one topic feels better immediately, but interleaved practice wins on tests a week later, and lower-proficiency learners gain the most. So: reuse each chunk in a **different** section later; alternate sub-topics within a section instead of one 40-sentence block; end each section with a few mixed-topic sentences. *(Nakata & Suzuki 2019; interleaved grammar practice studies.)*

### 6. Spaced re-exposure inside the deck order
Every new item recurs in at least two later sentences, one within about 10 cards and one in a later section. Vary the context, not just the card. No orphan vocabulary: a vocab card that no later sentence uses gets a sentence or gets cut. *(Spacing effect; varied practice as a desirable difficulty; Wozniak: refer to other memories.)*

### 7. One idea per card, redundancy welcome
The front asks for exactly one thing. Seeing the same chunk from several angles (word card, chunk card, two sentences) is good redundancy, not a violation. *(Wozniak: minimum information principle; redundancy rule.)*

### 8. Productive direction, no answer leaks
English front → Chinese back trains speaking; productive retrieval builds productive knowledge, and receptive retrieval does not transfer to it. Fronts carry no characters or pinyin. They may carry a short context cue in parentheses, "(lit. ...)" or "(道 = measure word for dishes)", to disambiguate, because a cue on the front is cheaper than a wordy answer. *(Retrieval-direction studies; Wozniak: context cues, optimize wording.)*

### 9. Fade the scaffold
Hints belong on the chunk card and the first sentence that uses a pattern. Later reuses drop the hint, because support that helps a novice becomes noise for a learner who already knows the item. *(Faded worked examples; expertise reversal effect.)*

### 10. Personalize, and flag confusables
Sentences should be things the learner would actually say about their own life (tea, BJJ, family, work); a personal example cuts learning time sharply. When two items are confusable (得 dé/de/děi, 种 zhǒng/zhòng, 过 "experienced" vs "pass"), say so on the front and keep them far apart. *(Wozniak: personalize; combat interference.)*

### 11. Frequency and usefulness first
Function words, measure words and patterns come before niche nouns; specialized terms (锦标赛, 横杠) go last in their section or get cut if no sentence uses them. Keep TTS audio on every card (text plus sound). *(Nation; Wozniak: prioritize.)*

### 12. Anki settings the deck depends on
The scaffold only works if Anki shows new cards in deck order. In deck options set **New card gather order: Ascending position** and **New card sort order: Order gathered**, and keep new cards/day modest (about 20 new/day produces roughly 200 reviews/day). Put this in the deck description. A Part 2 deck assumes Part 1 is fully learned; say so too. *(Anki manual.)*

### Verify before shipping
Build a lexicon from the prerequisite deck plus each earlier card, segment every sentence card against it (dynamic programming, fewest unknown characters), and flag any sentence with untaught characters. Target: zero flagged sentences. Also check for orphan vocab (rule 6), long vocab runs (rule 3), and adjacent set members (rule 4). The original Part 2 deck failed the first check with 174 flagged sentences and was replaced by `recall_conversational_chinese_part2_v2.json`, which passes.

### Sources
- Wozniak, *Twenty rules of formulating knowledge* — https://www.supermemo.com/en/blog/twenty-rules-of-formulating-knowledge
- Tinkham 1997, semantic vs thematic clustering — https://journals.sagepub.com/doi/10.1191/026765897672376469
- Waring 1997, semantic sets replication — https://www.sciencedirect.com/science/article/abs/pii/S0346251X97000134
- Erten & Tekin 2008, semantic sets — https://www.sciencedirect.com/science/article/abs/pii/S0346251X08000420
- Nation 2000, *Learning vocabulary in lexical sets* — https://onlinelibrary.wiley.com/doi/10.1002/j.1949-3533.2000.tb00239.x
- Nakata & Suzuki 2019, blocking vs interleaving grammar — https://onlinelibrary.wiley.com/doi/abs/10.1111/modl.12581
- Learning direction in retrieval practice (SSLA) — https://www.cambridge.org/core/journals/studies-in-second-language-acquisition/article/abs/effects-of-learning-direction-in-retrieval-practice-on-efl-vocabulary-learning/159EE50F4B8835207764FB1B11077F29
- Boers et al. 2006, formulaic sequences and oral proficiency — https://www.researchgate.net/publication/258169489_Formulaic_sequences_and_perceived_oral_proficiency_putting_a_Lexical_Approach_to_the_test
- Expertise reversal effect — https://www.cambridge.org/core/books/cambridge-handbook-of-expertise-and-expert-performance/cognitive-load-and-expertise-reversal/03F656FD334F23214426ACB4118FEBF9
- Wilkinson 2020, deliberate learning from word cards — https://vli-journal.org/wp/wp-content/uploads/2021/08/VLI_9_2_9_wilkinson.pdf
- Anki manual, deck options — https://docs.ankiweb.net/deck-options.html

## Source-book decks

When a deck is built from a source text (Persian decks in `decks/Persian/`), only make cards the book itself translates directly. Skip unglossed material rather than filling gaps from outside sources.
