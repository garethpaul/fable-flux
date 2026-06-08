"""
Diversity Tracker for Story Generation
Ensures systematic diversity across characters, settings, tags, and story types
"""

import json
import logging
from typing import List, Dict, Set, Tuple
from collections import defaultdict
import random

class DiversityTracker:
    def __init__(self):
        self.character_usage = defaultdict(int)
        self.setting_usage = defaultdict(int)
        self.tag_combinations = defaultdict(int)
        self.story_type_count = {"problem_solution": 0, "daily_adventure": 0}
        self.current_character_index = 0
        self.current_setting_index = 0
        self.recent_tag_combinations = []  # Track recent combinations
        
        # Category mapping for tag diversity
        self.tag_categories = {
            "emotional": ["empathy", "kindness", "compassion", "understanding", "emotional-awareness", 
                         "self-regulation", "mindfulness", "patience", "calmness", "resilience"],
            "learning": ["education", "curiosity", "discovery", "learning", "growth-mindset", 
                        "persistence", "practice", "improvement", "skill-building", "knowledge"],
            "social": ["friendship", "cooperation", "teamwork", "sharing", "taking-turns", 
                      "communication", "listening", "respect", "inclusion", "diversity"],
            "problem_solving": ["problem-solving", "critical-thinking", "creativity", "innovation", 
                               "logical-thinking", "decision-making", "planning", "organization", "strategy", "resourcefulness"],
            "character": ["honesty", "integrity", "responsibility", "fairness", "justice", 
                         "gratitude", "generosity", "helpfulness", "courage", "bravery"],
            "independence": ["self-confidence", "self-esteem", "independence", "self-reliance", 
                           "leadership", "initiative", "assertiveness", "self-advocacy", "personal-boundaries", "self-care"],
            "health": ["healthy-habits", "exercise", "nutrition", "hygiene", "safety", 
                      "outdoor-activity", "sports", "movement", "coordination", "wellness"],
            "environmental": ["environmental-care", "recycling", "conservation", "community-service", 
                            "helping-others", "volunteering", "civic-responsibility", "global-awareness", "sustainability"],
            "creative": ["art", "music", "dance", "writing", "storytelling", "imagination", 
                        "creative-expression", "innovation", "crafting", "building"],
            "daily_life": ["routine", "time-management", "chores", "responsibility", "organization", 
                          "following-directions", "completing-tasks", "goal-setting", "planning", "preparation"],
            "conflict": ["conflict-resolution", "peaceful-solutions", "compromise", "negotiation", 
                        "forgiveness", "apology", "making-amends", "peaceful-communication", "anger-management", "frustration-coping"],
            "diversity": ["cultural-diversity", "acceptance", "inclusion", "celebrating-differences", 
                         "open-mindedness", "tolerance", "respect-for-others", "global-citizenship", "language-appreciation", "tradition-sharing"]
        }
        
        # Reverse mapping: tag -> category
        self.tag_to_category = {}
        for category, tags in self.tag_categories.items():
            for tag in tags:
                self.tag_to_category[tag] = category
                
    def get_next_character(self, characters: List[str]) -> str:
        """
        Get next character using systematic rotation with balance checking
        """
        if not characters:
            raise ValueError("Characters list is empty")
            
        # If we haven't used all characters equally, pick the least used,
        # including characters that have not appeared in usage state yet.
        if self.character_usage:
            usage_counts = {char: self.character_usage.get(char, 0) for char in characters}
            min_usage = min(usage_counts.values())
            least_used = [char for char, count in usage_counts.items() if count == min_usage]
            if least_used:
                character = random.choice(least_used)
                logging.debug(f"Selected least used character: {character} (usage: {min_usage})")
                return character
        
        # Otherwise, systematic rotation
        character = characters[self.current_character_index % len(characters)]
        self.current_character_index += 1
        logging.debug(f"Selected character by rotation: {character}")
        return character
        
    def get_next_setting(self, settings: List[str]) -> str:
        """
        Get next setting using systematic rotation with balance checking
        """
        if not settings:
            raise ValueError("Settings list is empty")
            
        # If we haven't used all settings equally, pick the least used,
        # including settings that have not appeared in usage state yet.
        if self.setting_usage:
            usage_counts = {setting: self.setting_usage.get(setting, 0) for setting in settings}
            min_usage = min(usage_counts.values())
            least_used = [setting for setting, count in usage_counts.items() if count == min_usage]
            if least_used:
                setting = random.choice(least_used)
                logging.debug(f"Selected least used setting: {setting} (usage: {min_usage})")
                return setting
        
        # Otherwise, systematic rotation
        setting = settings[self.current_setting_index % len(settings)]
        self.current_setting_index += 1
        logging.debug(f"Selected setting by rotation: {setting}")
        return setting
        
    def get_balanced_tags(self, all_tags: List[str], min_count: int = 3, max_count: int = 5) -> List[str]:
        """
        Select tags ensuring variety across categories and avoiding recent combinations
        """
        if not all_tags:
            raise ValueError("Tags list is empty")
            
        target_count = random.randint(min_count, max_count)
        selected = []
        categories_used = set()
        
        # Get tag usage counts
        tag_usage = defaultdict(int)
        for combo_str in self.tag_combinations:
            for tag in combo_str.split(","):
                tag_usage[tag.strip()] += 1
                
        # Sort tags by usage (least used first) and shuffle within usage groups
        available_tags = sorted(all_tags, key=lambda t: (tag_usage.get(t, 0), random.random()))
        
        # First pass: select one tag from each category, prioritizing unused categories
        for tag in available_tags:
            if len(selected) >= target_count:
                break
                
            category = self.tag_to_category.get(tag, "general")
            
            # Prefer unused categories, but don't be too strict
            if category not in categories_used or len(categories_used) < 3:
                selected.append(tag)
                categories_used.add(category)
                logging.debug(f"Selected tag: {tag} (category: {category})")
                
        # Second pass: fill remaining slots with best available tags
        while len(selected) < target_count and len(selected) < len(available_tags):
            for tag in available_tags:
                if tag not in selected:
                    selected.append(tag)
                    logging.debug(f"Added additional tag: {tag}")
                    break
                    
        # Ensure we don't repeat recent combinations
        combo_str = ",".join(sorted(selected))
        if combo_str in self.recent_tag_combinations[-20:]:  # Check last 20 combinations
            # Try to swap one tag
            for i, tag in enumerate(selected):
                for replacement in available_tags:
                    if replacement not in selected:
                        test_combo = selected.copy()
                        test_combo[i] = replacement
                        test_combo_str = ",".join(sorted(test_combo))
                        if test_combo_str not in self.recent_tag_combinations[-20:]:
                            selected = test_combo
                            logging.debug(f"Swapped {tag} for {replacement} to avoid repetition")
                            break
                        
        return selected
        
    def get_story_type(self) -> str:
        """
        Alternate between story types for perfect balance
        """
        if self.story_type_count["problem_solution"] <= self.story_type_count["daily_adventure"]:
            return "problem_solution"
        else:
            return "daily_adventure"
            
    def record_usage(self, character: str, setting: str, tags: List[str], story_type: str):
        """
        Record usage for tracking and update counters
        """
        self.character_usage[character] += 1
        self.setting_usage[setting] += 1
        self.story_type_count[story_type] += 1
        
        # Record tag combination
        tag_combo = ",".join(sorted(tags))
        self.tag_combinations[tag_combo] += 1
        self.recent_tag_combinations.append(tag_combo)
        
        # Keep only recent combinations for efficiency
        if len(self.recent_tag_combinations) > 100:
            self.recent_tag_combinations = self.recent_tag_combinations[-50:]
            
        logging.info(f"Recorded usage - Character: {character} ({self.character_usage[character]}), "
                    f"Setting: {setting} ({self.setting_usage[setting]}), "
                    f"Story type: {story_type} ({self.story_type_count[story_type]})")
        
    def get_usage_stats(self) -> Dict:
        """
        Get current usage statistics for monitoring
        """
        char_usage_values = list(self.character_usage.values()) if self.character_usage else [0]
        setting_usage_values = list(self.setting_usage.values()) if self.setting_usage else [0]
        
        return {
            "character_usage": {
                "min": min(char_usage_values),
                "max": max(char_usage_values),
                "avg": sum(char_usage_values) / len(char_usage_values)
            },
            "setting_usage": {
                "min": min(setting_usage_values),
                "max": max(setting_usage_values),
                "avg": sum(setting_usage_values) / len(setting_usage_values)
            },
            "story_types": dict(self.story_type_count),
            "total_stories": sum(self.story_type_count.values()),
            "unique_tag_combinations": len(self.tag_combinations)
        }
        
    def save_state(self, filepath: str):
        """
        Save current state to file for persistence
        """
        state = {
            "character_usage": dict(self.character_usage),
            "setting_usage": dict(self.setting_usage),
            "tag_combinations": dict(self.tag_combinations),
            "story_type_count": self.story_type_count,
            "current_character_index": self.current_character_index,
            "current_setting_index": self.current_setting_index,
            "recent_tag_combinations": self.recent_tag_combinations
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
            
    def load_state(self, filepath: str):
        """
        Load state from file
        """
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
                
            self.character_usage = defaultdict(int, state.get("character_usage", {}))
            self.setting_usage = defaultdict(int, state.get("setting_usage", {}))
            self.tag_combinations = defaultdict(int, state.get("tag_combinations", {}))
            self.story_type_count = state.get("story_type_count", {"problem_solution": 0, "daily_adventure": 0})
            self.current_character_index = state.get("current_character_index", 0)
            self.current_setting_index = state.get("current_setting_index", 0)
            self.recent_tag_combinations = state.get("recent_tag_combinations", [])
            
            logging.info(f"Loaded diversity tracker state from {filepath}")
            
        except FileNotFoundError:
            logging.info(f"No existing state file found at {filepath}, starting fresh")
        except Exception as e:
            logging.error(f"Error loading state from {filepath}: {e}")
