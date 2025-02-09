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
keep doc_id_new doc_id_old date_clean title_clean undergrad_clean undergrad_ivy mba_clean mba_top14

gen year = substr(date_clean, 1, 4)
destring year, replace
drop date_clean

gen undergrad_attend = !missing(undergrad_clean)
gen mba_attend = !missing(mba_clean)

*merge in factors
merge 1:1 doc_id_new doc_id_old using "$outfolder\data\competency_factors.dta", nogen
drop if factor_1==.

*merge in scorecard
merge 1:1 doc_id_new doc_id_old using "$outfolder\data\scorecard.dta", nogen


*regress with factors
eststo clear
eststo: reg factor_1 undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg factor_2 undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg factor_3 undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg factor_4 undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_broad_revenue undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_broad_cost undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_growth_both undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_growth_ebitda undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_growth_revenue undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_culture undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_deals undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_exit undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_finance undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_leader undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_operations undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_relations undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_staffing undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_strategy undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_broad_revenue factor_1_st factor_2_st factor_3_st factor_4_st undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_broad_cost factor_1_st factor_2_st factor_3_st factor_4_st undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_growth_both factor_1_st factor_2_st factor_3_st factor_4_st undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_growth_ebitda factor_1_st factor_2_st factor_3_st factor_4_st undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_growth_revenue factor_1_st factor_2_st factor_3_st factor_4_st undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_culture factor_1_st factor_2_st factor_3_st factor_4_st undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_deals factor_1_st factor_2_st factor_3_st factor_4_st undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_exit factor_1_st factor_2_st factor_3_st factor_4_st undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_finance factor_1_st factor_2_st factor_3_st factor_4_st undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_leader factor_1_st factor_2_st factor_3_st factor_4_st undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_operations factor_1_st factor_2_st factor_3_st factor_4_st undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_relations factor_1_st factor_2_st factor_3_st factor_4_st undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_staffing factor_1_st factor_2_st factor_3_st factor_4_st undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
eststo: reg sc_strategy factor_1_st factor_2_st factor_3_st factor_4_st undergrad_attend undergrad_ivy mba_attend mba_top14 if regexm(title_clean, "ceo")
esttab using "$outfolder\output_raw\schooling_sc_factors_ceo.csv", replace label nogaps b(3) /*
*/ varwidth(30) r2 star(* 0.10 ** 0.05 *** 0.01) nonumbers mtitles("factor1" "factor2" "factor3" "factor4" "broad_rev" "broad_cost" "growth_both" "growth_ebitda" "growth_revenue" "culture" "deals" "exit" "finance" "leader" "operations" "relations" "staffing" "strategy" "broad_rev" "broad_cost" "growth_both" "growth_ebitda" "growth_revenue" "culture" "deals" "exit" "finance" "leader" "operations" "relations" "staffing" "strategy") 

