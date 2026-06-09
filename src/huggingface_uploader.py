"""
Hugging Face Dataset Uploader for Children's Stories

This module provides functionality to:
1. Convert markdown stories to JSONL format
2. Upload the dataset to Hugging Face Hub
3. Manage dataset metadata and configuration
"""

import json
import os
import re
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

try:
    from huggingface_hub import HfApi, create_repo, upload_file
    from datasets import Dataset, DatasetDict
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    logging.warning("Hugging Face libraries not available. Install with: pip install huggingface_hub datasets")


class StoryParser:
    """Parse markdown stories with frontmatter into structured data"""
    
    def __init__(self):
        self.frontmatter_pattern = re.compile(r'^---\n(.*?)\n---\n(.*)', re.DOTALL)
    
    def parse_story_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse a single story markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            match = self.frontmatter_pattern.match(content)
            if not match:
                logging.warning(f"No frontmatter found in {file_path}")
                return None
            
            frontmatter_str, story_content = match.groups()
            
            # Parse YAML frontmatter
            try:
                metadata = yaml.safe_load(frontmatter_str)
            except yaml.YAMLError as e:
                logging.error(f"Error parsing frontmatter in {file_path}: {e}")
                return None

            if not isinstance(metadata, dict):
                logging.warning(f"Frontmatter metadata in {file_path} must be a mapping")
                return None

            characters = self._metadata_string_list(metadata, "characters", file_path)
            tags = self._metadata_string_list(metadata, "tags", file_path)
            if characters is None or tags is None:
                return None
            
            # Clean and extract story text
            story_text = self._extract_story_text(story_content.strip())
            
            # Create structured record
            record = {
                "id": metadata.get("id", file_path.stem),
                "title": self._extract_title(story_content),
                "text": story_text,
                "type": metadata.get("type", "unknown"),
                "characters": characters,
                "setting": metadata.get("setting", ""),
                "word_count": metadata.get("words", len(story_text.split())),
                "tags": tags,
                "source_file": str(file_path.name),
                "created_at": datetime.now().isoformat()
            }
            
            return record
            
        except Exception as e:
            logging.error(f"Error parsing {file_path}: {e}")
            return None

    def _metadata_string_list(self, metadata: Dict[str, Any], field: str, file_path: Path) -> Optional[List[str]]:
        """Return a non-empty list of strings for list-typed dataset fields."""
        values = metadata.get(field)
        if not isinstance(values, list) or not values:
            logging.warning(f"Frontmatter {field} in {file_path} must be a non-empty list")
            return None

        normalized = []
        for value in values:
            if not isinstance(value, str) or not value.strip():
                logging.warning(f"Frontmatter {field} in {file_path} must contain only non-empty strings")
                return None
            normalized.append(value.strip())

        return normalized
    
    def _extract_title(self, content: str) -> str:
        """Extract title from markdown content"""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return "Untitled Story"
    
    def _extract_story_text(self, content: str) -> str:
        """Extract clean story text, removing markdown formatting"""
        # Remove title line
        lines = content.split('\n')
        if lines and lines[0].startswith('# '):
            lines = lines[1:]
        
        # Join and clean
        text = '\n'.join(lines).strip()
        
        # Basic markdown cleanup (keep it simple for story text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Remove italic markers
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove bold markers
        text = re.sub(r'\n\n+', '\n\n', text)  # Normalize paragraph spacing
        
        return text


class HuggingFaceUploader:
    """Upload children's stories dataset to Hugging Face Hub"""
    
    def __init__(self, token: Optional[str] = None):
        if not HF_AVAILABLE:
            raise ImportError("Hugging Face libraries not available. Install with: pip install huggingface_hub datasets")
        
        self.api = HfApi(token=token)
        self.token = token
        self.parser = StoryParser()
    
    def convert_stories_to_jsonl(self, 
                                stories_dir: Path, 
                                output_file: Path,
                                include_existing: bool = True,
                                include_generated: bool = True) -> int:
        """Convert all story files to JSONL format"""
        records = []
        
        # Process different story directories
        directories_to_process = []
        
        if include_existing:
            existing_dir = stories_dir / "data" / "stories"
            if existing_dir.exists():
                directories_to_process.append(("existing", existing_dir))
        
        if include_generated:
            generated_dir = stories_dir / "output" / "generated_stories"
            if generated_dir.exists():
                directories_to_process.append(("generated", generated_dir))
        
        for source_type, directory in directories_to_process:
            logging.info(f"Processing {source_type} stories from {directory}")
            
            for file_path in directory.glob("*.md"):
                record = self.parser.parse_story_file(file_path)
                if record:
                    record["source_type"] = source_type
                    records.append(record)
                else:
                    logging.warning(f"Failed to parse {file_path}")
        
        # Write to JSONL
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        logging.info(f"Converted {len(records)} stories to {output_file}")
        return len(records)
    
    def create_dataset_card(self, repo_name: str = "your-username/children-stories-dataset") -> str:
        """Create a README.md for the dataset with proper YAML metadata"""
        return f"""---
annotations_creators:
- no-annotation
language_creators:
- machine-generated
language:
- en
license:
- cc-by-4.0
multilinguality:
- monolingual
size_categories:
- 1K<n<10K
source_datasets:
- original
task_categories:
- text-generation
task_ids:
- language-modeling
- text2text-generation
paperswithcode_id: null
pretty_name: Children's Stories Dataset
tags:
- children-stories
- educational
- storytelling
- creative-writing
- moral-values
- problem-solving
- emotional-intelligence
dataset_info:
  features:
  - name: id
    dtype: string
  - name: title
    dtype: string
  - name: text
    dtype: string
  - name: type
    dtype: string
  - name: characters
    sequence: string
  - name: setting
    dtype: string
  - name: word_count
    dtype: int64
  - name: tags
    sequence: string
  - name: source_type
    dtype: string
  - name: source_file
    dtype: string
  - name: created_at
    dtype: string
  config_name: default
  data_files:
  - split: train
    path: train.jsonl
  default: true
---

# Children's Stories Dataset

## Dataset Description

This dataset contains a collection of children's stories designed to teach positive values, problem-solving skills, and emotional intelligence. The stories feature diverse characters and settings, making them suitable for children aged 3-8.

## Dataset Structure

Each story record contains:

- `id`: Unique story identifier
- `title`: Story title
- `text`: Full story text
- `type`: Story type (e.g., "daily_adventure", "problem_solution")
- `characters`: List of main characters
- `setting`: Story setting/location
- `word_count`: Number of words in the story
- `tags`: Educational and thematic tags
- `source_type`: Whether the story is "existing" or "generated"
- `source_file`: Original filename
- `created_at`: Timestamp of dataset creation

## Educational Themes

The stories cover various educational themes including:

- Problem-solving and critical thinking
- Friendship and cooperation
- Emotional awareness and regulation
- Creativity and imagination
- Kindness and empathy
- Persistence and growth mindset
- Environmental awareness
- Cultural diversity and inclusion

## Usage

```python
from datasets import load_dataset

dataset = load_dataset("{repo_name}")

# Access a story
story = dataset["train"][0]
print(f"Title: {{story['title']}}")
print(f"Characters: {{story['characters']}}")
print(f"Setting: {{story['setting']}}")
print(f"Story: {{story['text']}}")
```

## Dataset Statistics

This dataset includes thousands of carefully curated children's stories with:

- Age-appropriate content (3-8 years)
- Positive educational themes
- Diverse character representation
- Various story settings and scenarios
- Educational tags for easy filtering

## Citation

If you use this dataset in your research, please cite:

```bibtex
@dataset{{children_stories_dataset,
  title={{Children's Stories Dataset}},
  author={{Your Name}},
  year={{2025}},
  url={{https://huggingface.co/datasets/{repo_name}}}
}}
```

## License

This dataset is released under the Creative Commons Attribution 4.0 International License (CC BY 4.0).

## Ethical Considerations

- All stories promote positive values and educational content
- Content is appropriate for children aged 3-8
- Stories encourage diversity, inclusion, and positive social values
- No harmful or inappropriate content included
"""
    
    def upload_dataset(self,
                      jsonl_file: Path,
                      repo_name: str,
                      private: bool = False,
                      commit_message: str = "Upload children's stories dataset") -> str:
        """Upload dataset to Hugging Face Hub"""
        
        try:
            # Create repository
            repo_url = create_repo(
                repo_id=repo_name,
                repo_type="dataset",
                private=private,
                token=self.token,
                exist_ok=True
            )
            logging.info(f"Repository created/found: {repo_url}")
            
            # Upload JSONL file
            upload_file(
                path_or_fileobj=str(jsonl_file),
                path_in_repo="train.jsonl",
                repo_id=repo_name,
                repo_type="dataset",
                token=self.token,
                commit_message=commit_message
            )
            logging.info(f"Uploaded {jsonl_file} to {repo_name}")
            
            # Create and upload README
            readme_content = self.create_dataset_card(repo_name)
            readme_path = jsonl_file.parent / "README.md"
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            upload_file(
                path_or_fileobj=str(readme_path),
                path_in_repo="README.md",
                repo_id=repo_name,
                repo_type="dataset",
                token=self.token,
                commit_message="Add dataset documentation"
            )
            logging.info(f"Uploaded README.md to {repo_name}")
            
            return repo_url
            
        except Exception as e:
            logging.error(f"Error uploading dataset: {e}")
            raise
    
    def create_and_upload_dataset(self,
                                 stories_dir: Path,
                                 repo_name: str,
                                 output_dir: Path = None,
                                 private: bool = False,
                                 include_existing: bool = True,
                                 include_generated: bool = True) -> Dict[str, Any]:
        """Complete pipeline: convert stories to JSONL and upload to HF Hub"""
        
        if output_dir is None:
            output_dir = stories_dir / "output" / "huggingface"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        jsonl_file = output_dir / "children_stories_dataset.jsonl"
        
        # Convert stories to JSONL
        num_stories = self.convert_stories_to_jsonl(
            stories_dir=stories_dir,
            output_file=jsonl_file,
            include_existing=include_existing,
            include_generated=include_generated
        )
        
        # Upload to Hugging Face Hub
        repo_url = self.upload_dataset(
            jsonl_file=jsonl_file,
            repo_name=repo_name,
            private=private
        )
        
        return {
            "repo_url": repo_url,
            "jsonl_file": str(jsonl_file),
            "num_stories": num_stories,
            "upload_time": datetime.now().isoformat()
        }


def main():
    """CLI interface for uploading dataset"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Upload children's stories to Hugging Face Hub")
    parser.add_argument("--repo-name", required=True, help="Hugging Face repository name (e.g., 'username/dataset-name')")
    parser.add_argument("--token", help="Hugging Face token (or set HF_TOKEN env var)")
    parser.add_argument("--private", action="store_true", help="Create private repository")
    parser.add_argument("--stories-dir", default=".", help="Root directory containing stories")
    parser.add_argument("--output-dir", help="Output directory for JSONL file")
    parser.add_argument("--existing-only", action="store_true", help="Include only existing stories")
    parser.add_argument("--generated-only", action="store_true", help="Include only generated stories")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Get token
    token = args.token or os.getenv('HF_TOKEN')
    if not token:
        raise ValueError("Please provide Hugging Face token via --token or HF_TOKEN environment variable")
    
    # Determine what to include
    include_existing = not args.generated_only
    include_generated = not args.existing_only
    
    # Create uploader and run
    uploader = HuggingFaceUploader(token=token)
    
    result = uploader.create_and_upload_dataset(
        stories_dir=Path(args.stories_dir),
        repo_name=args.repo_name,
        output_dir=Path(args.output_dir) if args.output_dir else None,
        private=args.private,
        include_existing=include_existing,
        include_generated=include_generated
    )
    
    print(f"✅ Successfully uploaded dataset!")
    print(f"📁 Repository: {result['repo_url']}")
    print(f"📄 JSONL file: {result['jsonl_file']}")
    print(f"📚 Stories included: {result['num_stories']}")


if __name__ == "__main__":
    main()
