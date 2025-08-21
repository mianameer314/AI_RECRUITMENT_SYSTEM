import asyncio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from bson import ObjectId
import google.generativeai as genai
import openai
import json
import os
from typing import Dict, Any, Optional
from app.core.config import settings
from app.services.email_service import EmailService
from app.workers.celery_worker import celery_app
from app.db.sync_mongo import db_sync as db 

class LLMService:
    """Service for integrating with various LLM providers"""
    
    def __init__(self, provider: str = "gemini"):
        self.provider = provider.lower()
        self._setup_provider()
    
    def _setup_provider(self):
        """Setup the selected LLM provider"""
        if self.provider == "gemini":
            # Configure Google Gemini
            api_key = os.getenv("GENAI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
            else:
                print("Warning: GENAI_API_KEY not found, using mock service")
                self.provider = "mock"
        
        elif self.provider == "openai":
            # OpenAI is already configured via environment variables
            self.client = openai.OpenAI()
        
        elif self.provider == "mock":
            # Mock service for development
            pass
        
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def analyze_resume(self, resume_text: str, job_description: str = "") -> Dict[str, Any]:
        """
        Analyze resume and provide scoring and insights
        
        Args:
            resume_text: Extracted text from resume
            job_description: Optional job description for matching
            
        Returns:
            Dictionary containing analysis results
        """
        
        prompt = self._create_analysis_prompt(resume_text, job_description)
        
        if self.provider == "gemini":
            return self._analyze_with_gemini(prompt)
        elif self.provider == "openai":
            return self._analyze_with_openai(prompt)
        else:
            return self._analyze_with_mock(resume_text)
    
    def _create_analysis_prompt(self, resume_text: str, job_description: str = "") -> str:
        """Create a comprehensive prompt for resume analysis"""
        
        base_prompt = f"""
        Analyze the following resume and provide a comprehensive evaluation:

        RESUME TEXT:
        {resume_text}

        Please provide analysis in the following JSON format:
        {{
            "overall_score": <score from 1-100>,
            "skills": {{
                "technical_skills": [<list of technical skills found>],
                "soft_skills": [<list of soft skills found>],
                "skill_score": <score from 1-100>
            }},
            "experience": {{
                "years_of_experience": <estimated years>,
                "relevant_experience": [<list of relevant experiences>],
                "experience_score": <score from 1-100>
            }},
            "education": {{
                "degrees": [<list of degrees>],
                "certifications": [<list of certifications>],
                "education_score": <score from 1-100>
            }},
            "strengths": [<list of key strengths>],
            "weaknesses": [<list of areas for improvement>],
            "recommendations": [<list of recommendations>],
            "summary": "<brief summary of the candidate>"
        }}
        """
        
        if job_description:
            base_prompt += f"""
            
            JOB DESCRIPTION:
            {job_description}
            
            Additionally, provide job matching analysis:
            {{
                "job_match_score": <score from 1-100>,
                "matching_skills": [<skills that match job requirements>],
                "missing_skills": [<skills required but not found in resume>],
                "fit_assessment": "<assessment of candidate fit for this role>"
            }}
            """
        
        return base_prompt
    
    def _analyze_with_gemini(self, prompt: str) -> Dict[str, Any]:
        """Analyze using Google Gemini"""
        try:
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text
            
            # Try to parse JSON from response
            try:
                # Find JSON in the response
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    analysis = json.loads(json_str)
                else:
                    # Fallback if JSON parsing fails
                    analysis = self._create_fallback_analysis(response_text)
                
            except json.JSONDecodeError:
                analysis = self._create_fallback_analysis(response_text)
            
            analysis["provider"] = "gemini"
            analysis["raw_response"] = response_text
            
            return analysis
            
        except Exception as e:
            print(f"Error with Gemini API: {e}")
            return self._create_error_analysis(str(e))
    
    def _analyze_with_openai(self, prompt: str) -> Dict[str, Any]:
        """Analyze using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert HR recruiter analyzing resumes. Provide detailed, accurate analysis in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            response_text = response.choices[0].message.content
            
            # Try to parse JSON from response
            try:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    analysis = json.loads(json_str)
                else:
                    analysis = self._create_fallback_analysis(response_text)
                
            except json.JSONDecodeError:
                analysis = self._create_fallback_analysis(response_text)
            
            analysis["provider"] = "openai"
            analysis["raw_response"] = response_text
            
            return analysis
            
        except Exception as e:
            print(f"Error with OpenAI API: {e}")
            return self._create_error_analysis(str(e))
    
    def _analyze_with_mock(self, resume_text: str) -> Dict[str, Any]:
        """Mock analysis for development/testing"""
        
        # Simple keyword-based analysis for development
        technical_keywords = ["python", "javascript", "java", "react", "sql", "aws", "docker", "kubernetes"]
        soft_keywords = ["leadership", "communication", "teamwork", "problem-solving", "analytical"]
        
        text_lower = resume_text.lower()
        
        found_technical = [skill for skill in technical_keywords if skill in text_lower]
        found_soft = [skill for skill in soft_keywords if skill in text_lower]
        
        # Estimate experience based on text length and keywords
        experience_years = min(len(resume_text) // 500, 15)
        
        overall_score = min(
            50 + len(found_technical) * 5 + len(found_soft) * 3 + experience_years * 2,
            100
        )
        
        return {
            "overall_score": overall_score,
            "skills": {
                "technical_skills": found_technical,
                "soft_skills": found_soft,
                "skill_score": min(len(found_technical) * 10 + len(found_soft) * 5, 100)
            },
            "experience": {
                "years_of_experience": experience_years,
                "relevant_experience": ["Experience extracted from resume"],
                "experience_score": min(experience_years * 6, 100)
            },
            "education": {
                "degrees": ["Degree information extracted"],
                "certifications": ["Certifications found"],
                "education_score": 75
            },
            "strengths": ["Strong technical background", "Good communication skills"],
            "weaknesses": ["Could improve in specific areas"],
            "recommendations": ["Consider additional certifications", "Expand project portfolio"],
            "summary": "Candidate shows promise with relevant skills and experience",
            "provider": "mock"
        }
    
    def _create_fallback_analysis(self, response_text: str) -> Dict[str, Any]:
        """Create fallback analysis when JSON parsing fails"""
        return {
            "overall_score": 70,
            "skills": {
                "technical_skills": ["Skills analysis available in raw response"],
                "soft_skills": ["Soft skills analysis available in raw response"],
                "skill_score": 70
            },
            "experience": {
                "years_of_experience": 3,
                "relevant_experience": ["Experience analysis available in raw response"],
                "experience_score": 70
            },
            "education": {
                "degrees": ["Education analysis available in raw response"],
                "certifications": ["Certification analysis available in raw response"],
                "education_score": 70
            },
            "strengths": ["Analysis available in raw response"],
            "weaknesses": ["Analysis available in raw response"],
            "recommendations": ["Analysis available in raw response"],
            "summary": "Detailed analysis available in raw response",
            "raw_response": response_text,
            "note": "JSON parsing failed, check raw_response for detailed analysis"
        }
    
    def _create_error_analysis(self, error_message: str) -> Dict[str, Any]:
        """Create error analysis when API calls fail"""
        return {
            "overall_score": 0,
            "skills": {
                "technical_skills": [],
                "soft_skills": [],
                "skill_score": 0
            },
            "experience": {
                "years_of_experience": 0,
                "relevant_experience": [],
                "experience_score": 0
            },
            "education": {
                "degrees": [],
                "certifications": [],
                "education_score": 0
            },
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "summary": "Analysis failed due to API error",
            "error": error_message,
            "provider": self.provider
        }


# The Celery task now handles the email notification
@celery_app.task
def analyze_resume_task(resume_id: str, admin_user_id: str, job_description: str = "", provider: str = "gemini"):
    # Load resume text from JSON
    json_path = f"app/uploads/json/{resume_id}.json"
    if not os.path.exists(json_path):
        print(f"❌ Resume JSON not found: {json_path}")
        return {"error": "Resume text not found"}

    with open(json_path, 'r') as f:
        resume_data = json.load(f)

    resume_text = resume_data.get("text", "")
    llm_service = LLMService(provider=provider)
    analysis = llm_service.analyze_resume(resume_text, job_description)

    # Save analysis to JSON
    analysis_path = f"app/uploads/json/{resume_id}_analysis.json"
    with open(analysis_path, 'w') as f:
        json.dump(analysis, f, indent=4)

    # Retrieve resume metadata and candidate email using synchronous PyMongo
    resume_meta = db.resumes.find_one({"resume_id": resume_id})
    if not resume_meta:
        print(f"❌ Resume metadata not found for resume_id: {resume_id}")
        return {"error": "Resume metadata not found"}

    candidate_user_id = resume_meta.get("user_id")
    user_meta = None
    if candidate_user_id:
        try:
            obj_id = ObjectId(candidate_user_id) if isinstance(candidate_user_id, str) else candidate_user_id
            user_meta = db.users.find_one({"_id": obj_id})
        except Exception as e:
            print(f"Error retrieving user_meta: {e}")
            user_meta = None

    # Send email if user exists
    if user_meta:
        recipient_email = user_meta.get("email")
        if recipient_email:
            overall_score = analysis.get("overall_score", 0)
            score_class = "high" if overall_score >= 80 else "medium" if overall_score >= 60 else "low"

            template_data = {
                "recipient_name": user_meta.get("name", "Candidate"),
                "resume_id": resume_id,
                "overall_score": overall_score,
                "score_class": score_class,
                "summary": analysis.get("summary", "Analysis completed"),
                "strengths": analysis.get("strengths", []),
                "job_match_score": analysis.get("job_match_score"),
                "missing_skills": analysis.get("missing_skills", []),
                "fit_assessment": analysis.get("fit_assessment", ""),
                "provider": analysis.get("provider", "unknown"),
                "dashboard_url": "http://localhost:8000/dashboard"
            }

            email_task = celery_app.send_task(
                'app.services.email_service.send_email_task',
                args=[[recipient_email],
                      f"Resume Analysis Complete - {resume_id}",
                      "analysis_notification.html",
                      template_data]
            )
            print(f"✅ Email notification task enqueued: {email_task.id} for {recipient_email}")

    return {"status": "success", "analysis": analysis}


def trigger_resume_analysis(resume_id: str, job_description: str, provider: str, admin_user_id: str):
    """
    Helper function to trigger the Celery task.
    
    Args:
        resume_id: The ID of the resume to analyze
        job_description: Optional job description for matching
        provider: LLM provider to use
        admin_user_id: The admin user ID who triggered the analysis
    """
    task = analyze_resume_task.delay(resume_id, admin_user_id, job_description, provider)
    return task.id


def get_resume_analysis(resume_id: str) -> Optional[Dict[str, Any]]:
    """
    Helper function to retrieve the final analysis from the saved file.
    """
    analysis_path = f"app/uploads/json/{resume_id}_analysis.json"
    if os.path.exists(analysis_path):
        with open(analysis_path, 'r') as f:
            return json.load(f)
    return None
