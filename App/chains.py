import os
from langchain_groq import  ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv
from numpy.fft.helper import ifftshift
from prompt_toolkit.key_binding.bindings.named_commands import self_insert

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model= "llama-3.3-70b-versatile" , temperature=0,)

    def extract_jobs(self , cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """"
            ### Scraped text from website{page_data}
            ### Instruction"
            Your job is to extract the job postings and return them in JSON format containing
            the following keys: `role` , `experience`, `skills` , `location` and `description`
            only return the valid JSON
            
            DO NOT infer, guess, or invent information.
            DO NOT use prior knowledge.
            ONLY use the text above.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Content too big . Unable to parse jobs.")
        return res if isinstance(res , list) else [res]

    def write_mail(self, job, links):
        prompt_email = PromptTemplate.from_template(
        """
            ### JOB DESCRIPTION:
            {job_description}
        
            ### INSTRUCTION:
            You are Khushi, a Business Development Executive at EY.
            EY is a global professional services firm that provides
            assurance, consulting, strategy, tax, and technology services.
        
            Over our experience, EY has helped enterprises with:
            - Digital transformation
            - Process automation and optimization
            - Risk management and compliance
            - Data, AI, and technology-driven solutions
        
            Your task is to write a **personalized cold email** to the client
            based on the job description above, explaining how EY can help
            solve their specific needs.
        
            Also include the **most relevant links** from the following list
            to showcase EY’s portfolio:
            {portfolio_links}
        
            Guidelines:
            - Be concise and professional
            - Focus on value, not features
            - Do NOT exaggerate or fabricate
            - Do NOT include a subject line
            - Do NOT add any preamble or explanation
        
            ### EMAIL (NO PREAMBLE):
            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job) , "portfolio_links": links})
        return res.content
if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))