addendum = "market conditions addendum to the appraisal report"
description = "general description"
income = "Income Approach to value"
grossIncome = "Toral gross montly rent"
comparable = "Sales comparison analysis"
comparableNumber = "COMPARABLE NO."
comparableSales = "COMPARABLE SALE #"
comparableSalesNumber = "COMPARABLE SALE NO."
comparableRental = "COMPARABLE RENTAL #"
comparableRentalsNumber = "COMPARABLE RENTAL NO."
location = "LOCATED AT"
appraisalValue = "APPRAISED VALUE OF SUBJECT PROPERTY"

COMPARABLE_SALES_PATTERN_KEYS = (
    "Comparable",
    "Comparable Numbers",
    "Comparable Sales",
    "Comparable Sales Number",
)
COMPARABLE_RENTAL_PATTERN_KEYS = (
    "Comparable Rental",
    "Comparable Rentals Number",
)

PATTERN_DEFINITIONS: dict[str, str] = {
    "Addendum": addendum,
    "Description": description,
    "Income": income,
    "Gross Income": grossIncome,
    "Comparable": comparable,
    "Comparable Numbers": comparableNumber,
    "Comparable Sales": comparableSales,
    "Comparable Rental": comparableRental,
    "Comparable Rentals Number": comparableRentalsNumber,
    "Comparable Sales Number": comparableSalesNumber,
    "Location": location,
    "Appraisal Value": appraisalValue,
}