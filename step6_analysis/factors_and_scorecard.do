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
**********    Regress factors on scorecard     ************
********************************************************************************

*grab competency factors and competencies
use "$outfolder\data\competency_factors.dta", clear
merge 1:1 doc_id_new doc_id_old using "$outfolder\data\competency_cleaned.dta", nogen

*merge in scorecard
merge 1:1 doc_id_new doc_id_old using "$outfolder\data\scorecard.dta", nogen

*create a correlation table of competencies on scorecard
estpost corr comp_* sc_broad_revenue sc_broad_cost ///
	sc_growth_both sc_growth_revenue sc_growth_ebitda sc_culture sc_deals sc_exit ///
	sc_finance sc_leader sc_operations sc_relations sc_staffing sc_strategy, matrix
eststo correlation
esttab correlation using "$outfolder\output_raw\sc_comp_corr.csv", not unstack compress noobs replace

*create a correlation table of factors on scorecard
estpost corr factor_1 factor_2 factor_3 factor_4 sc_broad_revenue sc_broad_cost ///
	sc_growth_both sc_growth_revenue sc_growth_ebitda sc_culture sc_deals sc_exit ///
	sc_finance sc_leader sc_operations sc_relations sc_staffing sc_strategy, matrix
eststo correlation
esttab correlation using "$outfolder\output_raw\sc_factors_corr.csv", not unstack compress noobs replace

*regress with everyone
eststo clear
eststo: reg sc_growth_both factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_growth_revenue factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_growth_ebitda factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_broad_revenue factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_broad_cost factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_culture factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_deals factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_exit factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_finance factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_leader factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_operations factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_relations factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_staffing factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_strategy factor_1_st factor_2_st factor_3_st factor_4_st
esttab using "$outfolder\output_raw\screg_on_factors_all.csv", replace label nogaps b(3) /*
*/ varwidth(30) r2 star(* 0.10 ** 0.05 *** 0.01) nonumbers mtitles("narrow_both" "narrow_revenue" "narrow_cost" "broad_revenue" "broad_cost" "culture" "deals" "exit" "finance" "leader" "operations" "relations" "staffing" "strategy") 


*repeat regression but only within c-suite
gen title_ceo = regexm(title_clean, "ceo")
gen title_cfo = regexm(title_clean, "cfo")
gen title_coo = regexm(title_clean, "coo")
gen num_titles = title_ceo + title_cfo + title_coo
drop if num_titles<1

*regress with growth/revenue people...csuite
eststo clear
eststo: reg sc_growth_both factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_growth_revenue factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_growth_ebitda factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_broad_revenue factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_broad_cost factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_culture factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_deals factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_exit factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_finance factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_leader factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_operations factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_relations factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_staffing factor_1_st factor_2_st factor_3_st factor_4_st
eststo: reg sc_strategy factor_1_st factor_2_st factor_3_st factor_4_st
esttab using "$outfolder\output_raw\screg_on_factors_csuite.csv", replace label nogaps b(3) /*
*/ varwidth(30) r2 star(* 0.10 ** 0.05 *** 0.01) nonumbers mtitles("narrow_both" "narrow_revenue" "narrow_cost" "broad_revenue" "broad_cost" "culture" "deals" "exit" "finance" "leader" "operations" "relations" "staffing" "strategy") 





*regress with growth/revenue people...ceo
eststo clear
eststo: reg sc_growth_both factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: reg sc_growth_revenue factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: reg sc_growth_ebitda factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: reg sc_broad_revenue factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: reg sc_broad_cost factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: reg sc_culture factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: reg sc_deals factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: reg sc_exit factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: reg sc_finance factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: reg sc_leader factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: reg sc_operations factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: reg sc_relations factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: reg sc_staffing factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: reg sc_strategy factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
esttab using "$outfolder\output_raw\screg_on_factors_ceo.csv", replace label nogaps b(3) /*
*/ varwidth(30) r2 star(* 0.10 ** 0.05 *** 0.01) nonumbers mtitles("narrow_both" "narrow_revenue" "narrow_cost" "broad_revenue" "broad_cost" "culture" "deals" "exit" "finance" "leader" "operations" "relations" "staffing" "strategy") 


*regress with growth/revenue people...cfo
eststo clear
eststo: reg sc_growth_both factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: reg sc_growth_revenue factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: reg sc_growth_ebitda factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: reg sc_broad_revenue factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: reg sc_broad_cost factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: reg sc_culture factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: reg sc_deals factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: reg sc_exit factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: reg sc_finance factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: reg sc_leader factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: reg sc_operations factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: reg sc_relations factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: reg sc_staffing factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: reg sc_strategy factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
esttab using "$outfolder\output_raw\screg_on_factors_cfo.csv", replace label nogaps b(3) /*
*/ varwidth(30) r2 star(* 0.10 ** 0.05 *** 0.01) nonumbers mtitles("narrow_both" "narrow_revenue" "narrow_cost" "broad_revenue" "broad_cost" "culture" "deals" "exit" "finance" "leader" "operations" "relations" "staffing" "strategy") 


*regress with growth/revenue people...ceo
eststo clear
eststo: reg sc_growth_both comp_* if regexm(title_clean, "ceo")
eststo: reg sc_growth_revenue comp_* if regexm(title_clean, "ceo")
eststo: reg sc_growth_ebitda comp_* if regexm(title_clean, "ceo")
eststo: reg sc_broad_revenue comp_* if regexm(title_clean, "ceo")
eststo: reg sc_broad_cost comp_* if regexm(title_clean, "ceo")
eststo: reg sc_culture comp_* if regexm(title_clean, "ceo")
eststo: reg sc_deals comp_* if regexm(title_clean, "ceo")
eststo: reg sc_exit comp_* if regexm(title_clean, "ceo")
eststo: reg sc_finance comp_* if regexm(title_clean, "ceo")
eststo: reg sc_leader comp_* if regexm(title_clean, "ceo")
eststo: reg sc_operations comp_* if regexm(title_clean, "ceo")
eststo: reg sc_relations comp_* if regexm(title_clean, "ceo")
eststo: reg sc_staffing comp_* if regexm(title_clean, "ceo")
eststo: reg sc_strategy comp_* if regexm(title_clean, "ceo")
esttab using "$outfolder\output_raw\screg_on_comp_ceo.csv", replace label nogaps b(3) /*
*/ varwidth(30) r2 star(* 0.10 ** 0.05 *** 0.01) nonumbers mtitles("narrow_both" "narrow_revenue" "narrow_cost" "broad_revenue" "broad_cost" "culture" "deals" "exit" "finance" "leader" "operations" "relations" "staffing" "strategy") 


*regress with growth/revenue people...cfo
eststo clear
eststo: reg sc_growth_both comp_* if regexm(title_clean, "cfo")
eststo: reg sc_growth_revenue comp_* if regexm(title_clean, "cfo")
eststo: reg sc_growth_ebitda comp_* if regexm(title_clean, "cfo")
eststo: reg sc_broad_revenue comp_* if regexm(title_clean, "cfo")
eststo: reg sc_broad_cost comp_* if regexm(title_clean, "cfo")
eststo: reg sc_culture comp_* if regexm(title_clean, "cfo")
eststo: reg sc_deals comp_* if regexm(title_clean, "cfo")
eststo: reg sc_exit comp_* if regexm(title_clean, "cfo")
eststo: reg sc_finance comp_* if regexm(title_clean, "cfo")
eststo: reg sc_leader comp_* if regexm(title_clean, "cfo")
eststo: reg sc_operations comp_* if regexm(title_clean, "cfo")
eststo: reg sc_relations comp_* if regexm(title_clean, "cfo")
eststo: reg sc_staffing comp_* if regexm(title_clean, "cfo")
eststo: reg sc_strategy comp_* if regexm(title_clean, "cfo")
esttab using "$outfolder\output_raw\screg_on_comp_cfo.csv", replace label nogaps b(3) /*
*/ varwidth(30) r2 star(* 0.10 ** 0.05 *** 0.01) nonumbers mtitles("narrow_both" "narrow_revenue" "narrow_cost" "broad_revenue" "broad_cost" "culture" "deals" "exit" "finance" "leader" "operations" "relations" "staffing" "strategy") 



*regress mean onto factors by sc type and position
eststo clear
eststo: reg sc_mean factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo") & sc_type=="revenue"
eststo: reg sc_mean factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo") & sc_type=="cost"
eststo: reg sc_mean factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo") & sc_type=="revenue"
eststo: reg sc_mean factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo") & sc_type=="cost"
esttab using "$outfolder\output_raw\scmean_on_factors_by_sctype.csv", replace label nogaps b(3) /*
*/ varwidth(30) r2 star(* 0.10 ** 0.05 *** 0.01) nonumbers mtitles("ceo_revenue" "ceo_cost" "cfo_revenue" "cfo_cost") 






*logit regression on if scorecard includes a given topic...ceo
eststo clear
eststo: logit has_sc_growth_both factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: logit has_sc_growth_revenue factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: logit has_sc_growth_ebitda factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: logit has_sc_broad_revenue factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: logit has_sc_broad_cost factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: logit has_sc_culture factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: logit has_sc_deals factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: logit has_sc_exit factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: logit has_sc_finance factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: logit has_sc_leader factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: logit has_sc_operations factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: logit has_sc_relations factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: logit has_sc_staffing factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
eststo: logit has_sc_strategy factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "ceo")
esttab using "$outfolder\output_raw\sclogit_on_factors_ceo.csv", replace label nogaps b(3) /*
*/ varwidth(30) r2 star(* 0.10 ** 0.05 *** 0.01) nonumbers mtitles("narrow_both" "narrow_revenue" "narrow_cost" "broad_revenue" "broad_cost" "culture" "deals" "exit" "finance" "leader" "operations" "relations" "staffing" "strategy") 

*logit regression on if scorecard includes a given topic...cfo
eststo clear
eststo: logit has_sc_growth_both factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: logit has_sc_growth_revenue factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: logit has_sc_growth_ebitda factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: logit has_sc_broad_revenue factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: logit has_sc_broad_cost factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: logit has_sc_culture factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: logit has_sc_deals factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: logit has_sc_exit factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: logit has_sc_finance factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: logit has_sc_leader factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: logit has_sc_operations factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: logit has_sc_relations factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: logit has_sc_staffing factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
eststo: logit has_sc_strategy factor_1_st factor_2_st factor_3_st factor_4_st if regexm(title_clean, "cfo")
esttab using "$outfolder\output_raw\sclogit_on_factors_cfo.csv", replace label nogaps b(3) /*
*/ varwidth(30) r2 star(* 0.10 ** 0.05 *** 0.01) nonumbers mtitles("narrow_both" "narrow_revenue" "narrow_cost" "broad_revenue" "broad_cost" "culture" "deals" "exit" "finance" "leader" "operations" "relations" "staffing" "strategy") 





