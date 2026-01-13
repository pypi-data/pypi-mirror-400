from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

# Initialize LLM removed


def analyze_resume_and_jd(resume_text, jd_text, llm):
    prompt = ChatPromptTemplate.from_template(
        """
        You are an expert ATS (Applicant Tracking System) Optimization Specialist and Recruiter.
        Analyze the following Resume and Job Description (JD) with the goal of maximizing the ATS match score.
        
        RESUME:
        {resume}
        
        JOB DESCRIPTION:
        {jd}
        
        Provide a structured analysis including:
        1. **Hard Skills Match**: List skills found in JD that are missing or weak in the resume.
        2. **Soft Skills Match**: List soft skills/competencies from JD.
        3. **Keywords to Add**: Exact phrases from the JD that MUST be included in the resume to pass ATS filters.
        4. **Experience Gaps**: Areas where the resume fails to demonstrate required experience.
        5. **ATS Score Prediction**: Estimate the current match score (0-100).
        """
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"resume": resume_text, "jd": jd_text})

def humanize_text(text, llm, type="resume"):
    if type == "resume":
        instructions = """
        **Refinement Goals:**
        1. **Sentence Variance**: Mix short, punchy sentences (5-10 words) with longer, detailed ones.
        2. **Vocabulary**: Replace "corporate speak" with "plain English". (e.g., instead of "facilitated", use "helped" or "ran").
        3. **Structure**: Ensure bullet points don't all start with the same verb tense or pattern.
        """
    else:
        instructions = """
        **Refinement Goals:**
        1. **Tone**: Make it sound like a driven professional talking to a colleague. Confident but not arrogant.
        2. **Flow**: Ensure smooth transitions between paragraphs. Avoid "In conclusion" or "Furthermore".
        3. **Hook**: Ensure the opening sentence grabs attention immediately.
        """

    prompt = ChatPromptTemplate.from_template(
        """
        You are a Senior Editor and Ghostwriter known for your "Anti-AI" writing style.
        Your task is to rewrite the following text to make it undetectable by AI detectors.
        
        **ORIGINAL TEXT:**
        {text}
        
        **STRICT RULES:**
        1. **Perplexity Injection**: Intentionally vary sentence length and structure. AI writes in uniform patterns; Humans are chaotic.
        2. **Burstiness**: Group short sentences together for impact, then follow with a long explanatory sentence.
        3. **No Fluff**: Remove adjectives that add no value (e.g., "visionary", "strategic", "esteemed").
        4. **Keep Keywords**: You MUST retain the specific technical skills and metrics from the original text.
        
        {instructions}
        
        **FEW-SHOT EXAMPLES (BAD vs GOOD):**
        
        *Bad (AI)*: "I utilized my extensive communication skills to facilitate a collaborative environment."
        *Good (Human)*: "I brought the team together to fix our communication gaps."
        
        *Bad (AI)*: "This project was pivotal in transforming our digital landscape."
        *Good (Human)*: "This project changed how we handle digital assets."
        
        Output ONLY the rewritten text.
        """
    )
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"text": text, "instructions": instructions})

def generate_tailored_resume(resume_text, jd_text, analysis, llm):
    # Step 1: Draft with Content Focus
    draft_prompt = ChatPromptTemplate.from_template(
        """
        You are an expert Resume Writer.
        Draft a resume based on the following inputs. Focus purely on CONTENT and METRICS first.
        
        RESUME:
        {resume}
        
        JOB DESCRIPTION:
        {jd}
        
        ANALYSIS:
        {analysis}
        
        **DRAFTING INSTRUCTIONS:**
        1. Include all "Keywords to Add" from the analysis.
        2. Use the STAR method for bullet points.
        3. Ensure all hard skills are listed.
        
        Output the draft in Markdown.
        """
    )
    draft_chain = draft_prompt | llm | StrOutputParser()
    draft = draft_chain.invoke({"resume": resume_text, "jd": jd_text, "analysis": analysis})
    
    # Step 2: Humanize
    return humanize_text(draft, llm, type="resume")

def generate_cover_letter(resume_text, jd_text, llm):
    # Step 1: Draft
    draft_prompt = ChatPromptTemplate.from_template(
        """
        Draft a cover letter for this role.
        
        RESUME:
        {resume}
        
        JOB DESCRIPTION:
        {jd}
        
        Structure: Hook -> Story -> Close.
        """
    )
    draft_chain = draft_prompt | llm | StrOutputParser()
    draft = draft_chain.invoke({"resume": resume_text, "jd": jd_text})
    
    # Step 2: Humanize
    return humanize_text(draft, llm, type="cover_letter")
