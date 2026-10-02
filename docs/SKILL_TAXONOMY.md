# WebArena skill taxonomy — derived from the 686 in-scope official tasks

Built by reading all 583 distinct intent templates in
`webarena_benchmarks/webarena.jsonl` that target a site we host
(gitlab 193, shopping 165, shopping_admin 153, reddit 95 templates;
686 task instances). Map and wikipedia are excluded — we have no mock.

This file exists because batches 1–4 aligned on *intent shape* and scoring
style, and never on **skill**. A task can look like a WebArena task, score like
one, and still exercise nothing the benchmark exercises. Skill is the thing that
transfers.

## The two axes

Every official task decomposes into **how the target is identified** (retrieval)
and **what is then done to it** (action). Official tasks are usually one of
each; the string_match half stops after retrieval, the program_html half runs
both. Naming the axes separately is what makes composition possible: a new task
is a chosen (R, A) pair, and a hard task is a chain of them where one's output
is the next's input.

### Axis R — retrieval / locate skills

| id | skill | official evidence |
|---|---|---|
| R1 | superlative under a filter | "best rating in Men's shoes with >=5 reviews and least expensive"; "top-1 best-selling product in 2022"; "most starred Covid location tracker" |
| R2 | temporal filter + relative-date arithmetic | "commits between Feb 2023 and May 2023"; "fulfilled orders over the past month (today is 6/12/2023)"; "refund report for Q1 (today is March 15, 2023)" |
| R3 | count / sum / range over a filtered set | "price range for products from ugreen"; "total payment of the last 5 pending orders"; "reviews mentioning 'disappointed'" |
| R4 | ordinal selection | "second most number of orders"; "my oldest order in 2023"; "top 3 contributors"; "the newest post" |
| R5 | faceted list navigation | category + price filter + sort; issues by label and state; order grid by status |
| R6 | text / semantic search inside content | "reviewers who mention ear cups being small"; "posts that recommend exactly one book"; "orders suspected of being fraudulent" |
| R7 | cross-entity join (two hops) | "the user who made the latest post on DIY -> count of their downvoted comments"; "customer with most cancellations -> their order SKUs" |
| R8 | semantic category matching | "a forum where I'm likely to get an answer"; "something that could alleviate jaw bruxism"; "the right template to speed up development" |
| R9 | attribute lookup on a named record | "shipping method for order 187"; "size configuration of the picture frame I bought Sep 2022" |
| R10 | report configuration | admin Reports with a date range and period granularity |

### Axis A — action / mutation skills

| id | skill | official evidence |
|---|---|---|
| A1 | single-field edit | gitlab status; bio; homepage URL; 404 page title |
| A2 | multi-field creation form | "simple product, 50 in stock, size S, colour blue, $60, attribute set top"; forum with name+title+description+sidebar; cart price rule |
| A3 | membership / permission grant | "add abisubramanya27 and lahwaacz as developer"; "invite him as a guest"; new group with members |
| A4 | bulk apply over a matched set | "like all submissions created by X"; "delete all pending reviews with less than 4 stars"; "mark all Aeon capri as out of stock" |
| A5 | arithmetic value mutation | "reduce by $5"; "increase by 23%"; "if previous stock exists, add to it" |
| A6 | variant / attribute-matrix edit | "add size 30 and 31 to all colour variants"; "add colour brown to size S" |
| A7 | content composition with transferred text | README containing links to the 5 most active DIY posts; post body carrying the repo description and link; "{count} customer(s) love it!" |
| A8 | comment / reply in thread context | "reply to the first reply"; "reply to the manager of the website in this post"; comment on the post you just created |
| A9 | vote / react | "upvote the newest post"; "thumbs down the top 3 post ever" |
| A10 | lifecycle transition | cancel order; approve review; disable product; close issue |
| A11 | address / contact record edit | billing address of order #299; account address after moving |
| A12 | create-then-link | create issue then assign; create project then add members; create MR then assign reviewer |
| A13 | conditional action | "if the last comment is from the author, reply 'Thank you'; otherwise tag the author" |

## Composition rules for batch 5

A task is a **skill chain**: an ordered list of (R|A) ids where each step's
output is consumed by the next.

* **medium** — 2 skills, at least one from each axis. `R4 -> A9` ("upvote the
  newest post") is the canonical official medium.
* **hard** — 3+ skills with at least two distinct retrieval skills OR a
  retrieval feeding two dependent actions. `R2 -> R3 -> A7` ("compute last
  year's shipping revenue, write it into a CMS block") is the canonical hard.

**Compose naturally, not combinatorially.** `R8 -> A2` (find the right forum,
then create a well-formed post there) is a real user story. `R10 -> A6` (run a
sales report, then edit a size/colour matrix) is two unrelated chores stapled
together, and an agent that learns it learns nothing transferable. The test is
whether a real person would ever have this as one errand.

## Skills that need the prerequisite-then-writeback framing

R5 and R10 terminate in a **view**, not persisted state. 187 official tasks are
scored on URL alone. Our nemo-side reward sees state only, so these cannot be
graded directly.

They are captured by making the view **the only route to a value**, and scoring
the value once written:

* official `url_match`: "Go to the page showing PS4 accessories sorted by
  ascending price" -> ours: "Add the cheapest PS4 accessory to my wish list".
* official `program_html`: "Show the shipping report from August 5, 2022 to
  March 1, 2023" -> ours: "Log last year's shipping revenue in the store's
  ledger" (2022 = 215 orders / $3,145.00, a real aggregate over 516 seeded rows).

  Note the example that does NOT work. "Log last quarter's refund total" reads
  well and is dead on arrival: the shopping_admin mock's `refunded_aggregated`
  holds a single row dated 2023-04-19, so Q1 2023 returns zero rows. Every
  report-derived figure must be checked against the seed before a task is
  designed around it — `output/census/shopping_admin.md` records which reports
  have data and which are permanently empty.

**The known limitation:** the skill is exercised but graded indirectly, so an
agent reaching the value by another route still scores. Mitigate by choosing
targets with no practical alternative route — a figure only the dated report
computes, a superlative over a set too large to eyeball. Do not pretend this is
closed; record it per task.

## What this replaces

Batches 1–4 chose tasks by **topic** ("gitlab labels", "reddit moderation").
Batch 5 chooses by **skill chain**, and topic is only the material the chain is
expressed in. Every bundle records:

```json
"metadata": {
  "skills": ["R2", "R3", "A7"],
  "skill_chain": "date-range report -> sum -> write the figure into a CMS block",
  "official_analogues": ["Show the shipping report from August 5, 2022 to March 1, 2023."]
}
```

`official_analogues` is the honesty check: if an author cannot name a real
benchmark task the design is aimed at, the design is not in-distribution and
the claim should be dropped rather than invented.
