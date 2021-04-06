WHITE_PAPER = "WHITE_PAPER"  # jaki jest stan AI
GUIDANCE = "GUIDANCE"
STRATEGY = "STRATEGY"  # jak należy działać względem AI
POLICY = (
    "POLICY"  # jak konkretne instytucje (głównie państwowe) powinny działać wobec AI
)
DECLARATION = "DECLARATION"  # jakie deklaracje działań podejmują konkretne instytucje
PROPOSITION_REGULATION = "PROPOSITION_REGULATION"  # proponowane regulacje
PILOT_REGULATION = (
    "PILOT_REGULATION"
)  # regulacja, która weszła w życie, ale ma ograniczony zasięg działania, bo jest poddawana ewaluacji
SELF_REGULATION = (
    "SELF_REGULATION"
)  # aktorzy/podmioty używające AI same samoograniczają się - same siebie regulują w relacjach do AI
PROPER_REGULATION = (
    "PROPER_REGULATION"
)  # regulacje, które weszły w życie (zakładamy, że tu państwo narzuca innym podmiotom zasady działania związane z AI)
INTERNATIONAL_AGREEMENT = "INTERNATIONAL_AGREEMENT"  # międzynarodowe umowy dotyczące AI
# REGULATION = "REGULATION"

_reverse_mapping = {
    WHITE_PAPER: ["White paper", "Report"],  # jaki jest stan AI
    GUIDANCE: [
        "Guidelines",
        "Guidance",
        "Ethics guidelines",
        "Code of practice",
        "Opinion, Ethics guidelines",
        "Principles",
    ],  # jakimi zasadami powinniśmy kierować się względem AI
    STRATEGY: [
        "Strategy",
        "Network, Strategy",
        "Strategy, Report",
        "Action plan",
    ],  # jak należy działać względem AI
    POLICY: [
        "Policy paper",
        "Policy briefing",
        "Policy",
        "Action programme",
    ],  # jak konkretne instytucje (głównie państwowe) powinny działać wobec AI
    DECLARATION: [
        "Declaration",
        "Statement",
        "Resolution",
    ],  # jakie deklaracje działań podejmują konkretne instytucje
    PROPOSITION_REGULATION: [
        "Proposed regulation",
        "Proposed law",
        "Proposal",
    ],  # proponowane regulacje
    PILOT_REGULATION: [
        "Pilot, Regulation",
        "Pilot",
        "Test environment",
    ],  # regulacja, która weszła w życie, ale ma ograniczony zasięg działania, bo jest poddawana ewaluacji
    SELF_REGULATION: [
        "Self-regulation",
        "Self-regulation, Standardisation",
        "Standardisation",
        "Self-regulation, Ethics guidelines",
        "Self-regulation, Policy principles",
    ],  # aktorzy/podmioty używające AI same samoograniczają się - same siebie regulują w relacjach do AI
    PROPER_REGULATION: [
        "Regulation",
        "Legislation",
        "Bill",
        "Directive",
        "Local law",
        "Federal law",
        "State legislation",
        "Local law, Task force",
    ],  # regulacje, które weszły w życie (zakładamy, że tu państwo narzuca innym podmiotom zasady działania związane z AI)
    INTERNATIONAL_AGREEMENT: [
        "Partnership, International agreement",
        "International agreement",
        "Declaration, International agreement",
        "Treaty",
    ],  # międzynarodowe umowy dotyczące AI
}

mapping = {
    value: key for key, values_list in _reverse_mapping.items() for value in values_list
}

classes_to_remove = [
    "Research",
    "Education",
    "Advisory body",
    "Observatory",
    "Partnership",
    "Working group",
    "Network",
    "Government body",
    "Task force",
    "Resource",
    "Select Committee",
    "Caucus",
    "Government community",
]
