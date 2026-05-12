import re


def analyze_spm(html_text: str):
    matches = re.findall(
        r'<span class="SmallFormData">\s*([SPM])\s*</span>',
        html_text
    )

    return (
        matches.count("S"),
        matches.count("P"),
        matches.count("M"),
    )