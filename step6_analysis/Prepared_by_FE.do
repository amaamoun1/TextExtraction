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
**********    Grab relevant variables     ************
********************************************************************************

*grab relevant vars
import excel "$onedrive\extractions_merged_anonymized_deduplicated.xlsx", firstrow clear
keep doc_id_new doc_id_old prepared_by_clean date_clean title_clean
gen year = substr(date_clean, 1, 4)
destring year, replace
drop date_clean

*merge in factors
merge 1:1 doc_id_new doc_id_old using "$outfolder\data\competency_factors.dta", nogen
drop if factor_1==.
tabulate prepared_by_clean
replace prepared_by_clean = subinstr(prepared_by_clean, "-", "_",.)

*look only within c-suite
gen title_ceo = regexm(title_clean, "ceo")
gen title_cfo = regexm(title_clean, "cfo")
gen title_coo = regexm(title_clean, "coo")
gen num_titles = title_ceo + title_cfo + title_coo
drop if num_titles<1

********************************************************************************
**********    Create columns for each preparer     ************
********************************************************************************

*need to split apart the prepared by column
drop if prepared_by_clean==""
split prepared_by_clean, parse(" AND ") generate(prep)
replace prep1 = subinstr(prep1, " ", "_", .)
replace prep2 = subinstr(prep2, " ", "_", .)
replace prep3 = subinstr(prep3, " ", "_", .)
gen prep_pres1 = prep1!=""

*reshape so that each preparer gets their own column
reshape wide prep_pres1, i(doc_id_new doc_id_old title_clean prepared_by_clean) j(prep1) string
rename prep_pres1* prep_*

*add a "prep_" to the second and third preparer so that we can easily match them 
replace prep2 = "prep_" + prep2
replace prep3 = "prep_" + prep3
unab prep_vars: prep_*
foreach prep in `prep_vars'{
	replace `prep' = 0 if missing(`prep')
	replace `prep' = 1 if prep2 == "`prep'"
	replace `prep' = 1 if prep3 == "`prep'"
}
drop prep2 prep3

unab prep_vars: prep_*
tabstat `prep_vars', statistics(sum) columns(statistics) save
mat T = r(StatTotal)' //StatTotal still has variables as columns
putexcel set "$outfolder\output_raw\Prepared_by_counts.csv", replace
putexcel A1 = matrix(T), names 

*only keep preparers with more than 50 interviews
unab prep_vars: prep_*
foreach var of varlist `prep_vars' {
  summarize `var'
  if r(sum) < 50 drop `var' 
  }

unab prep_vars: prep_*
tabstat `prep_vars', statistics(sum) columns(statistics)


********************************************************************************
**********    Analysis     ************
********************************************************************************


eststo clear
eststo: reg factor_1 prep_*
eststo: reg factor_2 prep_*
eststo: reg factor_3 prep_*
eststo: reg factor_4 prep_*
esttab using "$outfolder\output_raw\Prepared_by_FE_50+.txt", replace label nogaps b(3) /*
*/ varwidth(30) r2 star(* 0.10 ** 0.05 *** 0.01) nonumbers mtitles("factor1" "factor2" "factor3" "factor4") 


*only keep preparers with more than 100 interviews
unab prep_vars: prep_*
foreach var of varlist `prep_vars' {
  summarize `var'
  if r(sum) < 100 drop `var' 
  }

unab prep_vars: prep_*
tabstat `prep_vars', statistics(sum) columns(statistics)


eststo clear
eststo: reg factor_1 prep_*
eststo: reg factor_2 prep_*
eststo: reg factor_3 prep_*
eststo: reg factor_4 prep_*
esttab using "$outfolder\output_raw\Prepared_by_FE_100+_nostd.txt", replace label nogaps b(3) /*
*/ varwidth(30) r2 star(* 0.10 ** 0.05 *** 0.01) nonumbers mtitles("factor1" "factor2" "factor3" "factor4") 


eststo clear
eststo: reg factor_1_st prep_*
eststo: reg factor_2_st prep_*
eststo: reg factor_3_st prep_*
eststo: reg factor_4_st prep_*
esttab using "$outfolder\output_raw\Prepared_by_FE_100+.txt", replace label nogaps b(3) /*
*/ varwidth(30) r2 star(* 0.10 ** 0.05 *** 0.01) nonumbers mtitles("factor1" "factor2" "factor3" "factor4") 


eststo clear
eststo: areg factor_1_st prep_*, abs(year)
eststo: areg factor_2_st prep_*, abs(year)
eststo: areg factor_3_st prep_*, abs(year)
eststo: areg factor_4_st prep_*, abs(year)
esttab using "$outfolder\output_raw\Prepared_by_FE_100+_yearFE.txt", replace label nogaps b(3) /*
*/ varwidth(30) r2 star(* 0.10 ** 0.05 *** 0.01) nonumbers mtitles("factor1" "factor2" "factor3" "factor4") 

