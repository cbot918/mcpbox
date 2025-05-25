from mcp.server.fastmcp import FastMCP
from mcp.client.stdio import stdio_client
import requests
import logging

logging.basicConfig(level=logging.INFO)
mcp = FastMCP("My App")

print("mcp server starting111...")

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def extract_pdf() -> str:
    logging.info("=====================")
    content = read_file("a.txt")
    logging.info(content)

    url = "http://localhost:8080/api/v1/general/rearrange-pages"

    # Read the PDF file
    with open("112翰林大滿貫乙卷數學_答案.pdf", "rb") as f:
        files = {
            "fileInput": ("112下國小南一數學6下新超群百分測驗卷_rearranged.pdf", f, "application/pdf")
        }

        data = {
            "customMode": "",
            "pageNumbers": "1,3,4,10"
        }

        response = requests.post(url, files=files, data=data)

    # Save the response if it's a file (e.g., PDF)
    if response.ok:
        with open("edited_pdf.pdf", "wb") as out_file:
            out_file.write(response.content)
        logging.info("PDF received and saved as output.pdf")
    else:
        logging.info("Request failed:", response.status_code, response.text)


    return {"content": content}
