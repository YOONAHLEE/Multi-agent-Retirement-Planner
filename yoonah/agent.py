try:
    from .financial_report_pipeline import adaptive_rag, SUMMARY_CACHE_PATH
except:
    from financial_report_pipeline import adaptive_rag, SUMMARY_CACHE_PATH

from datetime import date

def write_report(
    query="오늘의 금융 보고서를 작성해주세요", 
    date=date.today().isoformat()):
    """
    Generates a financial report based on the provided query and date.
    Args:
        query (str): The financial query to be processed.
        date (str): The date for which the report is generated. default is today's date in ISO format.
        or you can put the direct date in the format 'YYYY-MM-DD'.
    Returns:
        str: A message indicating the completion of the report generation.
    """
    # Process the query and generate the report
    # This is a placeholder for the actual implementation
    print(f"Generating report for query: {query} on date: {date}")
    
    # Initialize state with required keys
    inputs = {
        "date": date,
        "query": query,
        "documents": [],  # Initialize empty documents list
        "doc_summary_chunks": [],
        "doc_summary": "",
        "web_summary": "",
        "final_output": "",
        "db_path": SUMMARY_CACHE_PATH
    }

    result = adaptive_rag.invoke(inputs)
    report = result.get("final_output", "")
    return "Report generation completed."



if __name__ == "__main__":
    # Example usage
    query = "오늘의 금융 보고서를 작성해주세요"
    date_str = "2025-06-11"  # Example date, can be changed as needed
    result = write_report(query=query, date=date_str)
    print(result)  # Output the result of the report generation
