import os
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

class AnalysisResult(BaseModel):
    key_developments: List[str] = Field(
        description="Key technical or commercial developments identified in the evidence."
    )
    opportunities: List[str] = Field(
        description="Opportunities that these developments present for an organization."
    )
    threats: List[str] = Field(
        description="Threats or competitive risks that these developments present for an organization."
    )
    trends: List[str] = Field(
        description="Emerging industry or technology trends identified."
    )
    confidence_score: str = Field(
        description="Confidence level in these findings. Must be one of: High, Medium, Low."
    )
    confidence_justification: str = Field(
        description="Explanation/justification for the chosen confidence score."
    )

def analyze_information(information: str) -> Dict[str, Any]:
    """
    Analyze collected competitive intelligence evidence using Gemini.
    
    Args:
        information: Combined text of all collected evidence.
        
    Returns:
        Dict representing the structured AnalysisResult.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
        
    if not information or not information.strip():
        return {
            "key_developments": [],
            "opportunities": [],
            "threats": [],
            "trends": [],
            "confidence_score": "Low",
            "confidence_justification": "No evidence was provided to analyze."
        }
        
    model_name = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
    
    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.1
        )
        
        structured_llm = llm.with_structured_output(AnalysisResult)
        
        prompt = (
            "You are an expert Competitive Intelligence Analyst.\n"
            "Your objective is to analyze the gathered raw information and research findings to extract actionable insights.\n\n"
            "Gathered Evidence:\n"
            f"\"\"\"\n{information}\n\"\"\"\n\n"
            "Analyze the above evidence and populate the required analysis fields carefully."
        )
        
        analysis = structured_llm.invoke(prompt)
        return analysis.model_dump()
    except Exception as e:
        raise RuntimeError(f"Gemini information analysis failed: {str(e)}")
