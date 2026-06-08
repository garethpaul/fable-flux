"""
Story Validator for Quality Assurance
Validates generated stories for format, content quality, and educational value
"""

import re
import yaml
import logging
from typing import Any, Dict, List, Tuple, Optional
from collections import Counter
import json

# Try to import optional dependencies for advanced validation
try:
    from textstat import flesch_reading_ease, flesch_kincaid_grade
    HAS_TEXTSTAT = True
except ImportError:
    HAS_TEXTSTAT = False
    logging.warning("textstat not available - using simplified readability checks")

try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False
    logging.warning("textblob not available - using simplified sentiment analysis")

class StoryValidator:
    """
    Comprehensive validator for generated children's stories
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.min_words = self.config.get('min_words', 600)
        self.max_words = self.config.get('max_words', 700)
        self.required_sentiment_score = self.config.get('required_sentiment_score', 0.1)
        self.min_reading_ease = self.config.get('min_reading_ease', 70)
        
        # Common words for 3+ year olds
        self.age_appropriate_indicators = {
            'simple_words': ['happy', 'sad', 'big', 'small', 'good', 'bad', 'nice', 'fun', 'play', 'friend'],
            'complex_words': ['subsequently', 'nevertheless', 'consequently', 'furthermore', 'moreover']
        }
        
    def validate_story(self, content: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Comprehensive story validation
        
        Args:
            content: The complete story content including YAML frontmatter
            
        Returns:
            Tuple of (is_valid: bool, validation_results: dict)
        """
        results = {
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'metrics': {}
        }
        
        try:
            # Parse and validate structure
            frontmatter, story_content = self._parse_story_structure(content)
            if not frontmatter or not story_content:
                results['errors'].append("Invalid story structure - missing frontmatter or content")
                return False, results
                
            results['metrics']['frontmatter'] = frontmatter
            
            # Validate frontmatter
            frontmatter_valid, frontmatter_errors = self._validate_frontmatter(frontmatter)
            if not frontmatter_valid:
                results['errors'].extend(frontmatter_errors)
                
            # Validate content
            content_metrics = self._analyze_content(story_content)
            results['metrics'].update(content_metrics)
            
            # Word count validation
            word_count = content_metrics['word_count']
            if not (self.min_words <= word_count <= self.max_words):
                results['errors'].append(f"Word count {word_count} outside range {self.min_words}-{self.max_words}")
                
            # Reading level validation
            if content_metrics.get('reading_ease', 0) < self.min_reading_ease:
                results['warnings'].append(f"Reading ease {content_metrics.get('reading_ease', 'unknown')} may be too difficult for age 3+")
                
            # Sentiment validation
            sentiment_score = content_metrics.get('sentiment_score', 0)
            if sentiment_score < self.required_sentiment_score:
                results['errors'].append(f"Sentiment score {sentiment_score:.2f} too negative (required: {self.required_sentiment_score})")
                
            # Structure validation
            structure_valid, structure_errors = self._validate_story_structure(story_content)
            if not structure_valid:
                results['errors'].extend(structure_errors)
                
            # Age appropriateness
            age_appropriate, age_warnings = self._check_age_appropriateness(story_content)
            if age_warnings:
                results['warnings'].extend(age_warnings)
                
            # Educational value
            educational_score = self._assess_educational_value(story_content, frontmatter.get('tags', []))
            results['metrics']['educational_score'] = educational_score
            if educational_score < 0.5:
                results['warnings'].append(f"Low educational value score: {educational_score:.2f}")
                
            # Overall validation
            results['is_valid'] = len(results['errors']) == 0
            
            if results['is_valid']:
                logging.debug(f"Story validation passed with {len(results['warnings'])} warnings")
            else:
                logging.warning(f"Story validation failed with {len(results['errors'])} errors")
                
        except Exception as e:
            results['errors'].append(f"Validation error: {str(e)}")
            logging.error(f"Story validation exception: {e}")
            
        return results['is_valid'], results
        
    def _parse_story_structure(self, content: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Parse YAML frontmatter and story content
        """
        if not content.strip().startswith("---"):
            return None, None
            
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None, None
            
        try:
            frontmatter = yaml.safe_load(parts[1])
            story_content = parts[2].strip()
            return frontmatter, story_content
        except yaml.YAMLError as e:
            logging.error(f"YAML parsing error: {e}")
            return None, None
            
    def _validate_frontmatter(self, frontmatter: Dict) -> Tuple[bool, List[str]]:
        """
        Validate YAML frontmatter structure and content
        """
        errors = []
        required_fields = ['id', 'type', 'characters', 'setting', 'words', 'tags']
        
        for field in required_fields:
            if field not in frontmatter:
                errors.append(f"Missing required field: {field}")
                
        # Validate specific fields
        if 'type' in frontmatter:
            valid_types = ['problem_solution', 'daily_adventure']
            if frontmatter['type'] not in valid_types:
                errors.append(f"Invalid story type: {frontmatter['type']}. Must be one of {valid_types}")
                
        if 'characters' in frontmatter:
            if not isinstance(frontmatter['characters'], list) or len(frontmatter['characters']) == 0:
                errors.append("Characters must be a non-empty list")
                
        if 'tags' in frontmatter:
            if not isinstance(frontmatter['tags'], list) or len(frontmatter['tags']) == 0:
                errors.append("Tags must be a non-empty list")
                
        return len(errors) == 0, errors
        
    def _analyze_content(self, content: str) -> Dict:
        """
        Analyze story content for various metrics
        """
        metrics = {}
        
        # Basic metrics
        words = content.split()
        metrics['word_count'] = len(words)
        metrics['sentence_count'] = len(re.findall(r'[.!?]+', content))
        metrics['paragraph_count'] = len([p for p in content.split('\n\n') if p.strip()])
        
        # Dialogue detection
        dialogue_matches = re.findall(r'"[^"]*"', content)
        metrics['dialogue_count'] = len(dialogue_matches)
        metrics['has_dialogue'] = len(dialogue_matches) > 0
        
        # Reading level analysis
        if HAS_TEXTSTAT and len(words) > 10:
            try:
                metrics['reading_ease'] = flesch_reading_ease(content)
                metrics['grade_level'] = flesch_kincaid_grade(content)
            except:
                metrics['reading_ease'] = self._simple_reading_ease(content)
        else:
            metrics['reading_ease'] = self._simple_reading_ease(content)
            
        # Sentiment analysis
        if HAS_TEXTBLOB:
            try:
                blob = TextBlob(content)
                metrics['sentiment_score'] = blob.sentiment.polarity
                metrics['sentiment_subjectivity'] = blob.sentiment.subjectivity
            except:
                metrics['sentiment_score'] = self._simple_sentiment(content)
        else:
            metrics['sentiment_score'] = self._simple_sentiment(content)
            
        return metrics
        
    def _simple_reading_ease(self, content: str) -> float:
        """
        Simple reading ease calculation when textstat is not available
        """
        words = content.split()
        sentences = len(re.findall(r'[.!?]+', content))
        
        if sentences == 0:
            return 0
            
        avg_sentence_length = len(words) / sentences
        
        # Count complex words (3+ syllables, simplified)
        complex_words = 0
        for word in words:
            word = re.sub(r'[^a-zA-Z]', '', word.lower())
            if len(word) > 6:  # Rough approximation for complex words
                complex_words += 1
                
        if len(words) == 0:
            return 0
            
        complex_word_ratio = complex_words / len(words)
        
        # Simplified reading ease score (higher = easier)
        ease_score = 100 - (avg_sentence_length * 1.5) - (complex_word_ratio * 100)
        return max(0, min(100, ease_score))
        
    def _simple_sentiment(self, content: str) -> float:
        """
        Simple sentiment analysis when TextBlob is not available
        """
        positive_words = [
            'happy', 'joy', 'love', 'wonderful', 'great', 'good', 'nice', 'fun', 'excited',
            'proud', 'smile', 'laugh', 'friend', 'help', 'kind', 'brave', 'smart', 'beautiful'
        ]
        
        negative_words = [
            'sad', 'angry', 'hate', 'terrible', 'bad', 'mean', 'scary', 'hurt', 'cry',
            'afraid', 'worried', 'mad', 'upset', 'disappointed', 'lonely', 'lost'
        ]
        
        words = [w.lower().strip('.,!?";') for w in content.split()]
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count + negative_count == 0:
            return 0.1  # Neutral but slightly positive
            
        return (positive_count - negative_count) / (positive_count + negative_count)
        
    def _validate_story_structure(self, content: str) -> Tuple[bool, List[str]]:
        """
        Validate story structure elements
        """
        errors = []
        
        # Check for title
        if not re.search(r'^#\s+.+', content, re.MULTILINE):
            errors.append("Story missing title (should start with '# Title')")
            
        # Check for proper ending
        if not content.strip().endswith("The End."):
            errors.append("Story must end with 'The End.'")
            
        # Check for minimum content length
        content_without_title = re.sub(r'^#.*$', '', content, flags=re.MULTILINE).strip()
        if len(content_without_title.split()) < 50:
            errors.append("Story content too short (excluding title)")
            
        return len(errors) == 0, errors
        
    def _check_age_appropriateness(self, content: str) -> Tuple[bool, List[str]]:
        """
        Check if content is appropriate for age 3+
        """
        warnings = []
        words = [w.lower().strip('.,!?";') for w in content.split()]
        
        # Check for overly complex words
        complex_word_count = 0
        for word in words:
            if word in self.age_appropriate_indicators['complex_words']:
                complex_word_count += 1
                
        if complex_word_count > 2:
            warnings.append(f"Contains {complex_word_count} potentially complex words for age 3+")
            
        # Check average word length
        avg_word_length = sum(len(word) for word in words if word.isalpha()) / max(1, len(words))
        if avg_word_length > 6:
            warnings.append(f"Average word length {avg_word_length:.1f} may be too high for age 3+")
            
        return len(warnings) == 0, warnings
        
    def _assess_educational_value(self, content: str, tags: List[str]) -> float:
        """
        Assess the educational value of the story
        """
        score = 0.0
        
        # Check for explicit learning themes in content
        learning_indicators = [
            'learn', 'teach', 'practice', 'try', 'help', 'share', 'kind', 'friend',
            'problem', 'solve', 'think', 'feel', 'understand', 'discover', 'find'
        ]
        
        words = [w.lower().strip('.,!?";') for w in content.split()]
        learning_word_count = sum(1 for word in words if word in learning_indicators)
        
        # Score based on learning words density
        if len(words) > 0:
            learning_density = learning_word_count / len(words)
            score += min(0.4, learning_density * 10)  # Max 0.4 points
            
        # Score based on tag relevance
        if tags:
            educational_tags = [
                'education', 'learning', 'problem-solving', 'creativity', 'empathy',
                'kindness', 'friendship', 'responsibility', 'courage', 'patience'
            ]
            relevant_tags = sum(1 for tag in tags if tag in educational_tags)
            score += min(0.3, relevant_tags * 0.1)  # Max 0.3 points
            
        # Check for moral/lesson conclusion
        last_paragraphs = ' '.join(content.split('\n\n')[-2:]).lower()
        lesson_indicators = ['learned', 'important', 'remember', 'always', 'never forget', 'realized']
        
        if any(indicator in last_paragraphs for indicator in lesson_indicators):
            score += 0.3
            
        return min(1.0, score)
        
    def quick_validate(self, content: str) -> bool:
        """
        Quick validation for basic requirements
        """
        try:
            # Check basic structure
            if not content.startswith("---") or "The End." not in content:
                return False
                
            # Check word count roughly
            word_count = len(content.split())
            if not (self.min_words * 0.8 <= word_count <= self.max_words * 1.2):
                return False
                
            # Check for YAML frontmatter
            parts = content.split("---", 2)
            if len(parts) < 3:
                return False
                
            yaml.safe_load(parts[1])  # Will raise exception if invalid
            return True
            
        except Exception:
            return False

def validate_story_file(filepath: str, validator: StoryValidator = None) -> Tuple[bool, Dict]:
    """
    Validate a story from a file
    """
    if validator is None:
        validator = StoryValidator()
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return validator.validate_story(content)
    except Exception as e:
        return False, {'errors': [f"File read error: {e}"]}
