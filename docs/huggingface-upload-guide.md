# Hugging Face Dataset Upload Guide

This guide provides detailed instructions for uploading your children's stories collection to Hugging Face Hub as a dataset.

## Overview

The Hugging Face upload functionality converts your markdown stories into a standardized JSONL dataset format and uploads it to Hugging Face Hub, making your educational content accessible to researchers, educators, and developers worldwide.

## Quick Start

### 1. Install Dependencies

```bash
pip install huggingface_hub datasets
```

### 2. Get Hugging Face Token

1. Visit [Hugging Face Settings](https://huggingface.co/settings/tokens)
2. Create a new token with "Write" permissions
3. Set as environment variable:
   ```bash
   export HF_TOKEN="your_token_here"
   ```

### 3. Test the System

```bash
python test_huggingface_upload.py
```

### 4. Upload Dataset

```bash
# Interactive upload
python upload_to_huggingface.py

# Quick upload
python upload_to_huggingface.py --repo-name "username/children-stories-dataset" --quick
```

## Current Dataset Stats

Based on your current collection:

- **Total Stories**: ~10,000 stories
- **Existing Stories**: Stories from `data/stories/` directory
- **Generated Stories**: Stories from `output/generated_stories/` directory
- **Format**: JSONL with comprehensive metadata

## Dataset Structure

Each story record contains:

```json
{
  "id": "story_7801",
  "title": "Rascal's Musical Magic",
  "text": "Full story content...",
  "type": "daily_adventure",
  "characters": ["A musical raccoon"],
  "setting": "musical practice room",
  "word_count": 652,
  "tags": ["art", "peaceful-solutions", "skill-building"],
  "source_type": "generated",
  "source_file": "story_7801.md",
  "created_at": "2024-09-05T23:39:00Z"
}
```

## Upload Options

### Basic Upload

```bash
python upload_to_huggingface.py --repo-name "username/dataset-name"
```

### Selective Upload

```bash
# Only existing stories
python upload_to_huggingface.py --repo-name "username/dataset-name" --existing-only

# Only generated stories
python upload_to_huggingface.py --repo-name "username/dataset-name" --generated-only
```

### Private Repository

```bash
python upload_to_huggingface.py --repo-name "username/dataset-name" --private
```

### Command Line Options

```bash
python upload_to_huggingface.py --help
```

## What Gets Uploaded

1. **Dataset File**: `train.jsonl` containing all stories in structured format
2. **Documentation**: `README.md` with comprehensive dataset description
3. **Metadata**: Repository configuration for proper dataset discovery

## Dataset Usage Examples

Once uploaded, users can access your dataset:

### Python with datasets library

```python
from datasets import load_dataset

# Load dataset
dataset = load_dataset("username/children-stories-dataset")

# Access stories
for story in dataset["train"]:
    print(f"Title: {story['title']}")
    print(f"Characters: {story['characters']}")
    print(f"Educational tags: {story['tags']}")
    break
```

### Filter by criteria

```python
# Filter by story type
adventure_stories = dataset.filter(lambda x: x["type"] == "daily_adventure")

# Filter by character type
animal_stories = dataset.filter(lambda x: any("raccoon" in char.lower() for char in x["characters"]))

# Filter by educational themes
creativity_stories = dataset.filter(lambda x: "art" in x["tags"])
```

## Benefits

### For Educators

- Access to high-quality educational stories
- Structured metadata for curriculum planning
- Diverse characters and settings for inclusive education

### For Researchers

- Large-scale children's literature dataset
- Educational content analysis opportunities
- Natural language processing research data

### For Developers

- Training data for educational AI applications
- Content for reading comprehension tools
- Story generation model fine-tuning

## File Structure

After running the upload, you'll have:

```
output/huggingface/
├── children_stories_dataset.jsonl  # Main dataset file
└── README.md                       # Dataset documentation
```

## Troubleshooting

### Common Issues

1. **Missing HF_TOKEN**

   ```bash
   export HF_TOKEN="your_token_here"
   ```

2. **Import Errors**

   ```bash
   pip install huggingface_hub datasets
   ```

3. **Permission Errors**

   - Ensure your token has "Write" permissions
   - Check repository name format: "username/dataset-name"

4. **Large Dataset Upload**
   - Upload process may take several minutes for 8,173 stories
   - Network interruptions are handled with automatic retry

### Validation Errors

If stories fail validation:

- Check `logs/generation.log` for specific errors
- Ensure story files have proper YAML frontmatter
- Verify markdown formatting

### Re-uploading

To update your dataset:

1. Make changes to your stories
2. Re-run the upload command
3. The repository will be updated with new content

## Repository Management

After upload, you can:

- View your dataset at `https://huggingface.co/datasets/username/dataset-name`
- Edit the README through the web interface
- Manage repository settings and permissions
- Track dataset downloads and usage

## Best Practices

### Repository Naming

- Use descriptive names: `children-stories-educational`
- Include relevant keywords for discoverability
- Follow kebab-case convention

### Documentation

- The auto-generated README is comprehensive
- Consider adding custom sections for specific use cases
- Include citation information if desired

### Privacy Considerations

- Use `--private` flag if content is proprietary
- Public datasets get better discoverability
- Consider educational value to the community

## Advanced Usage

### Programmatic Upload

```python
from src.huggingface_uploader import HuggingFaceUploader
from pathlib import Path

uploader = HuggingFaceUploader(token="your_token")
result = uploader.create_and_upload_dataset(
    stories_dir=Path("."),
    repo_name="username/dataset-name",
    private=False
)

print(f"Uploaded {result['num_stories']} stories to {result['repo_url']}")
```

### Custom Dataset Card

Modify the `create_dataset_card()` method in `src/huggingface_uploader.py` to customize the generated README.

---

## Support

For issues with:

- **Upload functionality**: Check logs and error messages
- **Hugging Face platform**: Visit [Hugging Face documentation](https://huggingface.co/docs)
- **Dataset usage**: See [datasets library documentation](https://huggingface.co/docs/datasets/)

The upload system is designed to be robust and user-friendly. Most issues can be resolved by checking environment variables and ensuring proper authentication.
