from ..services.llm_client import LLMClient
from .resume_analyzer import ResumeAnalyzerAgent
from .interviewer import InterviewerAgent
from .followup import FollowupAgent
from .technical_evaluator import TechnicalEvaluatorAgent
from .hr_evaluator import HREvaluatorAgent
from .feedback_coach import FeedbackCoachAgent
from ..utils.prompt_loader import ORCHESTRATOR_PROMPT
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    def __init__(self):
        self.llm_client = LLMClient()
        self.resume_analyzer_agent = ResumeAnalyzerAgent()
        self.interviewer_agent = InterviewerAgent()
        self.followup_agent = FollowupAgent()
        self.technical_evaluator = TechnicalEvaluatorAgent()
        self.hr_evaluator = HREvaluatorAgent()
        self.feedback_coach = FeedbackCoachAgent()

    async def analyze_resume(self, resume_text: str) -> dict:
        return await self.resume_analyzer_agent.analyze(resume_text)


    async def determine_next_stage(self, current_round: str, current_step: int, history: list, items: list = None, has_achievements: bool = False) -> str:
        """
        Determines the stage based on the number of completed interaction steps.
        current_step 0 = Introduction / Tell me about yourself.
        """
        if current_round == "hr":
            return "behavioral"
        
        # Calculate Resume Stage duration based on item types
        exp_count = sum(1 for i in (items or []) if "company" in i)
        proj_count = sum(1 for i in (items or []) if "company" not in i)
        
        # 3 questions for Exp, 4 for Projects
        resume_stage_end = (exp_count * 3) + (proj_count * 4) + 1 # +1 for intro answer
        
        # DSA Stage: exactly 2 questions
        dsa_stage_end = resume_stage_end + 2
        
        # Achievements Stage (1 question)
        achievements_stage_end = dsa_stage_end + (1 if has_achievements else 0)
        
        # HR Stage (14 questions)
        hr_stage_end = achievements_stage_end + 14

        if current_step == 0:
            return "intro"
        elif 1 <= current_step < resume_stage_end:
            return "resume_deep_dive"
        elif resume_stage_end <= current_step < dsa_stage_end:
            return "dsa_tech"
        elif has_achievements and dsa_stage_end <= current_step < achievements_stage_end:
            return "achievements"
        elif achievements_stage_end <= current_step < hr_stage_end:
            return "hr_round"
        else:
            return "wrap_up_technical"

    async def generate_response(
        self, 
        current_round: str, 
        last_question: str, 
        candidate_answer: str, 
        resume_context: str,
        current_step: int = 0,
        interview_history: list = None,
        project_count: int = 0,
        items: list = None,
        has_achievements: bool = False
    ) -> str:
        logger.info(f"Generating response: round={current_round}, step={current_step}, project_count={project_count}, has_achievements={has_achievements}")
        
        if current_round == "completed":
            return {
                "response": "The interview is already completed. Thank you!",
                "stage": "completed"
            }

        if project_count == 0:
            project_count = 2 # fallback

        # 1. Determine the stage
        stage = await self.determine_next_stage(current_round, current_step, interview_history, items, has_achievements)
        
        # Special logic for current item
        current_item_str = "General"
        item_step = 1
        total_item_questions = 3

        if stage == "resume_deep_dive" and items:
            # We need to find which item we are on by counting the steps
            running_step = 1 # step 0 was intro
            found = False
            for idx, item in enumerate(items):
                is_exp = "company" in item
                limit = 3 if is_exp else 4
                if running_step <= current_step < (running_step + limit):
                    current_item = item
                    item_step = (current_step - running_step) + 1
                    total_item_questions = limit
                    item_type = "Experience" if is_exp else "Project"
                    # Enforce Most Important Questions Rule
                    if item_step == 1:
                        if is_exp:
                            current_item_str = f"{item_type} {idx + 1} (Question 1/3: Role Overview & Core Impact): {json.dumps(current_item)}"
                        else:
                            current_item_str = f"{item_type} {idx + 1} (Question 1/4: Project Overview & Core Tech): {json.dumps(current_item)}"
                    elif item_step == 2:
                        if is_exp:
                            current_item_str = f"{item_type} {idx + 1} (Focus: Technical Challenges & Stack): {json.dumps(current_item)}"
                        else:
                             current_item_str = f"{item_type} {idx + 1} (Question 2/4: Deep Dive - Complex Challenges): {json.dumps(current_item)}"
                    elif item_step == 3:
                        if is_exp:
                            current_item_str = f"{item_type} {idx + 1} (Focus: System Design/Architecture & Trade-offs): {json.dumps(current_item)}"
                        else:
                             current_item_str = f"{item_type} {idx + 1} (Question 3/4: Architecture & Scalability Decisions): {json.dumps(current_item)}"
                    else:
                        current_item_str = f"{item_type} {idx + 1} (Question 4/4: Optimization, outcome & Future Improvements): {json.dumps(current_item)}"
                    logger.info(f"Focusing on {item_type} {idx + 1}: Step {item_step}/{limit}")
                    found = True
                    break
                running_step += limit

        # 2. Evaluate current answer
        answer_analysis = "The answer was good. Move forward to the next point promptly."
        
        if stage == "intro":
            # DIRECT JUMP: Do not ask follow-ups about intro. Move immediately to first resume item.
            if items and len(items) > 0:
                current_item = items[0]
                is_exp = "company" in current_item
                total_item_questions = 3 if is_exp else 4
                item_type = "Experience" if is_exp else "Project"
                current_item_str = f"{item_type} 1: {json.dumps(current_item)}"
                answer_analysis = f"Acknowledge the introduction BRIEFLY and transition IMMEDIATELY to the FIRST {item_type} item from the resume. No generic intro follow-ups."
            else:
                answer_analysis = "Transition to their background. Skip follow-up background questions."

        elif stage == "resume_deep_dive":
            # Specific guidance for resume items
            item_type = "Experience" if (items and item_step <= 3 and "company" in items[0]) else "Project" # Approximation for safety
            # Re-derive item_type for accurate guidance
            if items:
                running_step = 1
                for item in items:
                    limit = 3 if "company" in item else 4
                    if running_step <= current_step < (running_step + limit):
                        item_type = "Experience" if "company" in item else "Project"
                        break
                    running_step += limit

            answer_analysis = f"Analyze Answer. You are on Question {item_step} of {total_item_questions} for this {item_type}. Moving at high speed. Acknowledge briefly and ask the next technical question from the provided plan."
            if item_step == total_item_questions:
                answer_analysis += " This is the FINAL question for this item. Transition to the next item or DSA stage immediately after the answer."

        elif stage == "dsa_tech":
            current_item_str = "Technical Problem Solving (DSA)"
            # Recalculate DSA start
            exp_count = sum(1 for i in (items or []) if "company" in i)
            proj_count = sum(1 for i in (items or []) if "company" not in i)
            resume_stage_end = (exp_count * 3) + (proj_count * 4) + 1
            dsa_step = current_step - resume_stage_end + 1
            
            if dsa_step == 1:
                answer_analysis = (
                    "Provide a HIGH-FREQUENCY MEDIUM difficulty DSA problem. "
                    "Format the problem in GEEKSFORGEEKS STYLE. "
                    "Explicitly state: 'You have 8 minutes. Write only the core function logic.' "
                )
            elif dsa_step == 2:
                answer_analysis = (
                    "Provide a second HIGH-FREQUENCY MEDIUM difficulty DSA problem from a DIFFERENT topic. "
                    "Format it in GEEKSFORGEEKS STYLE. "
                    "Explicitly state: 'Second challenge. 8 minutes. Focus on function logic.' "
                    "After this, we will move to the final Behavioral/HR round."
                )
        
        elif stage == "achievements":
            current_item_str = "Final Technical Item: Achievements"
            answer_analysis = (
                "Transition strictly to discussion about significant achievements. "
                "Ask one high-level question about their most proud professional moment."
            )

        elif stage == "hr_round":
            current_item_str = "HR Round"
            # Calculate HR specific step
            hr_stage_start = achievements_stage_end if has_achievements else dsa_stage_end
            hr_step = current_step - hr_stage_start + 1
            
            hr_questions = [
                "Why do you want to join our company?",
                "Why this role specifically?",
                "What are your top 3 strengths?",
                "Tell me about a time you handled a difficult technical conflict.",
                "How do you stay updated with new technologies?",
                "Tell me about a project where you took major ownership.",
                "How do you handle tight deadlines and pressure?",
                "What is your preferred work style (remote/hybrid/colocated)?",
                "Where do you see yourself in 3–5 years?",
                "Do you have any questions for me?"
            ]
            
            total_hr = len(hr_questions)
            if 1 <= hr_step <= total_hr:
                question_text = hr_questions[hr_step - 1]
                if hr_step == 1:
                    answer_analysis = (
                        f"Start the HR round. Say: 'Great work on the technical problems. Now, let's move to the HR and Behavioral round.' "
                        f"Then ask: '{question_text}'"
                    )
                elif hr_step == total_hr:
                    answer_analysis = (
                        f"Ask the final question: '{question_text}'. "
                        "After the candidate answers, conclude by saying: 'Thank you. That concludes the interview. You can close the window.'"
                    )
                else:
                    answer_analysis = f"Ask the next HR question: '{question_text}'"
            else:
                 answer_analysis = "Conclude the interview. Say: 'Thank you. That concludes the interview. You can close the window.'"

        else:
            # Fallback
            answer_analysis = "Acknowledge the candidate's last answer very briefly and move to the next question. FOCUS ON TECHNICAL DEPTH."
            try:
                # Use followup agent to see if we MUST probe (only for resume rounds)
                if stage == "resume_deep_dive":
                    quality_response = await self.followup_agent.evaluate_answer(last_question, candidate_answer, resume_context)
                    quality = quality_response.get("quality", "good")
                    if quality == "shallow":
                        answer_analysis = f"The answer was shallow. Ask this probe: {quality_response.get('followup_question')}"
            except Exception as e:
                logger.error(f"Followup analysis failed: {e}")

        # 3. Compile history (limit context for speed)
        recent_history = (interview_history or [])[-8:]
        history_str = "\n".join([f"Q: {item['question']}\nA: {item['answer']}" for item in recent_history])
        if last_question and candidate_answer:
            history_str += f"\nQ: {last_question}\nA: {candidate_answer}"
        
        # 4. Generate response and run Gap concurrently
        try:
            interviewer_task = self.interviewer_agent.generate_response(
                current_round=current_round,
                stage=stage,
                resume_context=resume_context[:2500], # Trim context for speed
                conversation_history=history_str,
                last_answer=candidate_answer,
                followup_instruction=answer_analysis,
                current_item=current_item_str,
                item_step=item_step,
                total_item_questions=total_item_questions
            )
            
            # Run LLM call and 3.5s sleep together (Restoring 3.5s as per User preference)
            response_text, _ = await asyncio.gather(
                interviewer_task,
                asyncio.sleep(3.5)
            )

            return {
                "response": response_text,
                "stage": stage
            }
        except Exception as e:
            logger.error(f"Error in interviewer_agent: {e}")
            return {
                "response": "I see. Let's move to the next part of your resume.",
                "stage": stage
            }

    async def generate_feedback(self, session_data: dict) -> str:
        """
        Orchestrates the final evaluation.
        """
        history = session_data.get("history", [])
        resume_context = session_data.get("resume_context", "")
        technical_transcript = ""
        hr_transcript = ""
        
        for item in history:
            text = f"Interviewer: {item.get('question')}\nCandidate: {item.get('answer')}\n\n"
            if item.get("round") == "technical":
                technical_transcript += text
            else:
                hr_transcript += text

        # Prepare full transcript for holistic analysis
        full_transcript = technical_transcript + hr_transcript
        
        if not full_transcript:
            return "No interview data available to generate a report."

        # Evaluate Technical and HR in PARALLEL for speed
        try:
            # Trim contexts drastically for speed
            trimmed_tech = full_transcript[:6000]
            trimmed_hr = (hr_transcript or full_transcript)[:4000]
            trimmed_resume = resume_context[:2000]

            # Define tasks
            tech_task = self.technical_evaluator.evaluate(trimmed_tech, trimmed_resume)
            hr_task = self.hr_evaluator.evaluate(trimmed_hr)

            # Run concurrently
            technical_eval, hr_eval = await asyncio.gather(tech_task, hr_task)
            
        except Exception as e:
            logger.error(f"Parallel evaluation failed: {e}")
            technical_eval = {"error": "Technical evaluation unavailable."}
            hr_eval = {"error": "HR evaluation unavailable."}
        
        # Final synthesis
        return await self.feedback_coach.generate_report(
            technical_eval, 
            hr_eval, 
            full_transcript[:8000], 
            resume_context[:2000]
        )
