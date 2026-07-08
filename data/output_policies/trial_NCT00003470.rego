package clinical_trial_NCT00003470

default allow = false

# Eligibility Criteria:
# DISEASE CHARACTERISTICS:
# 
#           -  Histologically or cytologically confirmed incurable adult anaplastic astrocytoma
# 
#           -  Evidence of progressive or recurrent tumor by MRI scan performed within 2 weeks prior
#              to study entry
# 
#           -  Must have received and failed standard therapy
# 
#           -  Tumor must be at least 5 mm
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
#           -  At least 2 months
# 
#         Hematopoietic:
# 
#           -  WBC at least 2000/mm^3
# 
#           -  Platelet count at least 50,000/mm^3
# 
#         Hepatic:
# 
#           -  Bilirubin no greater than 2.5 mg/dL
# 
#           -  SGOT and SGPT no greater than 5 times upper limit of normal
# 
#           -  No hepatic failure
# 
#         Renal:
# 
#           -  Creatinine no greater than 2.5 mg/dL
# 
#           -  No history of renal conditions that contraindicate high dosages of sodium
# 
#         Cardiovascular:
# 
#           -  No uncontrolled hypertension
# 
#           -  No history of congestive heart failure
# 
#           -  No history of other cardiovascular conditions that contraindicate high dosages of
#              sodium
# 
#         Pulmonary:
# 
#           -  No serious lung disease such as severe chronic obstructive pulmonary disease
# 
#         Other:
# 
#           -  Not pregnant or nursing
# 
#           -  Fertile patients must use effective contraception during and for 4 weeks after study
# 
#           -  No active infection
# 
#           -  No other serious concurrent disease
# 
#         PRIOR CONCURRENT THERAPY:
# 
#         Biologic therapy:
# 
#           -  At least 4 weeks since prior immunotherapy and recovered
# 
#           -  No concurrent immunomodulating agents
# 
#         Chemotherapy:
# 
#           -  At least 4 weeks since prior chemotherapy (6 weeks for nitrosoureas) and recovered
# 
#           -  No concurrent antineoplastic agents
# 
#         Endocrine therapy:
# 
#           -  Concurrent corticosteroids allowed
# 
#         Radiotherapy:
# 
#           -  At least 8 weeks since prior radiotherapy and recovered
# 
#         Surgery:
# 
#           -  Fully recovered from any prior surgery
# 
#         Other:
# 
#           -  Prior cytodifferentiating agent allowed
# 
#           -  No prior antineoplaston therapy

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
    max_val := parse_age("99 Years")
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
    "99 Years" == "N/A"
}
age_in_range(age) if {
    "18 Years" != "N/A"
    "99 Years" == "N/A"
    parts := split("18 Years", " ")
    age >= to_number(parts[0])
}
age_in_range(age) if {
    "18 Years" == "N/A"
    "99 Years" != "N/A"
    parts := split("99 Years", " ")
    age <= to_number(parts[0])
}
