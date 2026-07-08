package clinical_trial_NCT00002814

default allow = false

# Eligibility Criteria:
# DISEASE CHARACTERISTICS: Biopsy proven glioblastoma multiforme or anaplastic astrocytoma
#         Central pathologic review at Dartmouth-Hitchcock Medical Center, including assay for tumor
#         p53 expression No anaplastic oligodendroglioma No mixed oligodendroastrocytoma Recurrent or
#         progressive disease following radiotherapy documented by CT or MRI within 2 weeks of entry
# 
#         PATIENT CHARACTERISTICS: Age: 18 and over Performance status: Karnofsky 60%-100%
#         Hematopoietic: WBC at least 3,000 ANC at least 1,500 Platelets at least 100,000 Hepatic:
#         Bilirubin no greater than 1.0 mg/dL AST/ALT no greater than 2.5 times normal Renal:
#         Creatinine no greater than 1.5 mg/dL Other: No documented sensitivity to E. coli-derived
#         products No major medical or psychiatric illness that would interfere with therapy or
#         compliance with scheduled follow-up No pregnant or nursing women Adequate contraception
#         required of fertile patients
# 
#         PRIOR CONCURRENT THERAPY: No prior taxanes or topoisomerase I inhibitors At least 4 weeks
#         since chemotherapy (6 weeks since nitrosoureas) At least 4 weeks since radiotherapy

allow {
    input_matches_gender
    input_matches_age
}

input_matches_gender {
    "All" == "All"
}
input_matches_gender {
    lower(input.gender) == lower("All")
}

input_matches_age {
    age := input.age
    age_in_range(age)
}

age_in_range(age) {
    min_val := parse_age("18 Years")
    max_val := parse_age("N/A")
    age >= min_val
    age <= max_val
}

parse_age(s) = res {
    s == "N/A"
    res := 0 # Or a very high number for max_age, but we'll handle it
}
parse_age(s) = res {
    s != "N/A"
    parts := split(s, " ")
    res := to_number(parts[0])
}

# Overriding age_in_range for N/A cases
age_in_range(age) {
    "18 Years" == "N/A"
    "N/A" == "N/A"
}
age_in_range(age) {
    "18 Years" != "N/A"
    "N/A" == "N/A"
    parts := split("18 Years", " ")
    age >= to_number(parts[0])
}
age_in_range(age) {
    "18 Years" == "N/A"
    "N/A" != "N/A"
    parts := split("N/A", " ")
    age <= to_number(parts[0])
}
