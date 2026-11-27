# Step 1 - collect district-level weekly dengue cases (Epidemiology Unit, MoH Sri Lanka)
# from the open-source `denguedatahub` R package, which compiles the Weekly Epidemiological Reports (WER).
# Run once from the project folder:   install.packages("denguedatahub")   then   source("scripts/01_export_dengue_csv.R")
# The data is read straight from the package's data file, so Java/rJava is NOT needed
# (library(denguedatahub) fails on Windows without Java because of its PDF-parsing dependencies).
e <- new.env()
lazyLoad(file.path(find.package("denguedatahub"), "data", "Rdata"), envir = e)
dir.create("data/raw", recursive = TRUE, showWarnings = FALSE)
write.csv(e$srilanka_weekly_data, "data/raw/srilanka_weekly_dengue.csv", row.names = FALSE)
if (!is.null(e$sl_province_districts))
  write.csv(e$sl_province_districts, "data/raw/sl_province_districts.csv", row.names = FALSE)
cat("Rows:", nrow(e$srilanka_weekly_data), " Years:",
    paste(range(e$srilanka_weekly_data$year), collapse = "-"), "\n")
