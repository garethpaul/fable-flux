---
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

dataset = load_dataset("garethpaul/children-stories-dataset")

# Access a story
story = dataset["train"][0]
print(f"Title: {story['title']}")
print(f"Characters: {story['characters']}")
print(f"Setting: {story['setting']}")
print(f"Story: {story['text']}")
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
@dataset{children_stories_dataset,
  title={Children's Stories Dataset},
  author={Gareth Jones},
  year={2025},
  url={https://huggingface.co/datasets/garethpaul/children-stories-dataset}
}
```

## License

This dataset is released under the Creative Commons Attribution 4.0 International License (CC BY 4.0).

## Ethical Considerations

- All stories promote positive values and educational content
- Content is appropriate for children aged 3-8
- Stories encourage diversity, inclusion, and positive social values
- No harmful or inappropriate content included
