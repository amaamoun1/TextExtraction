/******************************************************************************
Yann Decressin: 
Purpose: Create dummies for individuals with crazy estimates
Input: 	
Output: ""
		 
******************************************************************************/
******************************************************************************
// Directories, log
clear all

global onedrive "C:\Users\ydecress\OneDrive - ghSMART\ghSMART_data"
global codefolder "C:\Users\ydecress\Desktop\Kaplan\TextExtraction\step6_analysis"
global outfolder "C:\Users\ydecress\Desktop\Kaplan\TextExtractionOutput"

cd "$codefolder"


********************************************************************************
**********    Prepare scorecard variables     ************
********************************************************************************



**** Grab the scorecard elements that were extracted using codes
import excel "$onedrive\extractions_merged_anonymized_deduplicated.xlsx", firstrow clear

*keep and rename important vars
keep doc_id* date_clean title_clean sc*
drop sc_present sc_outcomes_amount
rename sc_*_rating sc_rating*
rename sc_*_topic sc_topic*
rename sc_*_desc sc_desc*

gen year = substr(date_clean, 1, 4)
destring year, replace
drop date_clean

*keep ceos, coos, and cfos
keep if regexm(title_clean, "(coo|ceo|cfo)")
tabulate title_clean
drop if regexm(title_clean, "ceo succesion")
drop if regexm(title_clean, "^deputy")
drop if regexm(title_clean, "^division")
drop if regexm(title_clean, "^region")
drop if regexm(title_clean, "^assistant")
drop if regexm(title_clean, "office of ceo")
drop if regexm(title_clean, "region ceo")
tabulate title_clean


*reshape long and keep scorecard elements with topics
reshape long sc_topic sc_rating sc_desc, i(doc_id_old doc_id_new title_clean year) j(entry)
drop sc_growth_revenue-sc_strategy
drop if sc_desc == ""

*convert letters to numbers
gen sc_score = 4.3 if sc_rating=="a+"
replace sc_score = 4 if sc_rating=="a"
replace sc_score = 3.7 if sc_rating=="a-"
replace sc_score = 3.3 if sc_rating=="b+"
replace sc_score = 3 if sc_rating=="b"
replace sc_score = 2.7 if sc_rating=="b-"
replace sc_score = 2.3 if sc_rating=="c+"
replace sc_score = 2 if sc_rating=="c"
replace sc_score = 1.7 if sc_rating=="c-"

*combine all of the relations elements...we can do a more detailed analysis later
replace sc_topic="relations" if regexm(sc_topic, "^relations")

duplicates report doc_id_new entry
duplicates list doc_id_new entry
save "$outfolder\data\sc_ready_for_summstats.dta", replace



********************************************************************************
**********    Calculate Statistics     ************
********************************************************************************


*************************************
****    General     ****
*************************************

use "$outfolder\data\sc_ready_for_summstats.dta", clear
unique(doc_id_old doc_id_new)

*calculate counts on the topic level
use "$outfolder\data\sc_ready_for_summstats.dta", clear
drop if sc_topic==""
encode sc_topic, gen(sc_topic_code)
duplicates drop doc_id_old doc_id_new sc_topic, force

graph hbar (count) doc_id_new, over(sc_topic_code) ///
	yscale(range(2500)) yline(2304) ///
	title("no clear scorecard templates") ///
	ytitle("number of interviews")
graph export "$outfolder\plots_scorecard\sc_count_by_topic.png", replace


*calculate counts on the entry level
use "$outfolder\data\sc_ready_for_summstats.dta", clear
drop if sc_topic==""
collapse (count) doc_id_new, by(entry)
rename doc_id_new num_docs
gsort entry

two line num_docs entry, title("sharp dropoff after entry 6") ///
	ytitle("number of interviews") xtitle("entry number")
graph export "$outfolder\plots_scorecard\sc_count_by_entry.png", replace


*calculate percent evaluated by entry
use "$outfolder\data\sc_ready_for_summstats.dta", clear
drop if missing(sc_score)
gen sc_evaluated = !missing(sc_topic) & !missing(sc_desc)
collapse (mean) eval_mean = sc_evaluated (sum) eval_sum = sc_evaluated (count) num_docs = doc_id_new, by(entry)
keep if num_docs > 100

two line eval_mean entry, ylabel(0(0.10)1) title("generally high evaluation rate") ///
	xtitle("entry number") ytitle("percent of entries with topic evaluated")
graph export "$outfolder\plots_scorecard\sc_per_evaluated_by_entry.png", replace

label var num_docs "total number of entries"
label var eval_sum "number of entries evaluated"
two line num_docs eval_sum entry,  title("generally high evaluation rate") ///
	xtitle("entry number") ytitle("number of interviews")
graph export "$outfolder\plots_scorecard\sc_count_evaluated_by_entry.png", replace



*************************************
****    Topic Freq by Entry     ****
*************************************


*calculate counts on the entry - sc_topic level
use "$outfolder\data\sc_ready_for_summstats.dta", clear
drop if sc_topic==""
collapse (count) doc_id_new, by(entry sc_topic)
rename doc_id_new num_docs
egen num_entry = sum(num_docs), by(entry)
gen per_docs = num_docs / num_entry
gsort entry -num_docs

two line per_docs entry if entry<=11, by(sc_topic, title("growth topics tend to lead"))  ///
	xtitle("entry number") ytitle("percent of interviews")
graph export "$outfolder\plots_scorecard\sc_per_by_topicentry.png", replace

two line num_docs entry if entry<=11, by(sc_topic, title("growth topics tend to lead"))  ///
	xtitle("entry number") ytitle("number of interviews")
graph export "$outfolder\plots_scorecard\sc_counts_by_topicentry.png", replace


*calculate counts on the entry - sc_topic level...overlapping
use "$outfolder\data\sc_ready_for_summstats.dta", clear
drop if sc_topic==""
collapse (count) doc_id_new, by(entry sc_topic)
rename doc_id_new num_docs
egen num_topic = sum(num_docs), by(sc_topic)
egen num_entry = sum(num_docs), by(entry)
gen per_docs = num_docs / num_entry
gsort entry -num_docs
keep if num_topic>500
drop num_entry num_topic
reshape wide num_docs per_docs, i(entry) j(sc_topic) string
rename num_docs* *_n
rename per_docs* *_p

unab vars: *_n *_p
foreach var in `vars'  {
	label var `var' "`var'"
}

two line *_p entry if entry<=8, ///
	title("growth topics lead") ///
	xtitle("entry number") ytitle("percent of interviews") ///
	legend(position(3) cols(1))
graph export "$outfolder\plots_scorecard\sc_per_by_topicentry.png", replace

two line *_n entry if entry<=8, ///
	title("growth topics lead") ///
	xtitle("entry number") ytitle("percent of interviews") ///
	legend(position(3) cols(1))
graph export "$outfolder\plots_scorecard\sc_counts_by_topicentry.png", replace


*************************************
****    Topic Freq by Entry Over time     ****
*************************************

*topic counts over time
use "$outfolder\data\sc_ready_for_summstats.dta", clear
drop if sc_topic==""
egen num_topic = count(doc_id_new), by(sc_topic)
keep if num_topic>500
duplicates drop doc_id_old doc_id_new sc_topic, force

drop if missing(year)
keep if year>=2000 & year<=2019
collapse (count) doc_id_new, by(sc_topic year)
rename doc_id_new docs_topic
egen docs_year = sum(docs_topic), by(year)
gen per_topic = docs_topic / docs_year
gsort year -docs_year
gsort -per_topic

reshape wide docs_topic per_topic, i(year) j(sc_topic) string
rename docs_topic* d_*
rename per_topic* p_*

foreach var in d_culture d_deals d_exit d_finance d_growth_both d_growth_ebitda d_growth_revenue ///
	d_leader d_operations d_relations d_staffing d_strategy p_culture p_deals p_exit p_finance ///
	p_growth_both p_growth_ebitda p_growth_revenue ///
	p_leader p_operations p_relations p_staffing p_strategy {
	label var `var' "`var'"
}
twoway line d_* year, ///
	title("topics counts vary with no. interviews") ///
	xtitle("year") ytitle("no. of interviews") ///
	legend(position(3) cols(1)) 
graph export "$outfolder\plots_scorecard\sc_topiccounts_by_year.png", replace

twoway line p_* year, ///
	title("specific growth topics are in decline") ///
	legend(position(3) cols(1)) ytitle("per. of topics")
graph export "$outfolder\plots_scorecard\sc_topicper_by_year.png", replace

*topic ranks over time
use "$outfolder\data\sc_ready_for_summstats.dta", clear
drop if sc_topic==""
egen num_topic = count(doc_id_new), by(sc_topic)
keep if num_topic>500

drop if missing(year)
keep if year>=2000 & year<=2019
collapse (min) entry, by(doc_id_new sc_topic year)
collapse (mean) entry, by(sc_topic year)
sort sc_topic year

reshape wide entry, i(year) j(sc_topic) string
rename entry* *

foreach var in culture deals exit finance growth_both growth_ebitda growth_revenue ///
	leader operations relations staffing strategy {
	label var `var' "`var'"
}
twoway line culture-strategy year, ///
	title("topic rankings are fairly constant") ytitle("average entry number") ///
	legend(position(3) cols(1)) 
graph export "$outfolder\plots_scorecard\sc_topicentry_by_year.png", replace



*************************************
****    Topic Rating Dist.     ****
*************************************


*calculate rating quantiles by topic
use "$outfolder\data\sc_ready_for_summstats.dta", clear
drop if sc_topic==""
egen num_topic = count(sc_score), by(sc_topic)
keep if num_topic>500
reshape wide sc_score, i(doc_id_new entry) j(sc_topic) string
multqplot sc_score*, allobs combine(title("fairly consistent rating distributions")) ///
	ytitle("rating") xtitle("percentile")
graph export "$outfolder\plots_scorecard\sc_ratings_qplot_by_topic.png", replace

*calculate rating box and whisker by topic
use "$outfolder\data\sc_ready_for_summstats.dta", clear
drop if sc_topic==""
graph hbox sc_score, over(sc_topic) title("fairly consistent rating distributions") ///
	ytitle("rating")
graph export "$outfolder\plots_scorecard\sc_ratings_box_by_topic.png", replace

*calculate rating percents by topic
collapse (count) doc_id_new, by(sc_topic sc_score)
drop if missing(sc_score)
replace sc_score = sc_score * 10
rename doc_id_new num_ratings
egen num_topic = sum(num_ratings), by(sc_topic)
keep if num_topic>500
gen per_ratings = num_ratings/num_topic
keep if num_topic>500
drop num_*
reshape wide per_ratings, i(sc_score) j(sc_topic) string
replace sc_score = sc_score / 10

rename per_ratings* *_p
unab vars: *_p
foreach var in `vars'  {
	label var `var' "`var'"
}
graph twoway scatter *_p sc_score, ///
	title("fairly consistent rating distribution") xtitle("rating") ytitle("per. of topic") ///
	legend(position(3) cols(1))
graph export "$outfolder\plots_scorecard\sc_ratings_scatter_by_topic.png", replace



*************************************
****    Combine Revenue and Cost topics     ****
*************************************

use "$outfolder\data\sc_ready_for_summstats.dta", clear
drop if sc_topic==""
drop sc_rating sc_desc
collapse (mean) sc_score (min) entry, by(doc_id_new doc_id_old sc_topic title_clean year)
reshape wide sc_score entry, i(doc_id_new doc_id_old) j(sc_topic) string
rename sc_score* sc_*
rename entry* en_*

egen sc_revenue_broad = rowmean(sc_branding sc_expansion sc_growth_revenue sc_innovate)
egen sc_cost_broad = rowmean(sc_growth_ebitda sc_operations)
egen en_revenue_broad = rowmin(en_branding en_expansion en_growth_revenue en_innovate)
egen en_cost_broad = rowmin(en_growth_ebitda en_operations)

gen has_both_narrow = 1 if sc_growth_ebitda!=. & sc_growth_revenue!=.
gen has_both_broad = 1 if sc_rev!=. & sc_cost!=.

summarize
save "$outfolder\data\sc_ready_for_summstats_withbroad.dta", replace

*counts of narrow vs broad
use "$outfolder\data\sc_ready_for_summstats_withbroad.dta", clear
graph hbar (count) sc_growth_revenue sc_growth_ebitda has_both_narrow sc_rev sc_cost has_both_broad, ///
	ascategory nolabel yscale(range(2500)) yline(2304) ///
	title("broadening definitions doubles observations") ///
	ytitle("number of interviews")
graph export "$outfolder\plots_scorecard\sc_count_by_cost_rev.png", replace


*entry distribution of narrow vs broaden
use "$outfolder\data\sc_ready_for_summstats_withbroad.dta", clear
keep year doc_id_new doc_id_old sc_growth_revenue sc_growth_ebitda sc_revenue_broad sc_cost_broad ///
	en_growth_revenue en_growth_ebitda en_revenue_broad en_cost_broad
reshape long sc_ en_, i(doc_id_old doc_id_new) j(sc_topic) string
rename sc_ score
rename en_ entry
drop if entry==.
collapse (count) doc_id_old, by(sc_topic entry)
rename doc_id_old num_docs

egen num_entry = sum(num_docs), by(entry)

reshape wide num_docs, i(entry) j(sc_topic) string
rename num_docs* *_n

unab vars: *_n 
foreach var in `vars'  {
	label var `var' "`var'"
}

two line *_n entry if entry<=8, ///
	title("broad picks up entry num 3+") ///
	xtitle("entry number") ytitle("percent of interviews") ///
	legend(position(3) cols(1))
graph export "$outfolder\plots_scorecard\sc_counts_by_topicentry_broad.png", replace


*count of broad over time
use "$outfolder\data\sc_ready_for_summstats_withbroad.dta", clear
keep if year >= 2000 & year <= 2019
collapse (count) sc_growth_ebitda sc_cost_broad sc_growth_revenue sc_revenue_broad, by(year)
unab vars: sc*
foreach var in `vars'  {
	label var `var' "`var'"
}
twoway line sc_growth_ebitda sc_cost_broad sc_growth_revenue sc_revenue_broad year, ///
	title("broad cost fairly constant") ytitle("num. interviews") ///
	legend(position(3) cols(1))
graph export "$outfolder\plots_scorecard\sc_topiccounts_broad_by_year.png", replace

*min ranks of broad over time
use "$outfolder\data\sc_ready_for_summstats_withbroad.dta", clear
keep if year >= 2000 & year <= 2019
collapse (mean) en_growth_ebitda en_cost_broad en_growth_revenue en_revenue_broad, by(year)
unab vars: en*
foreach var in `vars'  {
	label var `var' "`var'"
}
twoway line en_growth_ebitda en_cost_broad en_growth_revenue en_revenue_broad year, ///
	title("broad vars change entry position") ytitle("average entry number") ///
	legend(position(3) cols(1))
graph export "$outfolder\plots_scorecard\sc_topicentry_broad_by_year.png", replace


*************************************
****    Compare CEOs and CFOs     ****
*************************************

use "$outfolder\data\sc_ready_for_summstats_withbroad.dta", clear
gen title_ceo = regexm(title_clean, "ceo")
gen title_cfo = regexm(title_clean, "cfo")
gen title_coo = regexm(title_clean, "coo")
gen num_titles = title_ceo + title_cfo + title_coo
keep if num_titles==1
drop num_titles
gen title = "ceo" if title_ceo==1
replace title = "cfo" if title_cfo==1
replace title = "coo" if title_coo==1
summarize title*
save "$outfolder\data\sc_ready_for_summstats_withbroad_ceocfo.dta", replace

*counts over time
use "$outfolder\data\sc_ready_for_summstats_withbroad_ceocfo.dta", clear
drop if year<2000 | year>2019 | year==.
collapse (count) doc_id_new, by(title year)
rename doc_id_new num_docs

reshape wide num_docs, i(year) j(title) string
rename num_docs* n_*
twoway line n_ceo n_cfo n_coo year, ///
	title("cfos become more common") ytitle("num. interviews") ///
	legend(position(3) cols(1))
graph export "$outfolder\plots_scorecard\sc_titlecounts_by_year.png", replace


*compare topic counts
use "$outfolder\data\sc_ready_for_summstats_withbroad_ceocfo.dta", clear
collapse (count) doc_id_new sc*, by(title)
rename doc_id_new num_docs
rename sc* num*

unab vars: num_*
foreach var in `vars'  {
	gen per_`var' = `var' / num_docs
}
rename per_num* per*
drop num_docs per_docs
reshape long per_ num_, i(title) j(topic) string
reshape wide per_ num_, i(topic) j(title) string
gen num_tot = num_ceo + num_cfo + num_coo
egen per_max = rowmax(per_ceo per_cfo per_coo)
drop if num_tot < 400

replace topic = "broad_cost" if topic=="cost_broad"
replace topic = "broad_revenue" if topic=="revenue_broad"
graph hbar (asis) per_ceo per_cfo per_coo, over(topic) nolabel ///
	title("title dictates if topics are included") ///
	ytitle("percent of interviews")
graph export "$outfolder\plots_scorecard\sc_topicper_by_title.png", replace


*compare topic entries
use "$outfolder\data\sc_ready_for_summstats_withbroad_ceocfo.dta", clear
collapse (mean) en*, by(title)
rename en* entry*

reshape long entry_, i(title) j(topic) string
reshape wide entry_, i(topic) j(title) string

drop if regexm(topic, "(analysis|branding|capital|compliance|expansion|innovate|manage|none)")

replace topic = "broad_cost" if topic=="cost_broad"
replace topic = "broad_revenue" if topic=="revenue_broad"
graph hbar (asis) entry_ceo entry_cfo entry_coo, over(topic) nolabel ///
	title("title does NOT dictate topic ordering") ///
	ytitle("percent of interviews")
graph export "$outfolder\plots_scorecard\sc_topicentry_by_title.png", replace












