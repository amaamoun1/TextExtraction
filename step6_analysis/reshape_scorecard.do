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
capture log using "$codefolder\reshape_scorecard.log", replace



********************************************************************************
**********    keep scorecard variables     ************
********************************************************************************



**** Grab the scorecard elements that were extracted using codes
import excel "$onedrive\extractions_merged_anonymized_deduplicated.xlsx", firstrow clear

*keep and rename important vars
keep doc_id* title_clean sc*
drop sc*desc sc_present sc_outcomes_amount sc_total_words
rename sc_*_rating sc_rating*
rename sc_*_topic sc_topic*

*reshape long and keep scorecard elements with topics
reshape long sc_topic sc_rating, i(doc_id_old doc_id_new title_clean) j(entry)
drop if sc_topic==""

*combine all of the relations elements...we can do a more detailed analysis later
replace sc_topic="relations" if regexm(sc_topic, "^relations")

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

*some documents have the same topic multiple times
*when collapsing, we average all the topic's ratings
duplicates report doc_id_old doc_id_new sc_topic
collapse (mean) sc_score, by(doc_id_old doc_id_new title_clean sc_topic sc_type)

*reshape back to wide format
reshape wide sc_score, i(doc_id_old doc_id_new title_clean sc_type) j(sc_topic) string
rename sc_score* sc_*
tempfile reshaped
save `reshaped'

**** Create an average score
import excel "$onedrive\extractions_merged_anonymized_deduplicated.xlsx", firstrow clear

*keep and rename important vars
keep doc_id* sc*
drop sc*desc sc_*_topic sc_present sc_outcomes_amount sc_total_words sc_score* sc_type
rename sc_*_rating sc_rating*

*reshape long and keep scorecard elements with topics
reshape long sc_rating, i(doc_id_old doc_id_new) j(entry)

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

*get mean
collapse (mean) sc_score, by(doc_id_old doc_id_new)
drop if sc_score==.
rename sc_score sc_mean

tempfile sc_mean
save `sc_mean'


**** Scorecard elements extracted by RAs from past data
import excel "$onedrive\extractions_merged_anonymized_deduplicated.xlsx", firstrow clear

*keep and rename important vars
keep doc_id* title_clean sc*
drop sc*desc sc*topic sc*rating sc_present sc_outcomes_amount sc_total_words sc_score* sc_type

*reshape long
reshape long sc_, i(doc_id_old doc_id_new title_clean) j(topic) string

*only keep those with ratings from the past data
rename sc_ sc_rating
drop if sc_rating==""

*convert grades to scores
gen sc_score = 4.3 if sc_rating=="a+"
replace sc_score = 4 if sc_rating=="a"
replace sc_score = 3.7 if sc_rating=="a-"
replace sc_score = 3.3 if sc_rating=="b+"
replace sc_score = 3 if sc_rating=="b"
replace sc_score = 2.7 if sc_rating=="b-"
replace sc_score = 2.3 if sc_rating=="c+"
replace sc_score = 2 if sc_rating=="c"
replace sc_score = 1.7 if sc_rating=="c-"
drop sc_rating

*reshape wide
reshape wide sc_score, i(doc_id_old doc_id_new title_clean) j(topic) string
rename sc_score* old_sc_*
tempfile reshaped_old
save `reshaped_old'


**** Calcualte mean from Scorecard elements extracted by RAs from past data
import excel "$onedrive\extractions_merged_anonymized_deduplicated.xlsx", firstrow clear

*keep and rename important vars
keep doc_id* sc*
drop sc*desc sc*topic sc*rating sc_present sc_outcomes_amount sc_total_words sc_score* sc_type

*reshape long
reshape long sc_, i(doc_id_old doc_id_new) j(topic) string

*only keep those with ratings from the past data
rename sc_ sc_rating
drop if sc_rating==""

*convert grades to scores
gen sc_score = 4.3 if sc_rating=="a+"
replace sc_score = 4 if sc_rating=="a"
replace sc_score = 3.7 if sc_rating=="a-"
replace sc_score = 3.3 if sc_rating=="b+"
replace sc_score = 3 if sc_rating=="b"
replace sc_score = 2.7 if sc_rating=="b-"
replace sc_score = 2.3 if sc_rating=="c+"
replace sc_score = 2 if sc_rating=="c"
replace sc_score = 1.7 if sc_rating=="c-"
drop sc_rating

*get mean
collapse (mean) sc_score, by(doc_id_old doc_id_new)
rename sc_score old_sc_mean

tempfile sc_mean_old
save `sc_mean_old'




**** Merge the two datasets

use `reshaped_old', clear
merge 1:1 doc_id_old doc_id_new title_clean using `reshaped', nogen
merge 1:1 doc_id_old doc_id_new using `sc_mean', nogen
rename sc_* new_sc_*
merge 1:1 doc_id_old doc_id_new using `sc_mean_old', nogen
summarize

*merge in the old extraction when the new extraction not available
rename old_sc_* sc_*
drop sc_other new_sc_none

unab sc_vars: sc_*
foreach var in `sc_vars'  {
	replace new_`var' = `var' if missing(new_`var')
}
drop sc_*
rename new_* *

*create the broad revenue and cost measures
egen sc_broad_revenue = rowmean(sc_branding sc_expansion sc_growth_revenue sc_innovate)
egen sc_broad_cost = rowmean(sc_growth_ebitda sc_operations)

*create dummy variables for if the sc element type was included or not
unab sc_vars: sc_*
foreach var in sc_analysis sc_branding sc_broad_cost sc_broad_revenue sc_capital sc_compliance sc_culture sc_deals sc_exit sc_expansion sc_finance sc_growth_both sc_growth_ebitda sc_growth_revenue sc_innovate sc_leader sc_manage sc_operations sc_relations sc_staffing sc_strategy  {
	generate has_`var' = `var'!=.
}

summarize

*check counts
count if !missing(sc_growth_ebitda) & !missing(sc_growth_revenue)


**** save
save "$outfolder\data\scorecard.dta", replace






**** check counts among ceo/cfo/coo
use "$outfolder\data\scorecard.dta", replace
//keep if title_clean=="ceo" | title_clean=="cfo" | title_clean=="coo"
keep if title_clean=="ceo"

summarize

count if !missing(sc_growth_ebitda) & !missing(sc_growth_revenue)
count if !missing(sc_growth_ebitda) & !missing(sc_growth_revenue) & !missing(sc_staffing)
count if !missing(sc_growth_ebitda) & !missing(sc_growth_revenue) & !missing(sc_strategy)
count if !missing(sc_growth_ebitda) & !missing(sc_growth_revenue) & !missing(sc_staffing)  & !missing(sc_strategy)
count if !missing(sc_growth_ebitda) & !missing(sc_growth_revenue) & !missing(sc_staffing)  & !missing(sc_strategy) & !missing(sc_relations)

count if (!missing(sc_growth_both) | (!missing(sc_growth_ebitda) & !missing(sc_growth_revenue)))
count if (!missing(sc_growth_both) | (!missing(sc_growth_ebitda) & !missing(sc_growth_revenue))) & !missing(sc_staffing)
count if (!missing(sc_growth_both) | (!missing(sc_growth_ebitda) & !missing(sc_growth_revenue))) & !missing(sc_strategy)
count if (!missing(sc_growth_both) | (!missing(sc_growth_ebitda) & !missing(sc_growth_revenue))) & !missing(sc_staffing)  & !missing(sc_strategy)
count if (!missing(sc_growth_both) | (!missing(sc_growth_ebitda) & !missing(sc_growth_revenue))) & !missing(sc_staffing)  & !missing(sc_strategy) & !missing(sc_relations)
count if (!missing(sc_growth_both) | (!missing(sc_growth_ebitda) & !missing(sc_growth_revenue))) & !missing(sc_staffing)  & !missing(sc_strategy) & !missing(sc_operations)
count if (!missing(sc_growth_both) | (!missing(sc_growth_ebitda) & !missing(sc_growth_revenue))) & !missing(sc_staffing)  & !missing(sc_strategy) & !missing(sc_relations) & !missing(sc_deals)


log close



