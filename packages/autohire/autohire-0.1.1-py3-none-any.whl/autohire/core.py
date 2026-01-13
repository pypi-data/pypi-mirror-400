import os
from langchain_openai import ChatOpenAI
from autohire.utils import extract_text, create_pdf_from_text
from autohire.agents import analyze_resume_and_jd, generate_tailored_resume

def process_resume(resume_path, jd_path, openai_api_key):
    """
    Takes a resume (PDF/DOCX), job description file, and OpenAI API key.
    Generates a tailored resume and saves it to 'tailored_resume' folder.
    """
    if not os.path.exists(resume_path):
        return f"Error: Resume file not found at {resume_path}"
    if not os.path.exists(jd_path):
        return f"Error: Job Description file not found at {jd_path}"

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7, api_key=openai_api_key)

    # Extract Text
    print("Extracting text...")
    resume_text = extract_text(resume_path)
    if "Error" in resume_text:
        return resume_text
    
    jd_text = extract_text(jd_path)
    if "Error" in jd_text:
        return jd_text

    # Analyze
    print("Analyzing...")
    analysis = analyze_resume_and_jd(resume_text, jd_text, llm)
    
    # Generate
    print("Generating tailored resume...")
    tailored_text = generate_tailored_resume(resume_text, jd_text, analysis, llm)
    
    # Save
    output_dir = "tailored_resume"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename based on original resume name
    base_name = os.path.splitext(os.path.basename(resume_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}_tailored.pdf")
    
    print(f"Saving to {output_path}...")
    create_pdf_from_text(tailored_text, output_path)
    
    return f"Success! Tailored resume saved to {output_path}"

def main():
    import argparse
    parser = argparse.ArgumentParser(description="AutoHire AI - Tailor your resume")
    parser.add_argument("resume", help="Path to resume file (PDF/DOCX)")
    parser.add_argument("jd", help="Path to job description file (TXT)")
    parser.add_argument("--key", help="OpenAI API Key", required=False)
    
    args = parser.parse_args()
    
    api_key = args.key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in env or arguments.")
        return

    result = process_resume(args.resume, args.jd, api_key)
    print(result)

if __name__ == "__main__":
    main()
