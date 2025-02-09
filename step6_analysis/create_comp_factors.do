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
**********    Prepare competency variables     ************
********************************************************************************


**** Grab the scorecard elements that were extracted using codes
import excel "$onedrive\extractions_merged_anonymized_deduplicated.xlsx", firstrow clear

keep doc_id_new doc_id_old title_clean comp_merged_*
reshape long comp_merged_, i(doc_id_new doc_id_old title_clean) j(competency) string
rename comp_merged_ rating
drop if rating==""

/* If we only wanted to keep c-suite candidates...
*keep ceos, coos, and cfos
tabulate title_clean
keep if regexm(title_clean, "(coo|ceo|cfo)")
drop if regexm(title_clean, "ceo succesion")
drop if regexm(title_clean, "^deputy")
drop if regexm(title_clean, "^division")
drop if regexm(title_clean, "^region")
drop if regexm(title_clean, "^assistant")
drop if regexm(title_clean, "office of ceo")
drop if regexm(title_clean, "region ceo")
tabulate title_clean
*/
//drop title_clean

*convert ratings to numbers
gen score = 4.3 if rating=="a+"
replace score = 4 if rating=="a"
replace score = 3.7 if rating=="a-"
replace score = 3.3 if rating=="b+"
replace score = 3 if rating=="b"
replace score = 2.7 if rating=="b-"
replace score = 2.3 if rating=="c+"
replace score = 2 if rating=="c"
replace score = 1.7 if rating=="c-"
drop rating

*drop competencies that are not common
egen competency_total = count(score), by(competency)
tabulate competency
drop if competency_total < 5000
drop competency_total

/* If we had wanted to drop documents without all common competencies
*drop documents without all common competencies
egen interview_total = count(score), by(doc_id_new doc_id_old)
tabulate interview_total
drop if interview_total < 28
drop interview_total
*/

reshape wide score, i(doc_id_new doc_id_old) j(competency) string
rename score* comp_*

summarize comp_*
save "$outfolder\data\competency_cleaned.dta", replace


/* Uses a PCA decomposition instead of factor analysis

*create factors
unab comps: comp_*
pca `comps', vce(normal)

*save information
esttab e(L) using "$outfolder\PCA_components.csv", replace plain
esttab e(Ev_stats) using "$outfolder\PCA_variance.csv", replace plain

*create variables for first 5 components
unab comps: comp_*
pca `comps', vce(normal) components(5)
predict factor_*

*/

use "$outfolder\data\competency_cleaned.dta", clear
unab varlist_chars: comp_*
factor `varlist_chars', factors(4) ml blank(0.15) altdivisor protect(50)

* save information
esttab e(L) using "$outfolder\output_raw\Factor_components.csv", replace plain
esttab e(Ev) using "$outfolder\output_raw\Factor_variance.csv", replace plain

* look at the model criteria
estat factors

* Rectrict sample to observations with non-missing characteristics, which are those used by factor analysis 
gen sample = e(sample)
drop if sample == 0 
drop sample

* Kaiser-Meyer-Olkin measure of sampling adequacy (overall) =  0.9325 
estat kmo, novar

* Generate four factor scores for each candidate 
predict factor_1 factor_2 factor_3 factor_4, notable

* standardize
foreach f in factor_1 factor_2 factor_3 factor_4 {
	egen `f'_st = std(`f')
}

summarize factor_*

keep doc_id_new doc_id_old factor*
save "$outfolder\data\competency_factors.dta", replace

* create plots for cluster
import excel "$onedrive\extractions_merged_anonymized_deduplicated.xlsx", firstrow clear
keep doc_id_new doc_id_old title_clean 

merge 1:1 doc_id_new doc_id_old using "$outfolder\data\competency_factors.dta", nogenerate

gen title_ceo = regexm(title_clean, "ceo")
gen title_cfo = regexm(title_clean, "cfo")
gen title_coo = regexm(title_clean, "coo")
gen num_titles = title_ceo + title_cfo + title_coo
gen title = "ceo" if title_ceo==1
replace title = "cfo" if title_cfo==1
replace title = "coo" if title_coo==1
replace title = "other" if title=="" | num_titles>1
tabulate title


twoway scatter factor_2_st factor_1_st, mcolor(%20) mlwidth(none)
graph export "$outfolder\plots_factors\x_factor1_y_factor2.png", replace

sepscatter factor_2_st factor_1_st, separate(title) mcolor(%20) mlwidth(none)



twoway scatter factor_3_st factor_1_st, mcolor(%20) mlwidth(none)
graph export "$outfolder\plots_factors\x_factor1_y_factor3.png", replace

twoway scatter factor_4_st factor_1_st, mcolor(%20) mlwidth(none)
graph export "$outfolder\plots_factors\x_factor1_y_factor4.png", replace

twoway scatter factor_2_st factor_3_st, mcolor(%20) mlwidth(none)
graph export "$outfolder\plots_factors\x_factor2_y_factor3.png", replace

twoway scatter factor_2_st factor_4_st, mcolor(%20) mlwidth(none)
graph export "$outfolder\plots_factors\x_factor2_y_factor4.png", replace

twoway scatter factor_3_st factor_4_st, mcolor(%20) mlwidth(none)
graph export "$outfolder\plots_factors\x_factor3_y_factor4.png", replace














