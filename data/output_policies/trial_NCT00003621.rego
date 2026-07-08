package clinical_trial_NCT00003621

default allow = false

# Eligibility Criteria:
# DISEASE CHARACTERISTICS: Histologically confirmed, newly diagnosed, anaplastic astrocytoma
#         No oligodendrogliomas or oligoastrocytomas
# 
#         PATIENT CHARACTERISTICS: Age: 18 and over Performance status: ECOG 0-2 Life expectancy: Not
#         specified Hematopoietic: WBC at least 3500/mm3 Platelet count at least 130,000/mm3 Hepatic:
#         Bilirubin no greater than 1.5 times upper limit of normal (ULN) SGOT no greater than 2
#         times ULN Renal: Creatinine no greater than 0.5 mg/dL Other: Not pregnant or nursing
#         Fertile patients must use effective contraception No uncontrolled infection No concurrent
#         malignant disease or major medical problem except superficial skin cancers
# 
#         PRIOR CONCURRENT THERAPY: Biologic therapy: Not specified Chemotherapy: At least 5 years
#         since prior chemotherapy Endocrine therapy: Concurrent corticosteroids allowed
#         Radiotherapy: At least 5 years since prior radiotherapy Surgery: Not specified

allow if {
    input_matches_gender
    input_matches_age
}

input_matches_gender if {
    "All" == "All"
}
input_matches_gender if {
    lower(input.gender) == lower("All")
}

input_matches_age if {
    age := input.age
    age_in_range(age)
}

age_in_range(age) if {
    min_val := parse_age("18 Years")
    max_val := parse_age("120 Years")
    age >= min_val
    age <= max_val
}

parse_age(s) = res if {
    s == "N/A"
    res := 0 # Or a very high number for max_age, but we'll handle it
}
parse_age(s) = res if {
    s != "N/A"
    parts := split(s, " ")
    res := to_number(parts[0])
}

# Overriding age_in_range for N/A cases
age_in_range(age) if {
    "18 Years" == "N/A"
    "120 Years" == "N/A"
}
age_in_range(age) if {
    "18 Years" != "N/A"
    "120 Years" == "N/A"
    parts := split("18 Years", " ")
    age >= to_number(parts[0])
}
age_in_range(age) if {
    "18 Years" == "N/A"
    "120 Years" != "N/A"
    parts := split("120 Years", " ")
    age <= to_number(parts[0])
}
