# Emotion_Classification/analyze_correlations.py
"""
Example script for running correlation analysis
"""

import pandas as pd
from correlation_analysis import EmotionCorrelationAnalyzer

def main():
    # Initialize analyzer
    analyzer = EmotionCorrelationAnalyzer()
    
    # Example texts for analysis (replace with your actual data)
    sample_texts = [
        "I feel absolutely wonderful today! Everything is going great.",
        "This is just okay, nothing special.",
        "I'm really disappointed and upset about what happened.",
        "The weather is nice but I have to work.",
        "Terrible day, everything went wrong from start to finish.",
        "I'm neutral about this situation.",
        "Happy birthday to me! Best day ever!",
        "I'm frustrated and angry with the results.",
        "It's a normal day, nothing exciting.",
        "I'm overjoyed with the news!"
    ]
    
    print("Analyzing text batch for correlations...")
    print(f"Number of texts: {len(sample_texts)}")
    print("-" * 50)
    
    # Run analysis
    results = analyzer.analyze_text_batch(sample_texts)
    
    # Print summary
    print("\n" + results['emotion_correlations']['summary'])
    
    # Print distribution
    print("\nEmotion Distribution:")
    for emotion, stats in results['emotion_distribution'].items():
        print(f"  {emotion}: {stats['count']} ({stats['percentage']:.1f}%)")
    
    # Print significant correlations
    print("\nSignificant Correlations (p < 0.05):")
    if results['emotion_correlations']['significant_correlations']:
        for corr in results['emotion_correlations']['significant_correlations']:
            print(f"  {corr['emotion_pair']}: r = {corr['pearson_correlation']:.3f}, p = {corr['p_value']:.4f}")
    else:
        print("  No significant correlations found.")
    
    # Visualize
    print("\nGenerating visualizations...")
    analyzer.visualize_correlations(results['probabilities'], save_path="correlation_analysis.png")
    
    # Generate report
    print("\nGenerating HTML report...")
    html_report = analyzer.generate_report(results, output_path="emotion_correlation_report.html")
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()