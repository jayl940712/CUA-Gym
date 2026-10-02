from common import an, REDDIT_ENV

E = REDDIT_ENV
NEWEST = ("NEWEST IS AMBIGUOUS (CORRECTIONS #21/#37, measured three times independently): /f/X/new "
          "sorts by id DESC (listing.js:34), not by timestamp, and the two orders disagree at the head "
          "of 59 of the 95 forums - only 35-36 are clean. f/DIY's /new head is id 119019 at 2023-03-31 "
          "19:01 while id 118903 is dated 23:55, later in time and lower in id, and Time.jsx:12 exposes "
          "the absolute datetime in the title/datetime attributes so BOTH readings are available and "
          "defensible. All three entities the census hands out for 'newest' (f/DIY 119019, f/space "
          "134164, f/Futurology 119517) are in the AMBIGUOUS set. Draw only from the clean 36 or name "
          "the intended order in the instruction. Tightest coincident margins among the clean set: "
          "f/aww 3m51s, f/dataisbeautiful 5m11s, f/wallstreetbets 8m14s, f/memes 9m52s, f/newhaven 11m18s.")
TITLELINK = ("Reddit submission TITLES are external links (Submission.jsx:120-126) - a replay that "
             "clicks a title navigates off-site and the run fails. The in-app route to a post's own "
             "page is the comment-count link in nav.submission__nav. The exception is image posts: "
             "currentUser.submissionLinkDestination is 'url', so their title link points at "
             "/submission_images/<file>.")
COUNTS = ("CORRECTIONS #49: the stored commentCount disagrees with the rendered comment rows for 6,475 "
          "of 8,012 submissions (81%), often by a lot (118568 stores 16 and holds 2). No task may "
          "branch on, count, or write back a SUBMISSION's comment count from either surface. "
          "CORRECTIONS #31: users[].submissionCount is a live-site total that disagrees with the "
          "rendered rows for every user (chrisdh79 424 vs 39; the dangerous one is Hrekires, 11 stored "
          "vs 10 rendered) - ground truth for any post count is the row count computed the way "
          "UserPage.jsx:41 computes it. Counting a user's own comment ROWS on /user/{n}/comments is a "
          "different and legitimate derivation; that is what official 0-4 do.")
HOTISTOP = ("CORRECTIONS #25/#29: ranking == netScore for 8,011 of the 8,012 seeded submissions, so the "
            "full Hot ordering EQUALS the full Top ordering in 94 of 95 forums (f/MachineLearning "
            "differs only because of the fixture submission 1). /f/X/top?t=all therefore renders "
            "exactly what /f/X renders, in the same order, and an agent that never touches the sort "
            "control or the time filter still lands on the right row - the R5 skill is unobservable in "
            "the reward. Fix it with injection as a design tool: republish the target through "
            "submissionEdits with ranking lowered to roughly position 40 of Hot (page 2, listings page "
            "at 25) while leaving netScore untouched, so Top and Hot genuinely differ. Ask of every "
            "task: would an agent that skipped the retrieval still succeed?")
RANKCONV = ("CORRECTIONS #24: there are TWO legitimate ranking conventions. A row standing in for "
            "pre-existing corpus content takes ranking == netScore; a row standing in for something the "
            "user posted takes epoch seconds, because that is what createSubmission writes (submission 1 "
            "carries 1686590745). Copying the epoch value onto a corpus-lookalike puts it above all "
            "8,012 on Hot. Say which convention is used in metadata.injected_preconditions.")

REDDIT = [
{
 "slug": "newest_thread_upvote",
 "skills": ["R4", "A9"],
 "chain": "identify the newest post in a named forum under a stated ordering, then upvote it",
 "entities": "draw from the 35-36 forums whose id order and timestamp order coincide at the head; f/aww (3m51s), f/dataisbeautiful (5m11s), f/wallstreetbets (8m14s), f/memes (9m52s), f/newhaven (11m18s) are the tightest of those and are still unambiguous. Ids are unique so the ordinal never ties; 25 vote forms render per listing page.",
 "writeback": "votes.submissions[\"<id>\"] = 1 (AppContext.jsx:321), plus the form's class flipping to vote--user-upvoted",
 "notes": E + " " + NEWEST + " " + TITLELINK + " " + COUNTS + " On a fresh seed / renders an empty 'Featured forums' shell (0 featured forums, 0 subscriptions), so either inject subscriptions to make the front page a real listing or route through the Forums index. " + RANKCONV + " CORRECTIONS #109: if a variant RETRACTS a vote instead of casting one, AppContext.jsx:329-333 deletes the key rather than zeroing it, so there is no 0 to gate on - gate the whole rubric on a positive marker elsewhere (the seed's untouched votes.submissions[\"1\"] == 1 plus a forums row) or the empty state scores. Batch-5 adjacent: newest_post_upvote_reply (R4->A9->A8); batch 6 keeps only the vote.",
 "analogues": an("reddit", 14, 15, 17, 18),
},
{
 "slug": "newest_thread_reply",
 "skills": ["R4", "A8"],
 "chain": "identify the newest post in a named forum, then post a comment (or a reply to a comment already in it)",
 "entities": "same clean-36 pool as newest_thread_upvote. Deep trees for a reply-to-a-comment variant: 13170 (IAmA), 59421 (books), 69404 (singularity). New comment ids allocate from 3000000; posting redirects to /f/{forum}/{sid}/{slug}/comment/{cid}.",
 "writeback": "newComments[] (AppContext.jsx:450 addComment)",
 "notes": E + " " + NEWEST + " " + TITLELINK + " " + COUNTS + " Unlike gitlab, reddit DOES have a per-comment Reply control (Comment.jsx:98, :261), so 'reply to the first reply' is expressible here - but the reply target must be identified by author and body, never by a comment count. Moderator action on another user's comment or submission is unreachable by clicking: Comment.jsx:120 and Submission.jsx:203 gate Delete/Edit on isOwn with no moderator branch, and mod_delete has no route in App.jsx - so no variant may delete or edit someone else's content. " + RANKCONV,
 "analogues": an("reddit", 19, 20, 90, 91),
},
{
 "slug": "active_top_titles_bio",
 "skills": ["R4", "A7"],
 "chain": "read the titles of the top N posts of a forum under a stated ordering, then write them in that order into my biography",
 "entities": "f/DIY/active top-5 are distinct to the minute (23:55:04 / 23:53:26 / 23:52:52 / 23:52:27 / 23:50:31); the same shape holds for books, space and technology. Prefer the ACTIVE ordering (lastActive) over Top, because it genuinely differs from the default Hot view.",
 "writeback": "currentUser.biography (updateBio, AppContext.jsx:622) - probed live setting it to 'DIY top post: 5649 points'",
 "notes": E + " " + HOTISTOP + " That is why this lane claims R4 over the ACTIVE ordering rather than R5 over Top: active is ordered by lastActive and is not a re-render of Hot. " + TITLELINK + " " + COUNTS + " Cross-site A7 is impossible - 22 of the 129 official instances (17%) carry text from gitlab or shopping and there is no cross-origin access; re-point the writeback at one of the six verified reddit vessels (post body, comment body, biography, private-message body, block reason, created-forum description/sidebar). Do NOT pre-place the source text in a reddit field: that hands the agent the answer and destroys the skill. CORRECTIONS #26: a clean top-1 margin does not license a top-N - check rank N against rank N+1 for the exact slice. Batch-5 adjacent: active_posts_into_bio.",
 "analogues": an("reddit", 25, 26, 5, 7),
},
{
 "slug": "top_post_page_subscribe",
 "skills": ["R4", "A3"],
 "chain": "navigate to the page of the forum's Nth-ranked post under a stated ordering, then subscribe to the forum from there",
 "entities": "top-ever has ZERO ties in any of the 95 forums; wide margins at f/space 14304 vs 12645, f/gadgets 11533 vs 7737, f/history 9675 vs 6133, f/books 3591. Most-commented ties in exactly four forums at rank 1 - news (219=219), dataisbeautiful (201), vermont (206), BridgeportCT (10) - and f/history additionally carries a THREE-WAY tie at 206 across ranks 2-4, invisible to a rank-1 audit. Safe most-commented margins >=5: Pennsylvania 244/214, nyc 238/223, jerseycity 230/156, massachusetts 224/212, Maine 218/201, television 218/209, boston 216/200, wallstreetbets 215/205, gadgets 214/207, tifu 214/209, technology 213/207, IAmA 212/193, food 212/204, space 212/206, washingtondc 212/202.",
 "writeback": "subscriptions[] + forums[i].subscriberCount (subscribe, AppContext.jsx:351); the front page stops being an empty shell and #sidebar > section becomes 'Subscribed forums' (the webarena-595..599 locator)",
 "notes": E + " " + HOTISTOP + " " + TITLELINK + " " + COUNTS + " Never phrase the ordinal as 'the most controversial post' - that is a ~10-way tie at netScore 0 in nearly every forum (books 10, DIY 10, movies 13, technology 12) and min(netScore) is 0 in all 95, so the corpus contains no negatively-scored submission at all and injecting one is out of envelope. CORRECTIONS #26 applies to every top-N here. The Subscribe button is [probed] present on the served build despite Sidebars.jsx being stale. Batch-5 adjacent: subscribe_from_superlative_post (R5->R4->A3) - batch 6 drops the faceted step and states the ordering.",
 "analogues": an("reddit", 35, 36, 38, 39),
},
{
 "slug": "all_time_top_downvote",
 "skills": ["R5", "A9"],
 "chain": "switch the listing sort to Top and the time window off the default day to All time, then thumbs-down the Nth row it produces",
 "entities": "zero top-ever ties in any of the 95 forums; tightest are pics 7522 vs 7502 (20), deeplearning 173 vs 168 (5), WorcesterMA 222 vs 207 (15). Wide: f/space 14304/12645, f/gadgets 11533/7737, f/history 9675/6133. Sort menu on /f/DIY emits exactly hot, new, active, top?t=day, controversial?t=day, most_commented?t=day; the time menu emits day/week/month/year/all.",
 "writeback": "votes.submissions[\"<id>\"] = -1; the form class becomes 'vote vote--user-downvoted'",
 "notes": E + " The R5 step is real and source-faithful: ListNav.jsx:58-60 appends ?t=day to Top/Controversial/Most-commented, and every ?t= value but 'all' returns ZERO rows because the corpus ends 2023-03-31 while 'today' is 2026, so the agent must then open the time dropdown. BUT " + HOTISTOP + " Every task in this lane must ship the ranking injection, or drop the R5 claim and relabel R4. Do not touch f/MachineLearning - its hottest post is always submission 1, a fixture artefact with ranking 1686590745. " + RANKCONV + " " + TITLELINK + " CORRECTIONS #26 applies to every top-N. Batch-5 adjacent: top_ever_post_downvote.",
 "analogues": an("reddit", 106, 107, 108, 110),
},
{
 "slug": "ranked_forum_dictated_post",
 "skills": ["R5", "A2"],
 "chain": "rank the forum index by a stated facet to identify which forum to post in, then submit the dictated post there",
 "entities": "forum index sorts are by_name, by_title, by_submissions, by_subscribers, by_creation_date (ForumsIndexPage.jsx:38-60, dropdown at :150-166). by_submissions: AskReddit 10,041, relationship_advice 5,718 - margin 4,323, clean. by_subscribers is a 95-WAY TIE at 0. by_creation_date's 78 forums share the date 2022-10-01. /submit exposes #submission_forum over all 95 forums, URL/Image/Text tabs, #submission_title, #submission_body.",
 "writeback": "newSubmissions[] (.forum, .title, .body/.url) via createSubmission, AppContext.jsx:384",
 "notes": E + " Keep the title, body and forum-selection RULE dictated so this stays the pure A2 creation form with only the target derived. CORRECTIONS #47: there is no ascending submission sort - by_submissions is DESC-only with no direction toggle, so 'the smallest forum' means paging to the TAIL (95 forums at 25/page = 4 pages), which is a legitimate and slightly harder R5. CORRECTIONS #32: /forums uses numbered OffsetPagination, not the 'More' cursor pager used by submission listings; a[rel=\"next\"] is the portable selector for both. CORRECTIONS #34: the 78-forum creation-date collision is NOT a data tie (timestamps differ to the second and sortForums compares the full ISO string) - what kills it is that ForumCard never renders a creation date at all, so the only signal is last-position-in-sort; a data tie is fixable by injection and an unrendered field is not. CORRECTIONS #35: never make the retrieval 'the most recently created X' when the agent creates an X during the episode - createForum stamps created: nowIso() and the agent's own row becomes the answer. createSubmission writes ranking as EPOCH SECONDS, which is correct for an agent-created row and is why a created post tops Hot. " + RANKCONV,
 "analogues": an("reddit", 80, 83, 85, 86),
},
{
 "slug": "ranked_row_direct_message",
 "skills": ["R5", "A7"],
 "chain": "read the title or score of the Nth row of a listing under a stated sort and time filter, then send its author a private message quoting that value",
 "entities": "same top-ever pool as all_time_top_downvote (zero ties in all 95 forums). Author profiles resolve for all 21,038 directory names (AppContext.jsx:288-300). Compose route: any byline -> /user/{n} -> Send message.",
 "writeback": "messages[0].messages[0].body (ComposeMessagePage.jsx:61) - probed live persisting 'DIY newest post is id 119019'",
 "notes": E + " " + HOTISTOP + " This lane's R5 claim needs the same ranking injection, or it is R4 in disguise. " + COUNTS + " The value quoted must be a title, a score or an id - never a comment count. Profile sidebars show only username, join date and bio, and every non-current-user bio is an opaque reddit token (probed: /user/ziostraccette reads 't2_2lbftn79'), so nothing on the profile is a usable derived value. " + TITLELINK + " Six A7 vessels exist and are all verified live (post body, comment body, biography, DM body, block reason, created-forum description/sidebar) - spreading across them is what keeps A7 lanes from collapsing onto one reward shape.",
 "analogues": an("reddit", 5, 6, 8, 26),
},
{
 "slug": "right_forum_for_question",
 "skills": ["R8", "A2"],
 "chain": "choose, from the 95 forum names, the forum where the described question would actually get an answer, then post the dictated question there",
 "entities": "consoles, gaming, headphones, nyc, pittsburgh, washingtondc, philadelphia, boston, relationship_advice, personalfinance, deeplearning, MachineLearning, singularity, books, DIY, food, technology.",
 "writeback": "newSubmissions[].forum + .title + .body",
 "notes": E + " title == description == name for ALL 95 forums (verified over src/data/forums.json) and sidebar is an opaque t5_* reddit id, so there is NO descriptive prose to reason over - the semantic match is on the forum NAME alone, and any 'read the description to decide' variant is ruled out. Several topics have two defensible homes (gaming vs consoles; MachineLearning vs deeplearning vs singularity; nyc vs a generic city forum) - either the instruction disambiguates or the reward accepts an author-enumerated forum set. Do not reproduce official 40-49 or 75-79 strings. Batch-5 adjacent: forum_choice_post_and_comment (R8->A2->A8->A12) - batch 6 keeps only the first two skills, and the comment-on-your-own-post half must not reappear here.",
 "analogues": an("reddit", 40, 41, 45, 75),
},
{
 "slug": "interest_forum_bulk_subscribe",
 "skills": ["R8", "A4"],
 "chain": "identify every forum on the index that belongs to a described category, then apply the same action (subscribe / hide) to the whole matched set",
 "entities": "ENUMERATE the matched set against src/data/forums.json - never from a census sample. The city/local-news family includes at least nyc, boston, philadelphia, washingtondc, pittsburgh, jerseycity, Newark, Hartford, newhaven, StamfordCT, WaterburyCT, BridgeportCT, yonkers, lakewood, Paterson, allentown, ManchesterNH, LowellMA, WorcesterMA, arlingtonva, columbiamd, vermont, Maine, massachusetts, Pennsylvania. Forum index pages at 25, so a set larger than 25 spans pages.",
 "writeback": "subscriptions[] (exact resulting array) + forums[i].subscriberCount; or hiddenForums[] (hideForum, AppContext.jsx:641)",
 "notes": E + " CORRECTIONS #46: 'seven reddit forums under 100 submissions' is really FOURTEEN and the census list omits BridgeportCT (4) entirely, plus the whole 55-76 band (arlingtonva 55, Documentaries 59, listentothis 62, ManchesterNH 62, Hartford 71, LowellMA 76). Treat every census list as a sample, never an enumeration. Assert the EXACT resulting collection, not a count (TASK4 S3.3). CORRECTIONS #110: a distractor - 'the neighbouring forum was NOT subscribed' - is true on {} by construction and can NEVER carry weight of its own; express it as a GATE that withdraws the paid components, so an over-broad sweep scores 0.0 rather than a docked 0.6, and do not list exclusion_constraint in hard_criteria because it is enforced, not scored. Never phrase the retrieval as a subscriber superlative: all 95 forums have subscriberCount 0. CORRECTIONS #48: an injection must not create a contradiction visible on one screen - card counts and rendered listings AGREE exactly for every forum below 50 submissions (Paterson 1/1, BridgeportCT 4/4, coolgithubprojects 45/45), and only diverge well above that (news 3,322 card vs 113 rows).",
 "analogues": an("reddit", 111, 116, 121, 122),
},
{
 "slug": "image_repost_carry_url",
 "skills": ["R6", "A2"],
 "chain": "find the described image post by searching the corpus, then re-post it into a second forum carrying its image URL",
 "entities": "'A Trejo Thanksgiving' 45604; the f/pics top-ever post (7522 vs 7502, margin 20). Probed search behaviour: 'honeycomb firewood' -> 1 result, 'bookshop.org' -> 14, 'Ted Lasso' -> 1, 'jaw bruxism' -> No results.",
 "writeback": "newSubmissions[].url + .title + .forum",
 "notes": E + " CORRECTIONS #30: this flow IS fully click-reachable, resolving a census 'not drive-verified' item. currentUser.submissionLinkDestination is 'url', so Submission.jsx:71-77 points an image post's TITLE link at /submission_images/<file> directly; clicking it navigates to the picture and the address bar then holds the absolute URL, so the ^https?:// promotion needs no typed or constructed URL. The validator that actually executes is SubmitPage.jsx:121-124, not EditSubmissionPage.jsx:70 (they agree, but the census justified it from a handler this flow never runs). Corollary: for image posts the permalink page is NOT reachable via the title - use the comment-count link in nav.submission__nav. All 2,748 files in dist/submission_images/ are referenced by a seeded post; there are no spares, so an injected image post must reuse a file. Search is capped at MAX_RESULTS = 50 (SearchPage.jsx:43) and returns fewer hits than the source's Postgres FTS (14 vs 32 on bookshop.org) - fine for new tasks, but never reuse an official expected answer, and never count anything whose true count could reach 50. Batch-5 adjacent: image_repost_cross_forum.",
 "analogues": an("reddit", 55, 56, 57, 59),
},
{
 "slug": "search_thread_comment",
 "skills": ["R6", "A8"],
 "chain": "locate the thread by a phrase in its title, body or comments, then comment on it",
 "entities": "search is a token-AND substring match over submission title+body and comment body (SearchPage.jsx:45-60). Deep comment trees 13170 (IAmA), 59421 (books), 69404 (singularity). The per-forum comment firehose /f/{forum}/comments is also a real entry point - registered at App.jsx:124, reached by a rendered Comments tab (ListNav.jsx:167-174), fixed newest-first, every row carrying an author byline (CommentRow.jsx:103).",
 "writeback": "newComments[]",
 "notes": E + " CORRECTIONS #33: the comment firehose is a whole click-reachable surface the census never enumerated, and it is why the block-a-user entity ceiling of '~5' was a property of one join rather than of the site. " + COUNTS + " " + TITLELINK + " Search truncates silently at 50. Moderation of individual content is unreachable: Comment.jsx:120 and Submission.jsx:203 gate Delete/Edit on isOwn with no moderator branch, grep for moderates|isMod over those files returns nothing, and mod_delete has no <Route> - injecting moderatorOf unlocks only forum-LEVEL surfaces. Batch-5 adjacent: reply_top_comment_quote_score (R4->R9->A7->A8) - batch 6 keeps the search and the comment and drops the quoted score, which belongs to ranked_row_direct_message.",
 "analogues": an("reddit", 92, 50, 52, 19),
},
{
 "slug": "named_own_post_body_line",
 "skills": ["R9", "A1"],
 "chain": "open the named own submission, then set its body to the stated line",
 "entities": "the current user's 46 submissions: 30 in f/television, 15 in f/movies, 1 in f/MachineLearning. Named targets: The Night Agent 134868, Ted Lasso season 3 135156, Star Trek: Starfleet Academy 135201. Highest-scoring own post 49068 at 8,549 (runner-up 5,268 - clean); within f/television 8,549 vs 4,513 (clean); within f/movies 5,268 vs 2,792 (clean).",
 "writeback": "submissionEdits[\"<id>\"] - a FULL RECORD REPLACEMENT, not a field patch (SCHEMA.md:253)",
 "notes": E + " CORRECTIONS #23: 45 of the 46 own submissions have NO body key at all - 43 are link posts and 2 are image posts. The single exception is submission 1 ('Nvidia RTX 4090', body 'Crazy device for ML!'), which IS official webarena-731 and must be avoided for contamination. So the correct rubric is body == <the stated line>, NOT <original> + <line>, and the official corpus agrees with the data rather than with the census: 731 is the only one of the five R9->A1 edit tasks scored must_include on both lines, while 732-735 are exact_match on the new line alone. Post edit is author-only (EditSubmissionPage.jsx:51) and delete likewise (DeleteSubmissionPage.jsx:30, probed 403 on another user's post). 'My lowest-scoring post' is a SEVEN-WAY TIE at netScore 0 (128812, 128823, 128824, 135191, 135199, 135201, 135204) - never use the minimum without raising six of the seven through submissionEdits. Gate the reward on the VALUE, never on 'was edited': AccountPage writes currentUser.email on every submit even when unchanged (SCHEMA.md:296). Batch-5 adjacent: own_post_append_edit.",
 "analogues": an("reddit", 123, 124, 125, 126),
},
{
 "slug": "short_url_forum_post",
 "skills": ["R9", "A2"],
 "chain": "resolve a submission named only by its short URL or id to the forum it lives in, then create the dictated post in that same forum",
 "entities": "the short URL renders as <kbd class=\"submission-meta__short-url\"> and was probed live as http://localhost:8002/97998 (Sidebars.jsx:172); the /{id} shortcut route resolves any of the 8,012 submissions. Example anchors: 97998 (DIY), 1 (MachineLearning - avoid, it is a fixture and official webarena-731's subject), 59421 (books), 13170 (IAmA).",
 "writeback": "newSubmissions[].forum + .title + .body",
 "notes": E + " The retrieval is load-bearing precisely because the instruction never names the forum - the agent must open the id to learn it. Verify the anchor is not one the official corpus names. " + TITLELINK + " The short-url <kbd> is [probed] present on the served build. Keep the created post's title and body dictated so the action stays A2. createSubmission writes ranking as epoch seconds (" + RANKCONV + ") and the created row therefore tops Hot, which is fine here but is why " + "CORRECTIONS #35 forbids pairing this with a 'most recently created' retrieval.",
 "analogues": an("reddit", 85, 86, 88, 89),
},
{
 "slug": "author_submission_tally_vessel",
 "skills": ["R3", "A7"],
 "chain": "count an author's submissions within a stated scope by paging their listing, then write that number into a reddit vessel",
 "entities": "verified row counts: chrisdh79 39 site-wide, marketrent 28, giuliomagnifico 15, IAI_Admin 27 in f/philosophy, chrisdh79 19 in f/gadgets, Sariel007 16 in f/UpliftingNews, marketrent 14 in f/history, lnfinity 13 in f/gifs, Hrekires 10 in f/news, UniversityofBath 8 in f/IAmA. Listings page at 25, so several of these are one page and marketrent/chrisdh79 site-wide are two.",
 "writeback": "any one of the six vessels - currentUser.biography, newSubmissions[].body, newComments[].body, messages[i].messages[j].body, blockedUsers[].comment, or a created forum's description/sidebar",
 "notes": E + " " + COUNTS + " This is the trap that matters here: Hrekires stores 11 and renders 10, a one-apart gap that survives a spot check and would fail every correct agent. Compute ground truth as the row count the way UserPage.jsx:41 does. Do NOT count via /search - MAX_RESULTS is 50 and both the mock and the live source cap there, so any true count near 50 renders silently wrong. Never ask 'how many posts are in f/X': the forum card shows the source DB's submissionCount (news 3,322) while the listing holds 113 rows, and the two disagree by design above ~50 submissions (they agree exactly below it - CORRECTIONS #48). Two official A4 targets do not exist in the seed: FTorrez81 has 0 posts in iphone13 (no such forum) and jacyanthis has 0 in EarthPorn. Batch-5 adjacent: dm_author_post_count (R4->R7->R3->A7) - batch 6 names the author and keeps only the count and the write.",
 "analogues": an("reddit", 5, 6, 8, 25),
},
{
 "slug": "two_hop_negative_comment_note",
 "skills": ["R7", "A7"],
 "chain": "join a post to its author's profile, count that author's below-zero-score comments by paging their comments tab, then record the number in a block reason or message",
 "entities": "the newest-post-author join is DEGENERATE - the answer is 0 for 85 of the 95 forums. The non-trivial ones are DIY -> ziostraccette (1 negative of 7 comments, one page), WorcesterMA -> mineinhusdson (1 of 42, two pages), lakewood -> WilliamInnes (2 of 2), Newark -> redditfindsaway (1 of 3); MechanicalKeyboards/philadelphia -> AutoModerator (20 of 490, twenty pages) and BridgeportCT/yonkers -> [deleted] (3,096 comments) are both infeasible. The real pool is much larger: corpus-wide 1,065 authors have at least one below-zero comment and 53 have two or more within a single 25-row page, reachable via the /f/{forum}/comments firehose byline.",
 "writeback": "blockedUsers[].comment (blockUser, AppContext.jsx:661) or messages[i].messages[j].body",
 "notes": E + " CORRECTIONS #33: the ~5-entity ceiling the census gives for this topic is a property of ONE join (newest-post-author), not of the site - R7 only needs a two-hop byline, and the per-forum comment firehose supplies 1,065 candidate authors. The binding constraint is click-reachability, not entity supply. " + COUNTS + " Counting a user's own comment ROWS is legitimate and is exactly what official 0-4 do; what is forbidden is a SUBMISSION's comment count. Profile sidebars show no aggregate counts at all (UserSidebar.jsx:52-113 renders username, join date and bio only), and users[].commentCount / negativeCommentCount are writable keys that change no pixel - counting always means paging a tab. CORRECTIONS #27: injecting votes.comments moves no rendered score and no ordering (Vote.jsx reads the map only to choose a CSS class; the number and buildTree's netScore DESC both come from the record's own netScore) - to move a comment's rank, replace the whole record through commentEdits[<id>], which overlay.resolveComment:210 and mergeComments:120 do consume. /user/{n}/comments sorts timestamp DESC, id DESC, so an injected comment needs a recent timestamp or it lands past page 1. Batch-5 adjacent: block_user_with_negative_count.",
 "analogues": an("reddit", 0, 1, 2, 3),
},
]
