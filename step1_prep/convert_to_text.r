rm(list=ls())
library(pdftools)

#collect the pdf filepaths
pdf_folder <- "C:/Users/Yann.Decressin/Documents/Pre2012PDFs/"
pdf_files <- list.files(path=pdf_folder, pattern="pdf$", full.names = T)

#loop over and create a .txt file for each file
total <- 0
for (file in pdf_files){
  if (total %% 500 == 0){
    print(total)
    print(Sys.time())
  }
  text_pages <- pdf_text(file)
  text_combined <- paste0(text_pages, sep="\n THIS IS A NEW PAGE \n", collapse = '')
  txt_file <- gsub("PDFs", "TXTs", file)
  txt_file <- gsub("\\.pdf$", ".txt", txt_file)
  writeLines(text_combined, con=txt_file)
  total <- total + 1
}

