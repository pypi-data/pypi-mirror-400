# Ediq - AI Detection SDK

Official Python client for Ediq AI Detection API by Wyzcon.

Detect AI-generated content in **educational documents** (essays, assignments) and **HR documents** (resumes, cover letters, LinkedIn profiles) with 96% accuracy.

## Installation

```bash
pip install ediq
```

## Quick Start

```python
from ediq import Ediq

client = Ediq("wyz_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

# Education: Detect AI in student essays
result = client.detect_edu("Student essay text...")
print(f"AI Probability: {result.probability}%")

# HR: Detect AI in resumes
result = client.detect_hr("Resume text...", context="resume")
print(f"AI Probability: {result.probability}%")
```

## Get Your API Key

1. Sign up at [wyzcon.com](https://wyzcon.com)
2. Get your free API key
3. Start detecting AI content

## Two Detection Modes

### 🎓 Education Mode
For essays, assignments, and student work. Supports student baselines for personalized detection.

### 💼 HR Mode
For resumes, cover letters, and LinkedIn profiles. Optimized for professional document patterns.

## Features

- ✅ **96% accuracy** on 10,000+ tested documents
- ✅ **9-layer detection** system
- ✅ **Student baselines** - Protect good writers (Education)
- ✅ **HR context awareness** - Resume, cover letter, LinkedIn (HR)
- ✅ **Photo scanning** - OCR for handwritten work
- ✅ **Comprehensive reports** - Detailed analysis
- ✅ **Type hints** - Full autocomplete support

## Education Mode Examples

### Basic Education Detection

```python
from ediq import Ediq

client = Ediq("your_api_key")

# Analyze student essay
result = client.detect_edu("The importance of renewable energy...")
print(f"AI: {result.probability}%")
print(f"Assessment: {result.assessment}")
```

### With Student Baseline

Compare against a student's verified previous work to reduce false positives:

```python
result = client.detect_edu(
    text="Current submission...",
    student_id="john_doe",
    baseline="Previous authentic work..."
)

print(f"AI: {result.probability}%")
print(f"Baseline Similarity: {result.baseline_similarity:.1%}")
```

### Detect from File (Education)

```python
result = client.detect_edu_file("essay.pdf")
print(f"AI: {result.probability}%")
```

### Detect from Image (Handwritten)

```python
result = client.detect_edu_image(
    "handwritten_essay.jpg",
    handwritten=True
)
print(f"AI: {result.probability}%")
```

### Formal Writing Mode

For academic papers and formal essays (reduces false positives):

```python
result = client.detect_edu(
    text="Formal academic paper...",
    formal_mode=True
)
```

## HR Mode Examples

### Detect AI in Resume

```python
from ediq import Ediq, HRContextType

client = Ediq("your_api_key")

# Analyze resume text
result = client.detect_hr(
    text="Experienced software engineer with 5+ years...",
    context="resume"  # or HRContextType.RESUME
)

print(f"AI: {result.probability}%")
print(f"Assessment: {result.assessment}")
```

### Detect AI in Cover Letter

```python
result = client.detect_hr(
    text="I am writing to express my interest...",
    context="cover_letter"
)
print(f"AI: {result.probability}%")
```

### Detect AI in LinkedIn Profile

```python
result = client.detect_hr(
    text="Passionate technology leader driving innovation...",
    context="linkedin_profile"
)
print(f"AI: {result.probability}%")
```

### Detect from HR File

```python
# Analyze resume PDF
result = client.detect_hr_file(
    "resume.pdf",
    context="resume"
)
print(f"AI: {result.probability}%")

# Analyze cover letter DOCX
result = client.detect_hr_file(
    "cover_letter.docx",
    context="cover_letter"
)
```

### With Comprehensive Report

```python
result = client.detect_hr(
    text="Resume text...",
    context="resume",
    include_report=True
)

print(result.report)  # Detailed writing analysis
```

## HR Context Types

| Context | Use For |
|---------|---------|
| `resume` | CV, resume documents |
| `cover_letter` | Job application cover letters |
| `linkedin_profile` | LinkedIn about/summary sections |
| `other` | Other professional documents |

## Check Usage

```python
usage = client.usage()
print(f"Used: {usage.used}/{usage.limit}")
print(f"Remaining: {usage.remaining}")
print(f"Tier: {usage.tier}")
```

## DetectionResult Properties

| Property | Type | Description |
|----------|------|-------------|
| `probability` | float | AI probability (0-100) |
| `assessment` | str | Category: likely_human, borderline, suspicious, likely_ai, highly_likely_ai |
| `confidence` | float | Confidence score (0-100) |
| `word_count` | int | Words analyzed |
| `mode` | str | Detection mode: "education" or "hr" |
| `scan_id` | int | Saved scan ID |
| `baseline_similarity` | float | Baseline match (Education only) |
| `hr_context` | str | Document context (HR only) |
| `report` | dict | Full writing analysis (if requested) |
| `layers` | dict | Layer-by-layer breakdown |

## Error Handling

```python
from ediq import Ediq, EdiqError, RateLimitError, AuthenticationError

client = Ediq("your_api_key")

try:
    result = client.detect_edu("Text...")
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded - wait and retry")
except EdiqError as e:
    print(f"API error: {e}")
```

## Migration from v1.x

The old methods still work but are deprecated:

```python
# Old (still works, defaults to education mode)
result = client.detect("Text...")
result = client.detect_file("essay.pdf")
result = client.detect_image("photo.jpg")

# New (explicit mode selection)
result = client.detect_edu("Text...")
result = client.detect_hr("Text...", context="resume")
```

## Documentation

Full documentation at [docs.wyzcon.com](https://docs.wyzcon.com)

## License

MIT License
