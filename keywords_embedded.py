COMPARABLE_SALES_PATTERN_KEYS = (
    "Comparable",
    "Comparable Numbers",
    "Comparable Sales",
    "Comparable Sales Number",
)
COMPARABLE_RENTAL_PATTERN_KEYS = (
    "Comparable Rental",
    "Comparable Rentals Number",
    "Rent Schedule",
)

EXCLUDED_PAGE_PHRASES = (
    "Table of Contents",
    "The Appraiser certifies and agrees that",
    "Photos",
    "Photo"
)

PATTERN_DEFINITIONS: dict[str, str] = {
    "Addendum": "market conditions addendum to the appraisal report",
    "Description": "general description",
    "Income": "Income Approach to value",
    "Gross Income": "Toral gross montly rent",
    "Comparable": "Sales comparison analysis",
    "Comparable Numbers": "COMPARABLE NO.",
    "Comparable Sales": "COMPARABLE SALE #",
    "Comparable Rental": "COMPARABLE RENTAL #",
    "Comparable Rentals Number": "COMPARABLE RENTAL NO.",
    "Rent Schedule": "SINGLE FAMILY COMPARABLE RENT SCHEDULE",
    "Comparable Sales Number": "COMPARABLE SALE NO.",
    "Location": "LOCATED AT",
    "Appraisal Value": "APPRAISED VALUE OF SUBJECT PROPERTY",
    "Information PUDs": "Project Information for PUDs",
}