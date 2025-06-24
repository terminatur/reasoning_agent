"""
File: src/components/synthesis.py
Purpose: Research synthesis and report generation component for combining findings into comprehensive reports
Functionality: Synthesizes research results, generates structured reports, manages citations, and ensures quality
Update Trigger: When report formats change, synthesis algorithms are updated, or citation standards are modified
Last Modified: 2024-06-24
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import re

try:
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from ..config import config
from ..models import ResearchReport, Citation, ToolResult

class ResearchSynthesizer:
    """
    Synthesizes research findings into comprehensive reports.
    Handles citation management, content organization, and quality assurance.
    """
    
    def __init__(self):
        self.model_name = config.get_model_config("synthesis")
        self.llm = None
        
        if LANGCHAIN_AVAILABLE and config.OPENAI_API_KEY:
            try:
                self.llm = ChatOpenAI(
                    model=self.model_name,
                    api_key=config.OPENAI_API_KEY,
                    temperature=0.3  # Moderate temperature for creative synthesis
                )
            except Exception as e:
                print(f"Warning: Could not initialize LLM for synthesis: {e}")
        else:
            print("Warning: LangChain not available. Synthesizer will use template-based generation.")
    
    def generate_report(
        self,
        query: str,
        research_results: List[ToolResult],
        context: str = "",
        report_style: str = "comprehensive"
    ) -> ResearchReport:
        """
        Generate a comprehensive research report from collected findings.
        
        Args:
            query: Original research query
            research_results: List of tool results from research steps
            context: Additional context for synthesis
            report_style: Style of report ("comprehensive", "executive", "academic")
        """
        # Extract and organize findings
        organized_findings = self._organize_findings(research_results)
        
        # Extract citations
        citations = self._extract_citations(research_results)
        
        # Generate report sections
        if self.llm:
            report_sections = self._generate_report_with_llm(
                query, organized_findings, citations, context, report_style
            )
        else:
            report_sections = self._generate_template_report(
                query, organized_findings, citations
            )
        
        # Create final report
        report = ResearchReport(
            query=query,
            executive_summary=report_sections["executive_summary"],
            detailed_findings=report_sections["detailed_findings"],
            conclusions=report_sections["conclusions"],
            citations=citations,
            methodology=report_sections["methodology"],
            limitations=report_sections.get("limitations"),
        )
        
        return report
    
    def _organize_findings(self, research_results: List[ToolResult]) -> Dict[str, List[str]]:
        """Organize research findings by type and relevance."""
        organized = {
            "web_search_results": [],
            "pdf_analysis": [],
            "data_analysis": [],
            "general_findings": [],
            "errors": []
        }
        
        for result in research_results:
            if not result.success:
                organized["errors"].append(f"Error from {result.tool_name}: {result.error_message}")
                continue
                
            content = str(result.result)
            
            if result.tool_name == "web_search":
                organized["web_search_results"].append(content)
            elif result.tool_name == "pdf_parser":
                organized["pdf_analysis"].append(content)
            elif result.tool_name == "data_analyzer":
                organized["data_analysis"].append(content)
            else:
                organized["general_findings"].append(content)
        
        return organized
    
    def _extract_citations(self, research_results: List[ToolResult]) -> List[Citation]:
        """Extract citations from research results."""
        citations = []
        
        for result in research_results:
            if not result.success:
                continue
                
            # Handle web search results with citations
            if result.tool_name == "web_search" and isinstance(result.result, dict):
                result_citations = result.result.get("citations", [])
                for citation_data in result_citations:
                    if isinstance(citation_data, dict):
                        citation = Citation(
                            source_url=citation_data.get("source_url"),
                            title=citation_data.get("title", "Unknown Title"),
                            author=citation_data.get("author"),
                            publication_date=None,  # Would need date parsing
                            accessed_date=datetime.now(),
                            snippet=citation_data.get("snippet", ""),
                            relevance_score=citation_data.get("relevance_score", 0.5)
                        )
                        citations.append(citation)
            
            # Handle PDF citations
            elif result.tool_name == "pdf_parser" and isinstance(result.result, dict):
                citation_data = result.result.get("citation", {})
                if citation_data:
                    citation = Citation(
                        source_url=citation_data.get("source_url"),
                        title=citation_data.get("title", "PDF Document"),
                        author=citation_data.get("author"),
                        publication_date=None,  # Would need date parsing
                        accessed_date=datetime.now(),
                        snippet="PDF document analysis",
                        relevance_score=0.8
                    )
                    citations.append(citation)
        
        # Remove duplicates based on URL or title
        unique_citations = []
        seen_urls = set()
        seen_titles = set()
        
        for citation in citations:
            identifier = citation.source_url or citation.title
            if identifier not in seen_urls and citation.title not in seen_titles:
                unique_citations.append(citation)
                if citation.source_url:
                    seen_urls.add(citation.source_url)
                seen_titles.add(citation.title)
        
        return unique_citations
    
    def _generate_report_with_llm(
        self,
        query: str,
        findings: Dict[str, List[str]],
        citations: List[Citation],
        context: str,
        report_style: str
    ) -> Dict[str, str]:
        """Generate report sections using LLM."""
        try:
            # Combine all findings into context
            findings_text = self._format_findings_for_llm(findings)
            citations_text = self._format_citations_for_llm(citations)
            
            sections = {}
            
            # Generate executive summary
            sections["executive_summary"] = self._generate_executive_summary(
                query, findings_text, context
            )
            
            # Generate detailed findings
            sections["detailed_findings"] = self._generate_detailed_findings(
                query, findings_text, citations_text, context
            )
            
            # Generate conclusions
            sections["conclusions"] = self._generate_conclusions(
                query, findings_text, context
            )
            
            # Generate methodology
            sections["methodology"] = self._generate_methodology(findings)
            
            # Generate limitations (if comprehensive report)
            if report_style == "comprehensive":
                sections["limitations"] = self._generate_limitations(findings)
            
            return sections
            
        except Exception as e:
            print(f"Error generating report with LLM: {e}")
            return self._generate_template_report(query, findings, citations)
    
    def _generate_template_report(
        self,
        query: str,
        findings: Dict[str, List[str]],
        citations: List[Citation]
    ) -> Dict[str, str]:
        """Generate basic report using templates."""
        sections = {}
        
        # Count findings
        total_findings = sum(len(finding_list) for finding_list in findings.values())
        web_results = len(findings.get("web_search_results", []))
        pdf_results = len(findings.get("pdf_analysis", []))
        
        sections["executive_summary"] = f"""
This research investigated: {query}

The investigation gathered information from {total_findings} sources, including {web_results} web sources and {pdf_results} document analyses. Key findings indicate significant information available on this topic across multiple domains.

The research provides insights into current trends, established practices, and emerging developments related to the query.
        """.strip()
        
        sections["detailed_findings"] = f"""
## Web Search Results
{len(findings.get('web_search_results', []))} web sources were analyzed, providing current information and diverse perspectives on the topic.

## Document Analysis  
{len(findings.get('pdf_analysis', []))} documents were analyzed for detailed technical information and established research.

## Key Insights
The research reveals multiple facets of {query}, with evidence supporting various approaches and considerations.
        """.strip()
        
        sections["conclusions"] = f"""
Based on the comprehensive research conducted:

1. The topic of {query} has substantial documentation and ongoing discussion
2. Multiple perspectives and approaches exist in the current literature
3. Further investigation may be warranted in specific areas identified during research

The findings provide a solid foundation for understanding the current state of knowledge regarding {query}.
        """.strip()
        
        sections["methodology"] = f"""
This research employed a systematic approach using multiple information sources:

1. Web search for current information and diverse perspectives
2. Document analysis for detailed technical content
3. Synthesis of findings from multiple sources
4. Citation management for traceability

Total sources analyzed: {total_findings}
        """.strip()
        
        return sections
    
    def _format_findings_for_llm(self, findings: Dict[str, List[str]]) -> str:
        """Format findings for LLM consumption."""
        formatted = []
        
        for category, finding_list in findings.items():
            if finding_list and category != "errors":
                formatted.append(f"## {category.replace('_', ' ').title()}")
                for i, finding in enumerate(finding_list[:3], 1):  # Limit to prevent token overflow
                    # Truncate very long findings
                    truncated_finding = finding[:1000] + "..." if len(finding) > 1000 else finding
                    formatted.append(f"{i}. {truncated_finding}")
                formatted.append("")
        
        return "\n".join(formatted)
    
    def _format_citations_for_llm(self, citations: List[Citation]) -> str:
        """Format citations for LLM consumption."""
        if not citations:
            return "No specific citations available."
        
        formatted = ["## Available Citations"]
        for i, citation in enumerate(citations[:10], 1):  # Limit citations
            citation_text = f"{i}. {citation.title}"
            if citation.author:
                citation_text += f" by {citation.author}"
            if citation.source_url:
                citation_text += f" ({citation.source_url})"
            formatted.append(citation_text)
        
        return "\n".join(formatted)
    
    def _generate_executive_summary(self, query: str, findings: str, context: str) -> str:
        """Generate executive summary using LLM."""
        prompt = f"""Write a concise executive summary for a research report.

Research Query: {query}
Context: {context}

Research Findings:
{findings}

Write a 3-4 paragraph executive summary that:
1. States the research objective clearly
2. Summarizes the key findings
3. Highlights the most important insights
4. Provides a brief overview of implications

Executive Summary:"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"Error generating executive summary: {e}")
            return f"Research was conducted on: {query}. Multiple sources were analyzed to provide comprehensive insights."
    
    def _generate_detailed_findings(self, query: str, findings: str, citations: str, context: str) -> str:
        """Generate detailed findings section using LLM."""
        prompt = f"""Write a detailed findings section for a research report.

Research Query: {query}
Context: {context}

Research Findings:
{findings}

Available Citations:
{citations}

Write a comprehensive findings section that:
1. Organizes information by themes or categories
2. Presents evidence systematically
3. References sources appropriately
4. Maintains objectivity
5. Includes specific details and examples

Detailed Findings:"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"Error generating detailed findings: {e}")
            return "Detailed analysis of research findings reveals multiple perspectives and comprehensive information on the topic."
    
    def _generate_conclusions(self, query: str, findings: str, context: str) -> str:
        """Generate conclusions section using LLM."""
        prompt = f"""Write a conclusions section for a research report.

Research Query: {query}
Context: {context}

Research Findings:
{findings}

Write a conclusions section that:
1. Synthesizes the key findings
2. Addresses the original research question
3. Identifies patterns and trends
4. Discusses implications
5. Suggests areas for further investigation

Conclusions:"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            print(f"Error generating conclusions: {e}")
            return "The research provides valuable insights into the topic and establishes a foundation for further investigation."
    
    def _generate_methodology(self, findings: Dict[str, List[str]]) -> str:
        """Generate methodology section based on tools used."""
        methods = []
        
        if findings.get("web_search_results"):
            methods.append("Web search analysis using current online sources")
        
        if findings.get("pdf_analysis"):
            methods.append("Document analysis of PDF sources")
        
        if findings.get("data_analysis"):
            methods.append("Quantitative data analysis and visualization")
        
        if not methods:
            methods.append("Multi-source information gathering and analysis")
        
        methodology = "This research employed the following methodology:\n\n"
        for i, method in enumerate(methods, 1):
            methodology += f"{i}. {method}\n"
        
        methodology += "\nThe research followed a systematic approach to ensure comprehensive coverage of the topic."
        
        return methodology
    
    def _generate_limitations(self, findings: Dict[str, List[str]]) -> str:
        """Generate limitations section."""
        limitations = ["This research has several limitations to consider:"]
        
        if findings.get("errors"):
            limitations.append("- Some information sources were not accessible during the research period")
        
        limitations.extend([
            "- The research is limited to sources available at the time of investigation",
            "- Information currency may vary across different sources",
            "- The scope was constrained by available tools and time limits",
            "- Further validation of findings may be beneficial"
        ])
        
        return "\n".join(limitations)
    
    def get_report_statistics(self, report: ResearchReport) -> Dict[str, Any]:
        """Get statistics about the generated report."""
        return {
            "total_word_count": report.word_count,
            "sections": {
                "executive_summary": len(report.executive_summary.split()),
                "detailed_findings": len(report.detailed_findings.split()),
                "conclusions": len(report.conclusions.split())
            },
            "citations_count": len(report.citations),
            "generated_at": report.generated_at.isoformat(),
            "has_limitations": report.limitations is not None
        }
    
    def export_report(self, report: ResearchReport, format_type: str = "markdown") -> str:
        """Export report in different formats."""
        if format_type == "markdown":
            return self._export_markdown(report)
        elif format_type == "text":
            return self._export_text(report)
        else:
            return self._export_text(report)
    
    def _export_markdown(self, report: ResearchReport) -> str:
        """Export report as Markdown."""
        markdown = f"""# Research Report: {report.query}

*Generated on {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}*

## Executive Summary

{report.executive_summary}

## Detailed Findings

{report.detailed_findings}

## Conclusions

{report.conclusions}

## Methodology

{report.methodology}
"""
        
        if report.limitations:
            markdown += f"\n## Limitations\n\n{report.limitations}\n"
        
        if report.citations:
            markdown += "\n## References\n\n"
            for i, citation in enumerate(report.citations, 1):
                citation_text = f"{i}. {citation.title}"
                if citation.author:
                    citation_text += f" by {citation.author}"
                if citation.source_url:
                    citation_text += f" - {citation.source_url}"
                citation_text += f" (Accessed: {citation.accessed_date.strftime('%Y-%m-%d')})"
                markdown += citation_text + "\n"
        
        return markdown
    
    def _export_text(self, report: ResearchReport) -> str:
        """Export report as plain text."""
        text = f"RESEARCH REPORT: {report.query.upper()}\n"
        text += f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += "=" * 60 + "\n\n"
        
        text += "EXECUTIVE SUMMARY\n" + "-" * 20 + "\n"
        text += report.executive_summary + "\n\n"
        
        text += "DETAILED FINDINGS\n" + "-" * 20 + "\n"
        text += report.detailed_findings + "\n\n"
        
        text += "CONCLUSIONS\n" + "-" * 20 + "\n"
        text += report.conclusions + "\n\n"
        
        text += "METHODOLOGY\n" + "-" * 20 + "\n"
        text += report.methodology + "\n\n"
        
        if report.limitations:
            text += "LIMITATIONS\n" + "-" * 20 + "\n"
            text += report.limitations + "\n\n"
        
        if report.citations:
            text += "REFERENCES\n" + "-" * 20 + "\n"
            for i, citation in enumerate(report.citations, 1):
                text += f"{i}. {citation.title}\n"
        
        return text
