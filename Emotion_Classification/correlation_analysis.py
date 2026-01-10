# Emotion_Classification/correlation_analysis.py


import sqlite3
import numpy as np
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import math
from typing import List, Dict, Tuple, Optional, Any
import warnings

# Conditional imports for visualization
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Visualizations disabled.")

warnings.filterwarnings('ignore')

class CorrelationAnalyzer:
    """Lightweight correlation analyzer for emotion data"""
    
    def __init__(self, db_path: str = "soul_sense.db"):
        """
        Initialize analyzer with database connection
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.emotion_labels = ["negative", "neutral", "positive"]
        
    def fetch_emotion_data(self, user_id: Optional[int] = None, 
                          days_back: int = 30) -> List[Dict]:
        """
        Fetch emotion data from database
        
        Args:
            user_id: Optional user ID to filter by
            days_back: Number of days to look back
            
        Returns:
            List of emotion records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        date_cutoff = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        if user_id:
            cursor.execute("""
                SELECT emotion, timestamp, confidence, text_sample 
                FROM emotion_records 
                WHERE user_id = ? AND date(timestamp) >= ?
                ORDER BY timestamp
            """, (user_id, date_cutoff))
        else:
            cursor.execute("""
                SELECT emotion, timestamp, confidence, text_sample 
                FROM emotion_records 
                WHERE date(timestamp) >= ?
                ORDER BY timestamp
            """, (date_cutoff,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        records = []
        for row in rows:
            records.append({
                'emotion': row[0],
                'timestamp': row[1],
                'confidence': row[2],
                'text_sample': row[3] if row[3] else ''
            })
        
        return records
    
    def calculate_basic_statistics(self, records: List[Dict]) -> Dict:
        """
        Calculate basic statistics for emotion data
        
        Args:
            records: List of emotion records
            
        Returns:
            Dictionary with statistics
        """
        if not records:
            return {}
        
        # Count emotions
        emotion_counts = Counter([r['emotion'] for r in records])
        total = len(records)
        
        # Calculate percentages
        percentages = {
            emotion: (count / total * 100) if total > 0 else 0
            for emotion, count in emotion_counts.items()
        }
        
        # Calculate average confidence
        confidences = [r['confidence'] for r in records if r['confidence'] is not None]
        avg_confidence = np.mean(confidences) if confidences else 0
        
        # Find most common emotion
        most_common = emotion_counts.most_common(1)
        most_common_emotion = most_common[0][0] if most_common else "none"
        
        return {
            'total_records': total,
            'emotion_counts': dict(emotion_counts),
            'percentages': percentages,
            'average_confidence': float(avg_confidence),
            'most_common_emotion': most_common_emotion,
            'date_range': {
                'start': records[0]['timestamp'],
                'end': records[-1]['timestamp']
            }
        }
    
    def analyze_emotion_transitions(self, records: List[Dict]) -> Dict:
        """
        Analyze transitions between consecutive emotions
        
        Args:
            records: List of emotion records in chronological order
            
        Returns:
            Transition analysis
        """
        if len(records) < 2:
            return {"message": "Insufficient data for transition analysis"}
        
        # Create transition matrix
        transitions = defaultdict(lambda: defaultdict(int))
        
        for i in range(len(records) - 1):
            current = records[i]['emotion']
            next_emotion = records[i + 1]['emotion']
            transitions[current][next_emotion] += 1
        
        # Calculate transition probabilities
        transition_probabilities = {}
        for from_emotion, to_dict in transitions.items():
            total_from = sum(to_dict.values())
            transition_probabilities[from_emotion] = {
                to_emotion: count / total_from
                for to_emotion, count in to_dict.items()
            }
        
        # Find most common transitions
        all_transitions = []
        for from_emotion, to_dict in transitions.items():
            for to_emotion, count in to_dict.items():
                prob = transition_probabilities[from_emotion][to_emotion]
                all_transitions.append({
                    'from': from_emotion,
                    'to': to_emotion,
                    'count': count,
                    'probability': prob
                })
        
        # Sort by frequency
        all_transitions.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            'transitions': dict(transitions),
            'probabilities': transition_probabilities,
            'most_common_transitions': all_transitions[:10],
            'stability_score': self._calculate_emotion_stability(transitions)
        }
    
    def _calculate_emotion_stability(self, transitions: Dict) -> float:
        """Calculate how stable emotions are (probability of staying in same emotion)"""
        total_transitions = 0
        same_emotion_transitions = 0
        
        for from_emotion, to_dict in transitions.items():
            for to_emotion, count in to_dict.items():
                total_transitions += count
                if from_emotion == to_emotion:
                    same_emotion_transitions += count
        
        return (same_emotion_transitions / total_transitions * 100) if total_transitions > 0 else 0
    
    def analyze_temporal_patterns(self, records: List[Dict]) -> Dict:
        """
        Analyze emotion patterns over time
        
        Args:
            records: List of emotion records
            
        Returns:
            Temporal pattern analysis
        """
        if not records:
            return {}
        
        # Group by hour of day
        hourly_patterns = defaultdict(lambda: defaultdict(int))
        
        for record in records:
            try:
                dt = datetime.strptime(record['timestamp'], '%Y-%m-%d %H:%M:%S')
                hour = dt.hour
                emotion = record['emotion']
                hourly_patterns[hour][emotion] += 1
            except:
                continue
        
        # Find dominant emotion for each hour
        dominant_by_hour = {}
        for hour, emotions in hourly_patterns.items():
            if emotions:
                dominant = max(emotions.items(), key=lambda x: x[1])[0]
                dominant_by_hour[hour] = {
                    'emotion': dominant,
                    'count': emotions[dominant]
                }
        
        # Calculate overall patterns
        time_of_day_stats = {
            'morning': self._analyze_time_period(records, 6, 12),
            'afternoon': self._analyze_time_period(records, 12, 18),
            'evening': self._analyze_time_period(records, 18, 22),
            'night': self._analyze_time_period(records, 22, 6)
        }
        
        return {
            'hourly_patterns': dict(hourly_patterns),
            'dominant_by_hour': dominant_by_hour,
            'time_of_day_stats': time_of_day_stats,
            'most_emotional_hour': max(hourly_patterns.items(), 
                                      key=lambda x: sum(x[1].values()))[0] if hourly_patterns else None
        }
    
    def _analyze_time_period(self, records: List[Dict], start_hour: int, end_hour: int) -> Dict:
        """Analyze emotions for a specific time period"""
        period_records = []
        
        for record in records:
            try:
                dt = datetime.strptime(record['timestamp'], '%Y-%m-%d %H:%M:%S')
                hour = dt.hour
                
                if start_hour <= end_hour:
                    if start_hour <= hour < end_hour:
                        period_records.append(record)
                else:  # Crosses midnight (e.g., 22-6)
                    if hour >= start_hour or hour < end_hour:
                        period_records.append(record)
            except:
                continue
        
        if not period_records:
            return {}
        
        emotion_counts = Counter([r['emotion'] for r in period_records])
        total = len(period_records)
        
        return {
            'total': total,
            'emotions': dict(emotion_counts),
            'dominant': max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else None
        }
    
    def calculate_correlations(self, records: List[Dict]) -> Dict:
        """
        Calculate basic correlations between emotion occurrences
        
        Args:
            records: List of emotion records
            
        Returns:
            Correlation analysis
        """
        if len(records) < 10:
            return {"message": "Insufficient data for correlation analysis"}
        
        # Create sequential data
        emotions_sequence = [r['emotion'] for r in records]
        
        # Calculate co-occurrence matrix (emotions appearing close together)
        window_size = min(5, len(records) // 2)
        co_occurrences = defaultdict(lambda: defaultdict(int))
        
        for i in range(len(emotions_sequence) - window_size):
            window = emotions_sequence[i:i + window_size]
            for j in range(len(window)):
                for k in range(j + 1, len(window)):
                    em1, em2 = window[j], window[k]
                    if em1 != em2:
                        co_occurrences[em1][em2] += 1
                        co_occurrences[em2][em1] += 1
        
        # Convert to correlation-like scores
        correlation_scores = {}
        for em1 in self.emotion_labels:
            correlation_scores[em1] = {}
            total_with_em1 = sum(co_occurrences[em1].values())
            
            for em2 in self.emotion_labels:
                if em1 != em2:
                    count = co_occurrences[em1].get(em2, 0)
                    score = count / total_with_em1 if total_with_em1 > 0 else 0
                    correlation_scores[em1][em2] = {
                        'co_occurrence_count': count,
                        'association_score': score,
                        'interpretation': self._interpret_association(score, em1, em2)
                    }
        
        # Find strongest associations
        strong_associations = []
        for em1 in correlation_scores:
            for em2, data in correlation_scores[em1].items():
                if data['association_score'] > 0.1:  # Threshold for meaningful association
                    strong_associations.append({
                        'pair': f"{em1} ↔ {em2}",
                        'score': data['association_score'],
                        'count': data['co_occurrence_count'],
                        'interpretation': data['interpretation']
                    })
        
        # Sort by strength
        strong_associations.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'correlation_matrix': correlation_scores,
            'strong_associations': strong_associations,
            'summary': self._generate_correlation_summary(strong_associations)
        }
    
    def _interpret_association(self, score: float, em1: str, em2: str) -> str:
        """Interpret association score"""
        if score < 0.05:
            return f"No meaningful association between {em1} and {em2}"
        elif score < 0.2:
            return f"Weak tendency for {em1} and {em2} to occur together"
        elif score < 0.4:
            return f"Moderate association: {em1} and {em2} often co-occur"
        else:
            return f"Strong association: {em1} and {em2} frequently appear together"
    
    def _generate_correlation_summary(self, associations: List[Dict]) -> str:
        """Generate summary text"""
        if not associations:
            return "No strong associations found between emotions."
        
        summary = f"Found {len(associations)} significant emotion association(s):\n\n"
        for assoc in associations[:3]:  # Top 3
            summary += f"• {assoc['pair']}: {assoc['interpretation']} (score: {assoc['score']:.3f})\n"
        
        return summary
    
    def generate_insights(self, records: List[Dict]) -> Dict:
        """
        Generate comprehensive insights from emotion data
        
        Args:
            records: List of emotion records
            
        Returns:
            Dictionary with insights
        """
        stats = self.calculate_basic_statistics(records)
        transitions = self.analyze_emotion_transitions(records)
        temporal = self.analyze_temporal_patterns(records)
        correlations = self.calculate_correlations(records)
        
        # Generate actionable insights
        insights = []
        
        # Insight 1: Emotion distribution
        if stats.get('percentages'):
            dominant_emotion = max(stats['percentages'].items(), key=lambda x: x[1])
            insights.append({
                'type': 'distribution',
                'title': 'Primary Emotional State',
                'content': f"Your predominant emotion is {dominant_emotion[0]} ({dominant_emotion[1]:.1f}% of the time)",
                'suggestion': self._get_suggestion_for_emotion(dominant_emotion[0])
            })
        
        # Insight 2: Emotion stability
        if transitions.get('stability_score'):
            stability = transitions['stability_score']
            if stability > 70:
                insights.append({
                    'type': 'stability',
                    'title': 'High Emotional Consistency',
                    'content': f"You show {stability:.1f}% consistency in maintaining the same emotion",
                    'suggestion': "This indicates emotional stability and predictability in your responses."
                })
            elif stability < 30:
                insights.append({
                    'type': 'stability',
                    'title': 'Frequent Emotional Shifts',
                    'content': f"Only {stability:.1f}% of emotions persist between entries",
                    'suggestion': "You may be experiencing varied emotional states or responding to changing circumstances."
                })
        
        # Insight 3: Temporal patterns
        if temporal.get('time_of_day_stats'):
            best_time = max(temporal['time_of_day_stats'].items(), 
                          key=lambda x: x[1].get('total', 0))
            if best_time[1].get('dominant'):
                insights.append({
                    'type': 'temporal',
                    'title': f'Time-Based Pattern',
                    'content': f"During {best_time[0]}, you're most frequently {best_time[1]['dominant']}",
                    'suggestion': f"Consider what activities or factors during {best_time[0]} contribute to this emotional state."
                })
        
        # Insight 4: Strong associations
        if correlations.get('strong_associations'):
            strongest = correlations['strong_associations'][0] if correlations['strong_associations'] else None
            if strongest and strongest['score'] > 0.3:
                insights.append({
                    'type': 'association',
                    'title': 'Emotion Pairing Pattern',
                    'content': strongest['interpretation'],
                    'suggestion': "This pattern suggests these emotional states may be linked in your experiences."
                })
        
        return {
            'statistics': stats,
            'transitions': transitions,
            'temporal_patterns': temporal,
            'correlations': correlations,
            'insights': insights,
            'summary': self._generate_overall_summary(stats, insights)
        }
    
    def _get_suggestion_for_emotion(self, emotion: str) -> str:
        """Get suggestion based on dominant emotion"""
        suggestions = {
            'positive': "Continue engaging in activities that bring you positivity and joy.",
            'neutral': "Your balanced emotional state allows for clear decision-making.",
            'negative': "Consider mindfulness techniques or discussing concerns with trusted individuals."
        }
        return suggestions.get(emotion, "Reflect on what influences your emotional state.")
    
    def _generate_overall_summary(self, stats: Dict, insights: List[Dict]) -> str:
        """Generate overall summary"""
        if not stats or not insights:
            return "Insufficient data for summary."
        
        summary = f"## Emotion Analysis Summary\n\n"
        summary += f"Based on {stats.get('total_records', 0)} entries:\n\n"
        
        for i, insight in enumerate(insights[:3], 1):
            summary += f"{i}. {insight['content']}\n"
        
        return summary
    
    def create_visualizations(self, records: List[Dict], save_dir: str = ".") -> List[str]:
        """
        Create visualizations of emotion analysis
        
        Args:
            records: List of emotion records
            save_dir: Directory to save visualization files
            
        Returns:
            List of file paths created
        """
        if not MATPLOTLIB_AVAILABLE or not records:
            return []
        
        saved_files = []
        stats = self.calculate_basic_statistics(records)
        
        # 1. Emotion Distribution Pie Chart
        if stats.get('percentages'):
            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            fig.suptitle('Emotion Analysis Dashboard', fontsize=16, fontweight='bold')
            
            # Pie chart
            labels = list(stats['percentages'].keys())
            sizes = list(stats['percentages'].values())
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']  # Red, Teal, Blue
            
            axes[0, 0].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            axes[0, 0].set_title('Emotion Distribution')
            
            # Bar chart
            axes[0, 1].bar(labels, sizes, color=colors)
            axes[0, 1].set_title('Emotion Frequency')
            axes[0, 1].set_ylabel('Percentage')
            axes[0, 1].tick_params(axis='x', rotation=45)
            
            # Temporal pattern
            temporal = self.analyze_temporal_patterns(records)
            if temporal.get('dominant_by_hour'):
                hours = sorted(temporal['dominant_by_hour'].keys())
                dominant_emotions = [temporal['dominant_by_hour'][h]['emotion'] for h in hours]
                
                # Map emotions to colors
                emotion_colors = {'negative': '#FF6B6B', 'neutral': '#4ECDC4', 'positive': '#45B7D1'}
                colors_temporal = [emotion_colors.get(e, 'gray') for e in dominant_emotions]
                
                axes[1, 0].bar(hours, [1]*len(hours), color=colors_temporal)
                axes[1, 0].set_title('Dominant Emotion by Hour')
                axes[1, 0].set_xlabel('Hour of Day')
                axes[1, 0].set_ylabel('Dominant Emotion')
                axes[1, 0].set_xticks(range(0, 24, 3))
            
            # Transition visualization
            transitions = self.analyze_emotion_transitions(records)
            if transitions.get('most_common_transitions'):
                common_trans = transitions['most_common_transitions'][:5]
                transition_labels = [f"{t['from']}→{t['to']}" for t in common_trans]
                transition_counts = [t['count'] for t in common_trans]
                
                axes[1, 1].bar(transition_labels, transition_counts, color='#95E1D3')
                axes[1, 1].set_title('Most Common Emotion Transitions')
                axes[1, 1].set_ylabel('Count')
                axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            chart_path = f"{save_dir}/emotion_analysis.png"
            plt.savefig(chart_path, dpi=150, bbox_inches='tight')
            plt.close()
            saved_files.append(chart_path)
        
        return saved_files
    
    def export_report(self, records: List[Dict], output_path: str = "emotion_report.txt") -> str:
        """
        Export analysis report to text file
        
        Args:
            records: List of emotion records
            output_path: Path to save report
            
        Returns:
            Report content
        """
        insights = self.generate_insights(records)
        
        report = "=" * 60 + "\n"
        report += "SOUL SENSE - EMOTION ANALYSIS REPORT\n"
        report += "=" * 60 + "\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Records Analyzed: {len(records)}\n\n"
        
        # Add summary
        if insights.get('summary'):
            report += insights['summary'] + "\n\n"
        
        # Add statistics
        if insights.get('statistics'):
            stats = insights['statistics']
            report += "STATISTICS\n"
            report += "-" * 40 + "\n"
            report += f"Total Entries: {stats.get('total_records', 0)}\n"
            report += f"Most Common Emotion: {stats.get('most_common_emotion', 'N/A')}\n"
            report += f"Average Confidence: {stats.get('average_confidence', 0):.1%}\n\n"
            
            if stats.get('percentages'):
                report += "Emotion Distribution:\n"
                for emotion, percentage in stats['percentages'].items():
                    report += f"  {emotion}: {percentage:.1f}%\n"
                report += "\n"
        
        # Add insights
        if insights.get('insights'):
            report += "KEY INSIGHTS\n"
            report += "-" * 40 + "\n"
            for i, insight in enumerate(insights['insights'], 1):
                report += f"{i}. {insight['title']}\n"
                report += f"   {insight['content']}\n"
                report += f"   Suggestion: {insight['suggestion']}\n\n"
        
        # Add correlations
        if insights.get('correlations') and insights['correlations'].get('strong_associations'):
            report += "EMOTION ASSOCIATIONS\n"
            report += "-" * 40 + "\n"
            for assoc in insights['correlations']['strong_associations'][:5]:
                report += f"{assoc['pair']}: {assoc['interpretation']} (score: {assoc['score']:.3f})\n"
            report += "\n"
        
        # Add temporal patterns
        if insights.get('temporal_patterns'):
            temporal = insights['temporal_patterns']
            if temporal.get('time_of_day_stats'):
                report += "TIME-BASED PATTERNS\n"
                report += "-" * 40 + "\n"
                for period, stats_period in temporal['time_of_day_stats'].items():
                    if stats_period.get('dominant'):
                        report += f"{period.capitalize()}: Mostly {stats_period['dominant']} "
                        report += f"({stats_period.get('total', 0)} entries)\n"
                report += "\n"
        
        report += "=" * 60 + "\n"
        report += "End of Report\n"
        report += "=" * 60 + "\n"
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report