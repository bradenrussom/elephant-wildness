"""
Text Analyzer - Core module for analyzing text metrics
Adapted from existing working MVP Standards Checker app
"""

import textstat
import re
from typing import List, Dict, Tuple


class TextAnalyzer:
    """Analyzes text for readability, word count, and other metrics"""
    
    def __init__(self, text: str):
        """
        Initialize the analyzer with text
        
        Args:
            text: The text to analyze
        """
        self.text = text
        self._words = None
        self._sentences = None
    
    @property
    def words(self) -> List[str]:
        """Get list of words (cached)"""
        if self._words is None:
            self._words = self.text.split()
        return self._words
    
    @property
    def sentences(self) -> List[str]:
        """Get list of sentences (cached)"""
        if self._sentences is None:
            self._sentences = [s.strip() for s in re.split(r'[.!?]+', self.text) if s.strip()]
        return self._sentences
    
    def word_count(self) -> int:
        """Count total words"""
        return len(self.words)
    
    def sentence_count(self) -> int:
        """Count total sentences"""
        return len(self.sentences)
    
    def paragraph_count(self, text_with_newlines: str = None) -> int:
        """
        Count paragraphs (non-empty blocks separated by newlines)
        
        Args:
            text_with_newlines: Optional text to analyze. Uses self.text if None.
        """
        text = text_with_newlines or self.text
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        return len(paragraphs)
    
    def reading_level(self) -> float:
        """
        Calculate Flesch-Kincaid Grade Level
        
        Returns:
            Grade level (e.g., 8.5 = 8th grade, 5 months)
        """
        return textstat.flesch_kincaid_grade(self.text)
    
    def flesch_reading_ease(self) -> float:
        """
        Calculate Flesch Reading Ease score (0-100)
        Higher = easier to read
        
        Returns:
            Score from 0-100
        """
        return textstat.flesch_reading_ease(self.text)
    
    def average_sentence_length(self) -> float:
        """Calculate average words per sentence"""
        if self.sentence_count() == 0:
            return 0
        return self.word_count() / self.sentence_count()
    
    def average_word_length(self) -> float:
        """Calculate average characters per word"""
        if not self.words:
            return 0
        total_chars = sum(len(word) for word in self.words)
        return total_chars / len(self.words)
    
    def keyword_frequency(self, keywords: List[str]) -> Dict[str, Dict]:
        """
        Analyze keyword frequency and density
        
        Args:
            keywords: List of keyword phrases to search for
        
        Returns:
            Dictionary with keyword stats:
            {
                'keyword': {
                    'count': int,
                    'density': float (percentage)
                }
            }
        """
        text_lower = self.text.lower()
        total_words = self.word_count()
        
        results = {}
        for keyword in keywords:
            if not keyword.strip():
                continue
            
            keyword_lower = keyword.lower()
            
            # Count occurrences (case-insensitive, whole phrase)
            count = len(re.findall(r'\b' + re.escape(keyword_lower) + r'\b', text_lower))
            
            # Calculate density (keyword words / total words * 100)
            keyword_word_count = len(keyword.split())
            if total_words > 0:
                density = (count * keyword_word_count / total_words) * 100
            else:
                density = 0
            
            results[keyword] = {
                'count': count,
                'density': round(density, 2)
            }
        
        return results
    
    def find_keyword_in_bold(self, doc_paragraphs, keywords: List[str]) -> Dict[str, int]:
        """
        Find how many times each keyword appears in bold text
        
        Args:
            doc_paragraphs: List of docx paragraph objects
            keywords: List of keywords to search for
        
        Returns:
            Dictionary mapping keywords to bold occurrence count
        """
        bold_counts = {kw: 0 for kw in keywords}
        
        for para in doc_paragraphs:
            for run in para.runs:
                if run.bold:
                    text_lower = run.text.lower()
                    for keyword in keywords:
                        if keyword.lower() in text_lower:
                            bold_counts[keyword] += 1
        
        return bold_counts
    
    def find_keyword_in_headings(self, doc_paragraphs, keywords: List[str]) -> Dict[str, int]:
        """
        Find how many times each keyword appears in heading styles
        
        Args:
            doc_paragraphs: List of docx paragraph objects
            keywords: List of keywords to search for
        
        Returns:
            Dictionary mapping keywords to heading occurrence count
        """
        heading_counts = {kw: 0 for kw in keywords}
        heading_styles = ['Heading 1', 'Heading 2', 'Heading 3', 'Heading 4', 'Heading 5']
        
        for para in doc_paragraphs:
            if para.style.name in heading_styles:
                text_lower = para.text.lower()
                for keyword in keywords:
                    if keyword.lower() in text_lower:
                        heading_counts[keyword] += 1
        
        return heading_counts
    
    def analyze_links(self, doc_paragraphs) -> Dict[str, any]:
        """
        Analyze links in the document
        
        Args:
            doc_paragraphs: List of docx paragraph objects
        
        Returns:
            Dictionary with link statistics
        """
        total_links = 0
        anchor_texts = []
        link_styles = []
        
        for para in doc_paragraphs:
            # Check paragraph style
            if 'link' in para.style.name.lower():
                total_links += 1
                link_styles.append(para.style.name)
                anchor_texts.append(para.text.strip())
            
            # Check for hyperlinks in runs
            for run in para.runs:
                if run.hyperlink:
                    total_links += 1
                    anchor_texts.append(run.text.strip())
        
        return {
            'total_links': total_links,
            'anchor_texts': anchor_texts,
            'link_styles': link_styles,
            'unique_anchor_texts': len(set(anchor_texts))
        }
    
    def compare_to_target(self, target_word_count: int = None, 
                          target_reading_level: float = None) -> Dict[str, Dict]:
        """
        Compare document metrics to targets
        
        Args:
            target_word_count: Target word count
            target_reading_level: Target reading level (grade)
        
        Returns:
            Dictionary with comparison results
        """
        actual_words = self.word_count()
        actual_reading_level = self.reading_level()
        
        results = {}
        
        if target_word_count:
            diff = actual_words - target_word_count
            status = 'on_target' if abs(diff) <= 50 else ('over' if diff > 0 else 'under')
            
            results['word_count'] = {
                'target': target_word_count,
                'actual': actual_words,
                'difference': diff,
                'status': status
            }
        
        if target_reading_level:
            diff = actual_reading_level - target_reading_level
            status = 'on_target' if abs(diff) <= 1.0 else ('above' if diff > 0 else 'below')
            
            results['reading_level'] = {
                'target': target_reading_level,
                'actual': round(actual_reading_level, 1),
                'difference': round(diff, 1),
                'status': status
            }
        
        return results
    
    def generate_summary(self, target_word_count: int = None,
                        target_reading_level: float = None,
                        keywords: List[str] = None) -> str:
        """
        Generate a text summary of the analysis
        
        Args:
            target_word_count: Optional target word count
            target_reading_level: Optional target reading level
            keywords: Optional list of keywords to analyze
        
        Returns:
            Multi-line string summary
        """
        lines = []
        lines.append("DOCUMENT ANALYSIS")
        lines.append("=" * 50)
        lines.append("")
        
        # Basic stats
        lines.append("Basic Statistics:")
        lines.append(f"  Word Count: {self.word_count()}")
        lines.append(f"  Sentence Count: {self.sentence_count()}")
        lines.append(f"  Reading Level: {self.reading_level():.1f} grade")
        lines.append(f"  Avg Sentence Length: {self.average_sentence_length():.1f} words")
        lines.append("")
        
        # Target comparison
        if target_word_count or target_reading_level:
            comparison = self.compare_to_target(target_word_count, target_reading_level)
            lines.append("Target Comparison:")
            
            if 'word_count' in comparison:
                wc = comparison['word_count']
                lines.append(f"  Word Count: {wc['actual']} (target: {wc['target']}, {wc['status']})")
            
            if 'reading_level' in comparison:
                rl = comparison['reading_level']
                lines.append(f"  Reading Level: {rl['actual']} (target: {rl['target']}, {rl['status']})")
            
            lines.append("")
        
        # Keyword analysis
        if keywords:
            kw_freq = self.keyword_frequency(keywords)
            lines.append("Keyword Analysis:")
            for keyword, stats in kw_freq.items():
                lines.append(f"  '{keyword}': {stats['count']} times ({stats['density']:.2f}% density)")
            lines.append("")
        
        return '\n'.join(lines)


# Example usage
if __name__ == '__main__':
    sample_text = """
    Health care is important. Virtual care services make it easier to access care.
    Sign in to your account to schedule appointments.
    """
    
    analyzer = TextAnalyzer(sample_text)
    
    print(f"Words: {analyzer.word_count()}")
    print(f"Sentences: {analyzer.sentence_count()}")
    print(f"Reading Level: {analyzer.reading_level():.1f}")
    
    # Keyword analysis
    keywords = ['health care', 'virtual care', 'sign in']
    kw_results = analyzer.keyword_frequency(keywords)
    for kw, stats in kw_results.items():
        print(f"{kw}: {stats['count']} times, {stats['density']:.2f}% density")
