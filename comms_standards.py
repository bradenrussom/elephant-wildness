"""
Communications Standards Module
Applies MVP Communications Standards automated rules
"""

import re
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.document_processor import DocumentProcessor
from core.utils import (
    load_config, get_module_config, format_time, format_time_range,
    spell_out_number, add_commas_to_number, clean_double_spaces,
    create_correction_log_entry
)


class CommunicationsStandardsProcessor:
    """Applies MVP Communications Standards"""
    
    def __init__(self, doc_processor: DocumentProcessor, config: dict = None):
        """
        Initialize the processor
        
        Args:
            doc_processor: DocumentProcessor instance with loaded document
            config: Optional config dict (will load if None)
        """
        self.doc_processor = doc_processor
        self.config = config or load_config()
        self.module_config = get_module_config('communications_standards', self.config)
        self.corrections = []
    
    def process(self) -> int:
        """
        Apply all communications standards corrections
        
        Returns:
            Number of corrections made
        """
        paragraphs = self.doc_processor.get_page_copy_paragraphs()
        
        for para in paragraphs:
            if not para.text.strip():
                continue
            
            original_text = para.text
            
            # Protect URLs, brackets, angles
            protected_text, placeholders = DocumentProcessor.protect_content(original_text)
            
            # Apply all corrections
            corrected_text = protected_text
            corrected_text = self._fix_state_abbreviations(corrected_text)
            corrected_text = self._fix_ampersands(corrected_text)
            corrected_text = self._fix_double_spaces(corrected_text)
            corrected_text = self._fix_digital_terms(corrected_text)
            corrected_text = self._fix_times(corrected_text)
            corrected_text = self._fix_numbers(corrected_text)
            corrected_text = self._fix_healthcare_terms(corrected_text)
            corrected_text = self._fix_branding(corrected_text)
            
            # Restore protected content
            corrected_text = DocumentProcessor.restore_content(corrected_text, placeholders)
            
            # Apply if changed
            if corrected_text != original_text:
                self.doc_processor.apply_text_to_paragraph(para, corrected_text)
        
        return len(self.corrections)
    
    def _fix_state_abbreviations(self, text: str) -> str:
        """Fix state abbreviations: N.Y. -> NY, etc."""
        if not self.module_config.get('state_abbreviations', {}).get('enabled'):
            return text
        
        replacements = self.module_config['state_abbreviations'].get('replacements', [])
        
        for item in replacements:
            pattern = item['pattern']
            correct = item['correct']
            
            if re.search(pattern, text):
                text = re.sub(pattern, correct, text)
                self.corrections.append(create_correction_log_entry(
                    'State Abbreviation', pattern, correct
                ))
        
        return text
    
    def _fix_ampersands(self, text: str) -> str:
        """Replace & with 'and' except in exceptions"""
        config = self.module_config.get('punctuation', {}).get('no_ampersands', {})
        if not config.get('enabled'):
            return text
        
        exceptions = config.get('exceptions', [])
        
        # Find all ampersands
        matches = list(re.finditer(r'&', text))
        
        for match in reversed(matches):  # Process backwards to maintain positions
            pos = match.start()
            
            # Check if in exception context
            in_exception = False
            for exception in exceptions:
                if exception in text[max(0, pos-10):pos+10]:
                    in_exception = True
                    break
            
            if not in_exception:
                text = text[:pos] + config['replace_with'] + text[pos+1:]
                self.corrections.append(create_correction_log_entry(
                    'Ampersand', '&', 'and'
                ))
        
        return text
    
    def _fix_double_spaces(self, text: str) -> str:
        """Remove double spaces"""
        if not self.module_config.get('punctuation', {}).get('single_spaces', {}).get('enabled'):
            return text
        
        if '  ' in text:
            new_text = clean_double_spaces(text)
            if new_text != text:
                self.corrections.append(create_correction_log_entry(
                    'Double Spaces', 'multiple spaces', 'single space'
                ))
            return new_text
        
        return text
    
    def _fix_digital_terms(self, text: str) -> str:
        """Fix digital terminology: healthcare -> health care, etc."""
        if not self.module_config.get('digital_terms', {}).get('enabled'):
            return text
        
        replacements = self.module_config['digital_terms'].get('replacements', [])
        
        for item in replacements:
            wrong = item['wrong']
            correct = item['correct']
            
            # Case-insensitive search but preserve original case pattern
            pattern = re.compile(r'\b' + re.escape(wrong) + r'\b', re.IGNORECASE)
            
            matches = list(pattern.finditer(text))
            for match in reversed(matches):
                original = match.group(0)
                
                # Preserve capitalization pattern
                if original[0].isupper():
                    replacement = correct.capitalize()
                else:
                    replacement = correct
                
                text = text[:match.start()] + replacement + text[match.end():]
                self.corrections.append(create_correction_log_entry(
                    'Digital Terminology', original, replacement
                ))
        
        return text
    
    def _fix_times(self, text: str) -> str:
        """Fix time formatting: 3:00 PM -> 3 pm, 8 AM - 5 PM -> 8 am–5 pm"""
        if not self.module_config.get('times', {}).get('enabled'):
            return text
        
        # Pattern for time ranges: "8:00 AM - 5:00 PM" or "8 am to 5 pm"
        range_pattern = r'\b(\d{1,2}):?(\d{2})?\s*(A\.?M\.?|P\.?M\.?)\s*[-–—]\s*(\d{1,2}):?(\d{2})?\s*(A\.?M\.?|P\.?M\.?)\b'
        
        matches = list(re.finditer(range_pattern, text, re.IGNORECASE))
        for match in reversed(matches):
            original = match.group(0)
            formatted = format_time_range(original)
            
            if formatted != original:
                text = text[:match.start()] + formatted + text[match.end():]
                self.corrections.append(create_correction_log_entry(
                    'Time Range', original, formatted
                ))
        
        # Pattern for single times: "3:00 PM"
        time_pattern = r'\b(\d{1,2}):?(\d{2})?\s*(A\.?M\.?|P\.?M\.?)\b'
        
        matches = list(re.finditer(time_pattern, text, re.IGNORECASE))
        for match in reversed(matches):
            original = match.group(0)
            formatted = format_time(original)
            
            if formatted != original:
                text = text[:match.start()] + formatted + text[match.end():]
                self.corrections.append(create_correction_log_entry(
                    'Time Format', original, formatted
                ))
        
        return text
    
    def _fix_numbers(self, text: str) -> str:
        """Spell out 1-9, add commas to 1,000+"""
        if not self.module_config.get('numbers', {}).get('enabled'):
            return text
        
        spell_config = self.module_config['numbers'].get('spell_out', {})
        comma_config = self.module_config['numbers'].get('add_commas', {})
        
        # Find all standalone numbers
        number_pattern = r'\b(\d+)\b'
        matches = list(re.finditer(number_pattern, text))
        
        for match in reversed(matches):
            num_str = match.group(1)
            try:
                num = int(num_str)
            except ValueError:
                continue
            
            # Check context for exclusions
            start = max(0, match.start() - 10)
            end = min(len(text), match.end() + 10)
            context = text[start:end].lower()
            
            # Skip if in exclusion context
            if any(excl in ['percentages', 'currency', 'years', 'phone_numbers'] 
                   for excl in spell_config.get('exclusions', [])):
                # Check for % sign, $, year-like, or phone-like
                if '%' in context or '$' in context:
                    continue
                if num > 1900 and num < 2100:  # Year
                    continue
                if len(num_str) >= 7:  # Phone number-like
                    continue
            
            # Spell out 1-9
            if 1 <= num <= 9:
                spelled = spell_out_number(num)
                text = text[:match.start()] + spelled + text[match.end():]
                self.corrections.append(create_correction_log_entry(
                    'Number Spelling', num_str, spelled
                ))
            
            # Add commas to 1,000+
            elif num >= comma_config.get('threshold', 1000):
                formatted = add_commas_to_number(num_str)
                if formatted != num_str:
                    text = text[:match.start()] + formatted + text[match.end():]
                    self.corrections.append(create_correction_log_entry(
                        'Number Commas', num_str, formatted
                    ))
        
        return text
    
    def _fix_healthcare_terms(self, text: str) -> str:
        """Fix healthcare terminology"""
        if not self.module_config.get('healthcare_terms', {}).get('enabled'):
            return text
        
        replacements = self.module_config['healthcare_terms'].get('replacements', [])
        
        for item in replacements:
            wrong = item['wrong']
            correct = item['correct']
            
            pattern = re.compile(r'\b' + re.escape(wrong) + r'\b', re.IGNORECASE)
            matches = list(pattern.finditer(text))
            
            for match in reversed(matches):
                original = match.group(0)
                
                # Preserve capitalization
                if original[0].isupper():
                    replacement = correct.capitalize()
                else:
                    replacement = correct
                
                text = text[:match.start()] + replacement + text[match.end():]
                self.corrections.append(create_correction_log_entry(
                    'Healthcare Terminology', original, replacement
                ))
        
        return text
    
    def _fix_branding(self, text: str) -> str:
        """Fix MVP branding terms"""
        if not self.module_config.get('branding', {}).get('enabled'):
            return text
        
        # MVP terminology
        mvp_terms = self.module_config['branding'].get('mvp_terminology', [])
        for item in mvp_terms:
            pattern = item['pattern']
            correct = item['correct']
            
            if pattern in text:
                text = text.replace(pattern, correct)
                self.corrections.append(create_correction_log_entry(
                    'MVP Branding', pattern, correct
                ))
        
        # Gia® - Add ® to first instance only
        gia_config = self.module_config['branding'].get('gia_platform', {})
        if gia_config.get('enabled'):
            # Only add ® if it's the first instance of "Gia" without ®
            if 'Gia' in text and 'Gia®' not in text:
                text = text.replace('Gia', 'Gia®', 1)
                self.corrections.append(create_correction_log_entry(
                    'Trademark Symbol', 'Gia', 'Gia®'
                ))
        
        return text
    
    def get_corrections_summary(self) -> dict:
        """Get summary of corrections by category"""
        summary = {}
        for correction in self.corrections:
            rule = correction['rule']
            if rule not in summary:
                summary[rule] = 0
            summary[rule] += 1
        return summary


# Example usage
if __name__ == '__main__':
    from core.document_processor import DocumentProcessor
    
    # Load document
    doc_proc = DocumentProcessor('test.docx')
    
    # Apply communications standards
    comms_proc = CommunicationsStandardsProcessor(doc_proc)
    count = comms_proc.process()
    
    print(f"Applied {count} corrections")
    print("\nCorrections by category:")
    for rule, count in comms_proc.get_corrections_summary().items():
        print(f"  {rule}: {count}")
    
    # Save
    doc_proc.save('test_corrected.docx')
