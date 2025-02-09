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

*keep only those considered for one of ceo/cfo/coo
gen title_ceo = regexm(title_clean, "ceo")
gen title_cfo = regexm(title_clean, "cfo")
gen title_coo = regexm(title_clean, "coo")
gen num_titles = title_ceo + title_cfo + title_coo
drop if num_titles>1
drop num_titles
gen title = "ceo" if title_ceo==1
replace title = "cfo" if title_cfo==1
replace title = "coo" if title_coo==1
replace title = "other" if title==""
tabulate title

eststo clear
bys title: eststo: quietly estpost summarize factor_1_st-factor_4_st, listwise
esttab using "$outfolder\output_raw\ceo_vs_cfo_vs_coo_factors.csv", cells("mean") label plain nodepvar replace