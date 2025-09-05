# Children's Story Generator

A comprehensive Python system for generating educational children's stories using the Poe API. This system extends your existing collection of 1,500 stories to 10,000 stories with systematic diversity and quality control.

## Features

- **Systematic Diversity**: Ensures equal usage of 200 characters, 100 settings, and balanced tag combinations
- **Quality Control**: Validates stories for word count, reading level, sentiment, and educational value
- **Rate Limiting**: Respects API limits with automatic retry logic
- **Progress Tracking**: Comprehensive logging and resumable generation
- **Batch Processing**: Efficient processing with error recovery
- **Educational Focus**: Stories designed for children aged 3+ with positive messages

## Quick Start

### 1. Installation

```bash
# Clone or download the project
# Navigate to the project directory

# Run setup
python setup.py

# Install dependencies
pip install -r requirements.txt

# Set your API key
export POE_API_KEY="your_api_key_here"
```

### 2. Test the System

```bash
# Generate 5 test stories
python generate_stories.py --test

# Generate 10 test stories
python generate_stories.py --test --size 10
```

### 3. Full Generation

```bash
# Generate all stories (1501-10000)
python generate_stories.py --generate
```

## Project Structure

```
synthetic-stories/
├── data/                       # Story data and configuration
│   ├── characters.json         # 200 diverse characters
│   ├── settings.json          # 100 varied settings
│   ├── tags.json              # Educational tags
│   └── stories/               # Your existing stories
├── src/                       # Core Python modules
│   ├── story_generator.py     # Main generation logic
│   ├── diversity_tracker.py   # Systematic diversity
│   ├── poe_client.py         # API client with rate limiting
│   ├── story_validator.py    # Quality assurance
│   └── batch_processor.py    # Batch management
├── config/                    # Configuration files
│   └── generation_config.yaml
├── output/                    # Generated stories
│   └── generated_stories/
├── logs/                      # Generation logs
└── generate_stories.py       # Main CLI script
```

## Usage Examples

### Basic Commands

```bash
# Run test generation
python generate_stories.py --test

# Full generation (1501-10000)
python generate_stories.py --generate

# Generate specific range
python generate_stories.py --batch 1501 1600

# Retry failed stories
python generate_stories.py --retry

# Show statistics
python generate_stories.py --stats
```

### Advanced Usage

```bash
# Verbose output
python generate_stories.py --test --verbose

# Quiet mode
python generate_stories.py --generate --quiet

# Custom configuration
python generate_stories.py --generate --config my_config.yaml
```

## Configuration

Edit `config/generation_config.yaml` to customize:

```yaml
generation:
  start_id: 1501
  end_id: 10000
  batch_size: 50
  use_existing_inspiration: 0.3

quality:
  min_words: 600
  max_words: 700
  required_sentiment_score: 0.1

poe_api:
  model: "gpt-4"
  rate_limit: 10
  temperature: 0.7
```

## Story Generation Process

### 1. Systematic Diversity

The system ensures diversity through:

- **Character Rotation**: Cycles through all 200 characters systematically
- **Setting Distribution**: Uses all 100 settings proportionally
- **Tag Balancing**: Selects 3-5 tags from different categories
- **Type Alternation**: Balances "problem_solution" and "daily_adventure" stories
- **Inspiration Integration**: 30% chance to use existing stories as inspiration

### 2. Quality Control

Each story is validated for:

- **Word Count**: 600-700 words
- **Reading Level**: Appropriate for age 3+
- **Sentiment**: Positive and encouraging
- **Structure**: Proper YAML frontmatter and story format
- **Educational Value**: Clear learning objectives

### 3. Generated Story Format

```markdown
---
id: story_1501
type: problem_solution
characters: ["A curious fox kit"]
setting: cozy bedroom
words: 645
tags: ["curiosity", "problem-solving", "courage", "friendship"]
---

# Fox's Big Discovery

[Story content here...]

The End.
```

## Monitoring Progress

### Real-time Statistics

```bash
python generate_stories.py --stats
```

Shows:

- Stories completed/remaining
- Success rate
- Character/setting usage balance
- Diversity metrics

### Log Files

- `logs/generation.log` - Detailed generation logs
- `logs/progress.json` - Current progress state
- `logs/batch_report_*.json` - Batch completion reports

## Expected Results

### Generation Metrics

- **Total Stories**: 8,500 new stories (1501-10000)
- **Character Usage**: Each character appears 42-43 times
- **Setting Usage**: Each setting appears ~85 times
- **Perfect Balance**: Equal distribution across all elements

### Timeline

- **Setup**: 30 minutes
- **Testing**: 1 hour
- **Full Generation**: 20-40 hours (depending on rate limits)
- **Quality Review**: 2-4 hours

### Cost Estimation

- **API Calls**: ~8,500 requests
- **Tokens**: ~8.5M tokens
- **Estimated Cost**: $170-340 (depending on Poe pricing)

## Troubleshooting

### Common Issues

1. **API Key Not Set**

   ```bash
   export POE_API_KEY="your_key_here"
   ```

2. **Rate Limit Errors**

   - System automatically handles rate limiting
   - Adjust `rate_limit` in config if needed

3. **Generation Failures**

   ```bash
   python generate_stories.py --retry
   ```

4. **Memory Issues**
   - Reduce `batch_size` in configuration
   - Process smaller ranges manually

### Resuming Generation

The system automatically resumes from where it left off:

```bash
# This will continue from the last completed story
python generate_stories.py --generate
```

### Validation Issues

If stories fail validation:

1. Check the logs for specific errors
2. Adjust quality thresholds in config
3. Use `--retry` to regenerate failed stories

## Advanced Features

### Custom Prompts

Modify prompt templates in `src/poe_client.py`:

```python
def build_story_prompt(self, story_id, character, setting, tags, story_type, base_story=None):
    # Customize prompt here
```

### Additional Validation

Add custom validators in `src/story_validator.py`:

```python
def custom_validation(self, content):
    # Your validation logic
```

### Different Models

Change the AI model in configuration:

```yaml
poe_api:
  model: "claude-2" # or other available models
```

## Support

### Logging

All operations are logged to `logs/generation.log`. For debugging:

```bash
python generate_stories.py --test --verbose
```

### Progress Recovery

If generation is interrupted, simply restart:

```bash
python generate_stories.py --generate
```

The system will resume from the last completed story.

## License

This project is designed for educational story generation. Please ensure compliance with Poe API terms of service.

---

**Ready to generate 8,500 educational children's stories!**

Start with `python generate_stories.py --test` to verify everything works, then run `python generate_stories.py --generate` for full generation.
