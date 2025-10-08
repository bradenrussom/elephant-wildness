"""
elephant-wildness - Streamlit App
Simple interface for processing Word documents with standards
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import os
import tempfile
from pathlib import Path

from core.document_processor import DocumentProcessor
from core.text_analyzer import TextAnalyzer
from modules.communications_standards import CommunicationsStandardsProcessor


# Page config
st.set_page_config(
    page_title="Copy Standards Checker",
    page_icon="📝",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #003366;
        margin-bottom: 1rem;
    }
    .stat-box {
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .stat-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .correction-box {
        padding: 1rem;
        background: #f0f2f6;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def main():
    st.markdown('<div class="main-header">📝 Standards Checker</div>', unsafe_allow_html=True)
    st.markdown("Automatically apply Communications Standards to Word documents")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Target metrics
        st.subheader("Target Metrics")
        target_word_count = st.number_input(
            "Target Word Count",
            min_value=0,
            value=500,
            step=50,
            help="Target word count for your document"
        )
        
        target_reading_level = st.slider(
            "Target Reading Level",
            min_value=4.0,
            max_value=12.0,
            value=8.0,
            step=0.5,
            help="Target Flesch-Kincaid grade level"
        )
        
        st.divider()
        
        # SEO Keywords
        st.subheader("SEO Keywords (Optional)")
        keyword_input = st.text_area(
            "Enter keywords (one per line)",
            height=100,
            help="Enter up to 5 keywords to track"
        )
        keywords = [k.strip() for k in keyword_input.split('\n') if k.strip()][:5]
        
        st.divider()
        
        # Module selection
        st.subheader("Standards to Apply")
        apply_comms = st.checkbox("Communications Standards", value=True, 
                                  help="State abbreviations, times, terminology, etc.")
        
        st.info("More modules coming soon:\n- Digital Standards\n- Content Proofing\n- Brand Standards")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload Word Document (.docx)",
            type=['docx'],
            help="Upload a .docx file to process"
        )
    
    with col2:
        st.markdown("### Document Markers")
        st.markdown("""
        Place these in your document:
        - `start_page_copy` / `end_page_copy`
        - `start_disclaimer` / `end_disclaimer`
        
        (Optional but recommended)
        """)
    
    if uploaded_file:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        try:
            # Load document
            with st.spinner("Loading document..."):
                doc_processor = DocumentProcessor(tmp_path)
                text = doc_processor.get_all_text('page_copy')
                analyzer = TextAnalyzer(text)
            
            # Display current stats
            st.header("📊 Document Analysis")
            
            stats = analyzer.get_document_stats()
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-value">{stats['word_count']}</div>
                    <div class="stat-label">Words</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-value">{stats['sentence_count']}</div>
                    <div class="stat-label">Sentences</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                reading_level = analyzer.reading_level()
                st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-value">{reading_level:.1f}</div>
                    <div class="stat-label">Reading Level</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                avg_sentence = analyzer.average_sentence_length()
                st.markdown(f"""
                <div class="stat-box">
                    <div class="stat-value">{avg_sentence:.1f}</div>
                    <div class="stat-label">Avg Sentence Length</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Target comparison
            if target_word_count or target_reading_level:
                st.subheader("🎯 Target Comparison")
                comparison = analyzer.compare_to_target(target_word_count, target_reading_level)
                
                col1, col2 = st.columns(2)
                with col1:
                    if 'word_count' in comparison:
                        wc = comparison['word_count']
                        status_emoji = "✅" if wc['status'] == 'on_target' else "⚠️"
                        st.markdown(f"""
                        **Word Count:** {status_emoji}
                        - Target: {wc['target']}
                        - Actual: {wc['actual']}
                        - Difference: {wc['difference']:+d}
                        """)
                
                with col2:
                    if 'reading_level' in comparison:
                        rl = comparison['reading_level']
                        status_emoji = "✅" if rl['status'] == 'on_target' else "⚠️"
                        st.markdown(f"""
                        **Reading Level:** {status_emoji}
                        - Target: {rl['target']:.1f}
                        - Actual: {rl['actual']:.1f}
                        - Difference: {rl['difference']:+.1f}
                        """)
            
            # Keyword analysis
            if keywords:
                st.subheader("🔍 Keyword Analysis")
                kw_results = analyzer.keyword_frequency(keywords)
                
                for kw, stats in kw_results.items():
                    density_status = "✅" if 3 <= stats['density'] <= 4 else "⚠️"
                    st.markdown(f"""
                    <div class="correction-box">
                        <strong>{kw}</strong> {density_status}<br>
                        Occurrences: {stats['count']} | Density: {stats['density']:.2f}%
                        {'(Recommended: 3-4%)' if stats['density'] < 3 or stats['density'] > 4 else ''}
                    </div>
                    """, unsafe_allow_html=True)
            
            # Process button
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔧 Process Document", type="primary", use_container_width=True):
                    if not apply_comms:
                        st.warning("No standards modules selected!")
                    else:
                        with st.spinner("Applying corrections..."):
                            # Apply communications standards
                            total_corrections = 0
                            
                            if apply_comms:
                                comms_processor = CommunicationsStandardsProcessor(doc_processor)
                                corrections_count = comms_processor.process()
                                total_corrections += corrections_count
                                
                                # Add analysis report
                                report = analyzer.generate_summary(
                                    target_word_count=target_word_count,
                                    target_reading_level=target_reading_level,
                                    keywords=keywords
                                )
                                report += "\n\n" + "="*50 + "\n"
                                report += f"CORRECTIONS APPLIED: {total_corrections}\n"
                                report += "="*50 + "\n\n"
                                
                                summary = comms_processor.get_corrections_summary()
                                for rule, count in summary.items():
                                    report += f"{rule}: {count}\n"
                                
                                doc_processor.add_analysis_section(report)
                            
                            # Save to temp file
                            output_path = tmp_path.replace('.docx', '_processed.docx')
                            doc_processor.save(output_path)
                            
                            # Success message
                            st.success(f"✨ Applied {total_corrections} corrections!")
                            
                            # Show corrections by category
                            if apply_comms:
                                st.subheader("📋 Corrections Applied")
                                summary = comms_processor.get_corrections_summary()
                                
                                for rule, count in summary.items():
                                    st.markdown(f"""
                                    <div class="correction-box">
                                        <strong>{rule}</strong>: {count} correction(s)
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            # Download button
                            with open(output_path, 'rb') as f:
                                st.download_button(
                                    label="📥 Download Processed Document",
                                    data=f,
                                    file_name=f"{Path(uploaded_file.name).stem}_processed.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    use_container_width=True
                                )
                            
                            # Cleanup
                            os.unlink(output_path)
            
            with col2:
                st.button("🔍 Analyze Only", help="Coming soon: Preview corrections without applying", 
                         disabled=True, use_container_width=True)
        
        finally:
            # Cleanup temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


if __name__ == '__main__':
    main()
