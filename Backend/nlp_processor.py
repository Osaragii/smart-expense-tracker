import re
from datetime import date, datetime, timedelta
from typing import Optional, Dict, List
from models import ExtractedExpenseData

class ExpenseNLPProcessor:
    def __init__(self):
        # Category keywords mapping
        self.category_keywords = {
            'food': ['food', 'lunch', 'dinner', 'breakfast', 'restaurant', 'pizza', 'burger', 'coffee', 'tea', 'snack', 'meal', 'eat', 'hungry', 'cafe', 'mcdonalds', 'kfc', 'subway', 'starbucks', 'dominos'],
            'transport': ['gas', 'fuel', 'uber', 'taxi', 'bus', 'train', 'metro', 'parking', 'toll', 'car', 'bike', 'flight', 'airline', 'travel', 'trip'],
            'shopping': ['shopping', 'clothes', 'shirt', 'shoes', 'dress', 'jacket', 'pants', 'buy', 'bought', 'purchase', 'store', 'mall', 'amazon', 'flipkart'],
            'entertainment': ['movie', 'cinema', 'game', 'music', 'concert', 'party', 'fun', 'entertainment', 'netflix', 'spotify', 'youtube'],
            'health': ['doctor', 'medicine', 'pharmacy', 'hospital', 'health', 'medical', 'dental', 'clinic', 'pills', 'treatment'],
            'utilities': ['electricity', 'water', 'internet', 'phone', 'mobile', 'wifi', 'cable', 'utility', 'bill', 'rent'],
            'groceries': ['grocery', 'groceries', 'vegetables', 'fruits', 'milk', 'bread', 'eggs', 'supermarket', 'walmart', 'target'],
            'education': ['book', 'course', 'class', 'school', 'college', 'university', 'education', 'study', 'learn'],
            'miscellaneous': ['other', 'misc', 'random', 'stuff', 'things', 'general']
        }
        
        # Date keywords mapping
        self.date_keywords = {
            'today': 0,
            'yesterday': -1,
            'day before yesterday': -2,
            'last monday': self._get_last_weekday(0),
            'last tuesday': self._get_last_weekday(1),
            'last wednesday': self._get_last_weekday(2),
            'last thursday': self._get_last_weekday(3),
            'last friday': self._get_last_weekday(4),
            'last saturday': self._get_last_weekday(5),
            'last sunday': self._get_last_weekday(6),
        }

    def _get_last_weekday(self, weekday: int) -> int:
        """Get days ago for last occurrence of weekday (0=Monday, 6=Sunday)"""
        today = datetime.now()
        days_ahead = weekday - today.weekday()
        if days_ahead > 0:  # Target day hasn't happened this week
            days_ahead -= 7
        return days_ahead

    def extract_amount(self, text: str) -> Optional[float]:
        """Extract monetary amount from text"""
        # Patterns for different amount formats
        patterns = [
            r'[\$₹£€]\s*(\d+(?:\.\d{2})?)',  # $50, ₹100, £30.50
            r'(\d+(?:\.\d{2})?)\s*(?:dollars?|bucks?|rupees?|pounds?|euros?)',  # 50 dollars, 30 bucks
            r'(\d+(?:\.\d{2})?)\s*(?:rs\.?|inr|usd|\$)',  # 50 rs, 100 INR
            r'(?:spent|paid|cost|price|amount)\s*[\$₹£€]?\s*(\d+(?:\.\d{2})?)',  # spent $50
            r'(\d+(?:\.\d{2})?)\s*(?:only|just)',  # 50 only
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, IndexError):
                    continue
        
        return None

    def extract_category(self, text: str) -> Optional[str]:
        """Extract category from text based on keywords"""
        text_lower = text.lower()
        
        # Count matches for each category
        category_scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return 'miscellaneous'

    def extract_date(self, text: str) -> Optional[date]:
        """Extract date from text"""
        text_lower = text.lower()
        today = date.today()
        
        # Check for relative date keywords
        for keyword, days_offset in self.date_keywords.items():
            if keyword in text_lower:
                if callable(days_offset):
                    days_offset = days_offset()
                return today + timedelta(days=days_offset)
        
        # Check for "X days ago" pattern
        days_ago_match = re.search(r'(\d+)\s*days?\s*ago', text_lower)
        if days_ago_match:
            days_ago = int(days_ago_match.group(1))
            return today - timedelta(days=days_ago)
        
        # Check for "last week", "this week" patterns
        if 'last week' in text_lower:
            return today - timedelta(days=7)
        elif 'this week' in text_lower or 'earlier this week' in text_lower:
            return today - timedelta(days=2)  # Assume 2 days ago
        
        # Default to today if no date found
        return today

    def extract_description(self, text: str, amount: Optional[float], category: Optional[str]) -> str:
        """Extract and clean description from text"""
        # Remove amount patterns
        cleaned_text = re.sub(r'[\$₹£€]\s*\d+(?:\.\d{2})?', '', text)
        cleaned_text = re.sub(r'\d+(?:\.\d{2})?\s*(?:dollars?|bucks?|rupees?|pounds?|euros?|rs\.?|inr|usd)', '', cleaned_text)
        
        # Remove common expense-related words
        remove_words = ['spent', 'paid', 'cost', 'bought', 'purchase', 'for', 'on', 'at', 'in', 'the', 'a', 'an', 'today', 'yesterday', 'last', 'ago', 'days?', 'only', 'just']
        pattern = r'\b(?:' + '|'.join(remove_words) + r')\b'
        cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
        
        # Remove extra whitespace and clean up
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        # If description is too short or empty, use category as fallback
        if len(cleaned_text) < 3 and category:
            return f"{category} expense"
        
        return cleaned_text if cleaned_text else "General expense"

    def calculate_confidence(self, extracted_data: ExtractedExpenseData) -> float:
        """Calculate confidence score for extraction"""
        confidence = 0.0
        
        # Amount confidence (40% weight)
        if extracted_data.amount is not None:
            confidence += 0.4
        
        # Category confidence (30% weight)
        if extracted_data.category and extracted_data.category != 'miscellaneous':
            confidence += 0.3
        elif extracted_data.category == 'miscellaneous':
            confidence += 0.1
        
        # Description confidence (20% weight)
        if extracted_data.description and len(extracted_data.description) > 5:
            confidence += 0.2
        elif extracted_data.description:
            confidence += 0.1
        
        # Date confidence (10% weight)
        if extracted_data.date:
            confidence += 0.1
        
        return min(confidence, 1.0)

    def process_expense_text(self, text: str) -> ExtractedExpenseData:
        """Main method to process natural language expense text"""
        # Extract individual components
        amount = self.extract_amount(text)
        category = self.extract_category(text)
        date_extracted = self.extract_date(text)
        description = self.extract_description(text, amount, category)
        
        # Create extracted data object
        extracted_data = ExtractedExpenseData(
            amount=amount,
            category=category,
            description=description,
            date=date_extracted,
            raw_text=text,
            confidence=0.0  # Will be calculated next
        )
        
        # Calculate confidence
        extracted_data.confidence = self.calculate_confidence(extracted_data)
        
        return extracted_data

# Create global instance
nlp_processor = ExpenseNLPProcessor()