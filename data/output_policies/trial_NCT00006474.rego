package clinical_trial_NCT00006474

default allow = false

# Eligibility Criteria:
# DISEASE CHARACTERISTICS:
# 
#           -  Part I:
# 
#                -  Histologically confirmed, newly diagnosed glioblastoma multiforme or anaplastic
#                   astrocytoma (closed to accrual 12/19/2000)
# 
#           -  Parts I and II:
# 
#                -  Histologically confirmed astrocytic, oligodendroglial, or mixed glial tumor
# 
#                     -  Grade III or higher
# 
#                     -  Recurrent or progressive after radiotherapy
# 
#           -  Evaluable residual disease by contrast-enhanced MRI or CT scan
# 
#         PATIENT CHARACTERISTICS:
# 
#         Age:
# 
#           -  18 and over
# 
#         Performance status:
# 
#           -  Karnofsky 60-100%
# 
#         Life expectancy:
# 
#           -  Not specified
# 
#         Hematopoietic:
# 
#           -  Granulocyte count at least 1,500/mm3
# 
#           -  Platelet count at least 100,000/mm3
# 
#         Hepatic:
# 
#           -  SGOT no greater than 2.5 times upper limit of normal
# 
#           -  Bilirubin normal
# 
#         Renal:
# 
#           -  Creatinine no greater than 1.5 mg/dL OR
# 
#           -  Creatinine clearance greater than 60 mL/min
# 
#           -  BUN no greater than 25 mg/dL
# 
#         Other:
# 
#           -  Not pregnant or nursing
# 
#           -  Negative pregnancy test
# 
#           -  Fertile patients must use effective contraception during and for 2 months after study
# 
#         PRIOR CONCURRENT THERAPY:
# 
#         Biologic therapy:
# 
#           -  At least 6 weeks since prior biologic therapy and recovered
# 
#         Chemotherapy:
# 
#           -  At least 2 weeks since prior chemotherapy (including but not limited to topotecan) and
#              recovered
# 
#                -  Patients in trials with one of the following treatment combinations are allowed
#                   to enroll 6 weeks after receiving carmustine (BCNU):
# 
#                     -  BCNU on day 1
# 
#                     -  BCNU on day 1 and topotecan on days 1, 8, 15, 22, 29, and 36
# 
#                     -  BCNU on day 1 and irinotecan on days 1, 8, 15, and 22
# 
#         Endocrine therapy:
# 
#           -  Patients on corticosteroids must be on a stable dose for at least 2 weeks before study
# 
#           -  At least 6 weeks since other prior endocrine therapy and recovered
# 
#         Radiotherapy:
# 
#           -  See Disease Characteristics
# 
#           -  At least 6 weeks since prior radiotherapy and recovered
# 
#         Surgery:
# 
#           -  Not specified

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
    max_val := parse_age("N/A")
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
    "N/A" == "N/A"
}
age_in_range(age) if {
    "18 Years" != "N/A"
    "N/A" == "N/A"
    parts := split("18 Years", " ")
    age >= to_number(parts[0])
}
age_in_range(age) if {
    "18 Years" == "N/A"
    "N/A" != "N/A"
    parts := split("N/A", " ")
    age <= to_number(parts[0])
}
