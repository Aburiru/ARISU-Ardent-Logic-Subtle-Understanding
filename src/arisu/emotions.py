# emotion_detector.py

import re
from datetime import datetime
from collections import Counter

class EmotionDetector:
    def __init__(self):
        """
        Initialize the emotion detection system
        Tracks user's emotional state over conversation
        """
        # Emotion keywords (expanded lists)
        self.emotions = {
            'happy': [
                'happy', 'great', 'awesome', 'love', 'excited', 'glad', 
                'wonderful', 'amazing', 'fantastic', 'yay', 'haha', 'lol',
                'nice', 'good', 'perfect', 'excellent', 'cool', 'thanks'
            ],
            'sad': [
                'sad', 'unhappy', 'depressed', 'down', 'miserable', 'cry',
                'crying', 'upset', 'hurt', 'lonely', 'alone', 'miss',
                'sigh', 'ugh', 'terrible', 'awful', 'horrible', 'bad'
            ],
            'angry': [
                'angry', 'mad', 'furious', 'pissed', 'annoyed', 'irritated',
                'frustrated', 'hate', 'stupid', 'damn', 'wtf', 'annoying',
                'rage', 'livid', 'infuriating'
            ],
            'anxious': [
                'worried', 'anxious', 'nervous', 'scared', 'afraid', 'fear',
                'stress', 'stressed', 'panic', 'overwhelmed', 'confused',
                'uncertain', 'doubt', 'dunno', 'idk', 'help', 'lost'
            ],
            'tired': [
                'tired', 'exhausted', 'sleepy', 'fatigue', 'worn', 'drained',
                'weary', 'beat', 'burned out', 'cant sleep', "can't sleep",
                'insomnia', 'staying up', 'late night', 'no sleep'
            ],
            'excited': [
                'excited', 'pumped', 'hyped', 'cant wait', "can't wait",
                'omg', 'wow', 'amazing', 'incredible', 'awesome', 'yes',
                'finally', 'lets go', "let's go", 'woohoo'
            ],
            'stressed': [
                'deadline', 'urgent', 'asap', 'hurry', 'quick', 'too much',
                'cannot cope', 'pressure', 'workload'
            ]
        }
        
        # Emotion history (last 10 messages)
        self.emotion_history = []
        
        # Conversation start time
        self.conversation_start = datetime.now()
        
        # Message count
        self.message_count = 0
    
    def detect_emotion(self, message):
        """
        Analyze a message and return detected emotion
        
        message = user's text
        Returns: (primary_emotion, intensity, indicators)
        """
        message_lower = message.lower()
        self.message_count += 1
        
        # Dictionary to count emotion indicators
        emotion_scores = {emotion: 0.0 for emotion in self.emotions}
        indicators = []
        
        # 1. CHECK KEYWORDS
        for emotion, keywords in self.emotions.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', message_lower):
                    emotion_scores[emotion] += 1
                    indicators.append(f"keyword: '{keyword}'")
        
        # 2. CHECK PUNCTUATION
        exclamation_count = message.count('!')
        question_count = message.count('?')
        ellipsis_count = message.count('...')
        
        if exclamation_count >= 2:
            emotion_scores['excited'] += 1.5
            emotion_scores['angry'] += 0.5
            indicators.append(f"excited punctuation (!!)")
        
        if question_count >= 3:
            emotion_scores['anxious'] += 1.0
            indicators.append("multiple questions (???)")
        
        if ellipsis_count >= 2:
            emotion_scores['sad'] += 1.0
            emotion_scores['tired'] += 0.5
            indicators.append("trailing off (...)")
        
        # 3. CHECK CAPS (shouting)
        if len(message) > 5:
            caps_count = sum(1 for c in message if c.isupper())
            caps_ratio = caps_count / len(message)
            
            if caps_ratio > 0.5:
                emotion_scores['angry'] += 2.0
                emotion_scores['excited'] += 1.5
                indicators.append("CAPS (shouting/excited)")
        
        # 4. CHECK MESSAGE LENGTH
        words = message.split()
        word_count = len(words)
        
        if word_count > 0 and word_count <= 3:
            emotion_scores['tired'] += 0.5
            emotion_scores['sad'] += 0.3
            indicators.append("very short message")
        
        elif word_count >= 50:
            emotion_scores['excited'] += 1.0
            emotion_scores['anxious'] += 0.5
            indicators.append("very long message")
        
        # 5. CHECK SPECIAL PATTERNS
        # Negative patterns
        if re.search(r"(can't|cannot|won't|don't know|give up)", message_lower):
            emotion_scores['anxious'] += 1.0
            emotion_scores['sad'] += 0.5
            indicators.append("negative/uncertain language")
        
        # Positive patterns
        if re.search(r"(thank|appreciate|grateful|love it)", message_lower):
            emotion_scores['happy'] += 1.5
            indicators.append("gratitude expression")
        
        # Find primary emotion
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        intensity = emotion_scores[primary_emotion]
        
        # If no clear emotion detected
        if intensity == 0:
            primary_emotion = 'neutral'
            intensity = 0
        
        # Store in history
        emotion_data = {
            'emotion': primary_emotion,
            'intensity': intensity,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        
        self.emotion_history.append(emotion_data)
        
        # Keep only last 10
        if len(self.emotion_history) > 10:
            self.emotion_history.pop(0)
        
        return primary_emotion, intensity, indicators
    
    def get_emotion_trend(self):
        """
        Analyze emotion trend over recent messages
        Returns: overall mood description
        """
        if not self.emotion_history:
            return "neutral"
        
        # Count emotions in history
        recent_emotions = [e['emotion'] for e in self.emotion_history if e['emotion'] != 'neutral']
        
        if not recent_emotions:
            return "neutral"
        
        # Check if consistently one emotion
        if len(set(recent_emotions)) == 1 and len(recent_emotions) >= 3:
            return f"consistently {recent_emotions[0]}"
        
        # Most common emotion
        counts = Counter(recent_emotions)
        most_common = counts.most_common(1)[0][0]
        return f"mostly {most_common}"
    
    def get_conversation_duration(self):
        """
        Returns how long the conversation has been going
        Returns: (duration_seconds, formatted_string)
        """
        duration = datetime.now() - self.conversation_start
        total_seconds = int(duration.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            formatted = f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            formatted = f"{minutes}m {seconds}s"
        else:
            formatted = f"{seconds}s"
        
        return total_seconds, formatted
    
    def get_stats(self):
        """
        Get full conversation statistics
        Returns: dictionary with all stats
        """
        duration_sec, duration_str = self.get_conversation_duration()
        
        stats = {
            'message_count': self.message_count,
            'duration': duration_str,
            'duration_seconds': duration_sec,
            'emotion_trend': self.get_emotion_trend(),
            'recent_emotions': [e['emotion'] for e in self.emotion_history]
        }
        
        return stats
