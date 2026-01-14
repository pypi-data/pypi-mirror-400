from fastapi import Query,HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import re
from pathlib import Path

#STATIC_DIR = "static"  # Make sure this matches the main.py path
documents_folder = Path.home() / "Documents"
question_bank_folder = documents_folder / "WebCam_OMR" / "Question_Bank"



async def where_to_copy_question_bank(base_folder: Path):
    """
    Returns the directory path where question bank files should be copied.
    Automatically creates the folder if it doesn't exist.
    
    Args:
        base_folder (Path): Base directory under which 'Question_Bank' folder will be created.
    
    Returns:
        dict: {
            "path": str(path_to_question_bank_folder),
            "example_file_name": example_file_name
        }
    """
    try:
        question_bank_folder = base_folder / "Question_Bank"

        # Ensure folder exists
        question_bank_folder.mkdir(parents=True, exist_ok=True)

        example_file_name = "CourseCode.tex  (e.g., EE3200.tex, EE1103.tex, CSE2229.tex etc.)"

        return {
            "path": str(question_bank_folder),
            "example_file_name": example_file_name
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating folder: {e}")




# ------------------ Pydantic model ------------------
class AddQuestionRequest(BaseModel):
    department: str
    courseCode: str
    questionType: str
    questionStatement: str
    correctAns: str
    options: Optional[List[str]] = None
    mcqMark: Optional[float] = None


# ------------------ Load or create question bank ------------------
async def load_or_create_question_bank(base_folder: Path, courseCode: str = Query(...)):
    filename = f"{courseCode}.tex"
    question_bank_folder = base_folder / "Question_Bank"
    filepath = os.path.join(question_bank_folder, filename)

    file_created = False

    # If file does not exist, create it
    if not os.path.exists(filepath):
        file_created = True
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(
                "%----------------------------------------------------\n"
                "%                  T/F questions\n"
                "%----------------------------------------------------\n\n"
                "%----------------------------------------------------\n"
                "%                  MCQ questions\n"
                "%----------------------------------------------------\n\n"
            )

    # Read the file content
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Return JSON including content and optional file path if created
    response_data = {"texContent": content}
    if file_created:
        response_data["createdFilePath"] = filepath

    return JSONResponse(response_data)
    



# ------------------ Add question ------------------
async def add_question(base_folder: Path, request_add_q_data: AddQuestionRequest):
    data = request_add_q_data
    question_bank_folder = base_folder / "Question_Bank"

    filename = f"{data.courseCode}.tex"
    filepath = os.path.join(question_bank_folder, filename)

    if not os.path.exists(filepath):
        return JSONResponse(status_code=404, content={"error": "File not found"})

    # Read file lines
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Prepare new question text
    if data.questionType.lower() == "tf":
        print("tf question type detected...")
        answer = data.correctAns
#        answer = data.options[0] if data.options else "T"
        mark = 1
        new_question_lines = [
            f'\\question[type=tf, answer={answer}, mark={mark}]\n',
            f'{data.questionStatement}\n',
            "\n"
        ]
        # Find first T/F question
        insert_idx = next((i for i, line in enumerate(lines) if line.startswith(r"\question[type=tf")), len(lines))
    
    elif data.questionType.lower() == "mcq":
        print("MCQ type detected...")
        if not data.options or len(data.options) < 2:
            return JSONResponse(status_code=400, content={"error": "MCQ must have at least 2 options"})
        
        print("JSON response contains >=2 options")
        
        correct_answer = data.correctAns
#        correct_answer = data.options[0]
        choices_text = "\n".join([f"\\choice {opt}" for opt in data.options])
        mark = data.mcqMark or 1
        print("Data values:", correct_answer,"\n",choices_text,"\n",mark )

        new_question_lines = [
            f'\\question[type=mcq, answer={correct_answer}, mark={mark}]\n',
            f'{data.questionStatement}\n',
            '\\begin{choices}\n',
            f'{choices_text}\n',
            '\\end{choices}\n',
            "\n"
        ]
        
        print("new_question_lines are created....\n\n",new_question_lines)
        # Find first MCQ question
        insert_idx = next((i for i, line in enumerate(lines) if line.startswith(r"\question[type=mcq")), len(lines))
    
    else:
        return JSONResponse(status_code=400, content={"error": "Unknown question type"})

    # Insert the new question
    lines[insert_idx:insert_idx] = new_question_lines

    # Write updated content back
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)

    return {"status": "success", "message": f"{data.questionType} question added successfully."}






# ------------------ Delete questions ------------------
async def delete_questions(base_folder: Path, data: dict):
    department = data.get("department")
    course_code = data.get("courseCode")
    qtype_to_delete = data.get("type")
    ids_to_delete = set(map(int, data.get("questionIds", [])))


    question_bank_folder = base_folder / "Question_Bank"
    filename = f"{course_code}.tex"
    filepath = os.path.join(question_bank_folder, filename)
    

    if not os.path.exists(filepath):
        return JSONResponse({"error": "File not found"}, status_code=404)

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    tf_counter = 0
    mcq_counter = 0
    skip_block = False
    for line in lines:
        if line.startswith(r"\question"):
            type_match = re.search(r"type=(\w+)", line)
            qtype = type_match.group(1) if type_match else None

            if qtype == "tf":
                tf_counter += 1
                qid = tf_counter
            elif qtype == "mcq":
                mcq_counter += 1
                qid = mcq_counter
            else:
                qid = None

            skip_block = (qtype == qtype_to_delete and qid in ids_to_delete)

        if not skip_block:
            new_lines.append(line)

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    return JSONResponse({"message": f"Deleted {len(ids_to_delete)} question(s)"})
