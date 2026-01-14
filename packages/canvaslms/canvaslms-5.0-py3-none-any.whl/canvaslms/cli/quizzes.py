import argparse
import csv
import json
import os
import re
import statistics
import sys
import time
from collections import defaultdict, Counter
from typing import Dict, List, Any

import canvaslms.cli
import canvaslms.cli.courses as courses
import canvaslms.cli.assignments as assignments
import canvaslms.cli.utils
from rich.console import Console
from rich.markdown import Markdown


def list_command(config, canvas, args):
    """Lists all quizzes in a course"""
    # Get the course list
    course_list = courses.process_course_option(canvas, args)

    if not course_list:
        canvaslms.cli.err(1, "No course found matching criteria")

    # Use filter_quizzes to get all quizzes (filter_quizzes attaches course to each quiz)
    quiz_list = list(filter_quizzes(course_list, ".*"))

    if not quiz_list:
        canvaslms.cli.err(1, "No quizzes found in the specified course(s)")

    # Keep track of quiz IDs we've already listed to avoid duplicates
    listed_quiz_ids = set()

    # Output using csv module
    writer = csv.writer(sys.stdout, delimiter=args.delimiter)
    writer.writerow(["Course Code", "Quiz Title", "Quiz Type", "Published", "Due Date"])

    for quiz in quiz_list:
        if quiz.id in listed_quiz_ids:
            continue

        # Determine quiz type
        if hasattr(quiz, "quiz_type"):
            quiz_type = getattr(quiz, "quiz_type", "quiz")
        else:
            quiz_type = "new_quiz"

        published = "Published" if getattr(quiz, "published", False) else "Unpublished"
        due_date = canvaslms.cli.utils.format_local_time(getattr(quiz, "due_at", None))

        # Use the course attached by filter_quizzes()
        writer.writerow(
            [quiz.course.course_code, quiz.title, quiz_type, published, due_date]
        )
        listed_quiz_ids.add(quiz.id)


def fetch_all_quizzes(course):
    """Fetches all quizzes (Classic and New Quizzes) in a course"""
    quizzes = []

    try:
        classic_quizzes = course.get_quizzes()
        quizzes.extend(classic_quizzes)
    except Exception as e:
        canvaslms.cli.warn(
            f"Could not fetch Classic Quizzes for " f"course {course.course_code}: {e}"
        )

    try:
        new_quizzes = course.get_new_quizzes()
        quizzes.extend(new_quizzes)
    except Exception as e:
        canvaslms.cli.warn(
            f"Could not fetch New Quizzes for " f"course {course.course_code}: {e}"
        )

    return quizzes


def filter_quizzes(course_list, regex):
    """Returns all quizzes from courses whose title or ID matches regex

    Searches both Classic Quizzes and New Quizzes. Yields Quiz objects
    with an attached course attribute for later reference.

    Args:
      course_list: List of Course objects to search
      regex: Regular expression string to match against quiz title or ID

    Yields:
      Quiz objects (both classic and new quizzes) that match the pattern
    """
    pattern = re.compile(regex, re.IGNORECASE)

    for course in course_list:
        quizzes = fetch_all_quizzes(course)
        for quiz in quizzes:
            # Match against quiz title or Canvas ID
            if pattern.search(quiz.title) or pattern.search(str(quiz.id)):
                # Attach course reference for later use (e.g., downloading reports)
                quiz.course = course
                yield quiz


def add_quiz_option(parser, required=False, suppress_help=False):
    """Adds quiz selection option to argparse parser

    Args:
      parser: The argparse parser to add options to
      required: Whether the quiz option should be required
      suppress_help: If True, hide this option from help output
    """
    # Add course option dependency (may already exist)
    try:
        courses.add_course_option(
            parser, required=required, suppress_help=suppress_help
        )
    except argparse.ArgumentError:
        # Option already added by another module
        pass

    # Use -a/--assignment for backward compatibility
    parser.add_argument(
        "-a",
        "--assignment",
        required=required,
        default=".*" if not required else None,
        help=(
            argparse.SUPPRESS
            if suppress_help
            else "Regex matching quiz title or Canvas ID, default: '.*'"
        ),
    )


def process_quiz_option(canvas, args):
    """Processes quiz option, returns a list of matching quizzes

    Args:
      canvas: Canvas API instance
      args: Parsed command-line arguments

    Returns:
      List of Quiz objects matching the criteria

    Raises:
      canvaslms.cli.EmptyListError: If no quizzes match the criteria
    """
    # First get the course list
    course_list = courses.process_course_option(canvas, args)

    # Get quiz regex pattern (from -a/--assignment argument)
    quiz_regex = getattr(args, "assignment", ".*")

    # Filter quizzes using our helper
    quiz_list = list(filter_quizzes(course_list, quiz_regex))

    if not quiz_list:
        raise canvaslms.cli.EmptyListError("No quizzes found matching the criteria")

    return quiz_list


def analyse_command(config, canvas, args):
    """Analyzes quiz or survey data from CSV file or Canvas"""
    csv_files = []
    if args.csv:
        csv_files.append(args.csv)
    else:
        try:
            # Use the unified quiz selection pattern
            quiz_list = process_quiz_option(canvas, args)

            # Download report for each matching quiz
            for quiz in quiz_list:
                import tempfile
                import requests

                # Fetch the report based on quiz type
                file_url = None

                if is_new_quiz(quiz):
                    # New Quiz - use New Quiz Reports API
                    try:
                        progress = create_new_quiz_report(
                            quiz.course, quiz.id, canvas._Canvas__requester
                        )
                        progress = poll_progress(progress)

                        if progress and hasattr(progress, "results"):
                            if isinstance(progress.results, dict):
                                file_url = progress.results.get("url")
                    except Exception as e:
                        canvaslms.cli.warn(
                            f"Error creating New Quiz report for '{quiz.title}': {e}"
                        )
                        continue
                else:
                    # Classic Quiz - use create_report()
                    try:
                        report = quiz.create_report(
                            report_type="student_analysis", includes_all_versions=True
                        )

                        # Poll until ready
                        for attempt in range(30):
                            report = quiz.get_quiz_report(report.id)
                            final_report = poll_progress(report, max_attempts=1)
                            if final_report:
                                report = final_report
                                break

                        # Extract file URL
                        if hasattr(report, "file"):
                            if hasattr(report.file, "url"):
                                file_url = report.file.url
                            elif isinstance(report.file, dict):
                                file_url = report.file.get("url")
                    except Exception as e:
                        canvaslms.cli.warn(
                            f"Error creating Classic Quiz report for '{quiz.title}': {e}"
                        )
                        continue

                if not file_url:
                    canvaslms.cli.warn(
                        f"Report file URL not available for quiz '{quiz.title}'"
                    )
                    continue

                # Download CSV to temporary file
                try:
                    response = requests.get(file_url)
                    response.raise_for_status()

                    # Create temp file and write CSV data
                    temp_fd, temp_path = tempfile.mkstemp(suffix=".csv", text=True)
                    with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                        f.write(response.content.decode("utf-8"))

                    csv_files.append(temp_path)
                except Exception as e:
                    canvaslms.cli.warn(
                        f"Error downloading report for quiz '{quiz.title}': {e}"
                    )
                    continue

        except canvaslms.cli.EmptyListError as e:
            canvaslms.cli.err(1, str(e))
        except Exception as e:
            canvaslms.cli.err(1, f"Error fetching from Canvas: {e}")

    for csv_file in csv_files:
        try:
            with open(csv_file, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

                if not rows:
                    canvaslms.cli.err(1, "CSV file is empty")

                # Initialize output buffer
                output_buffer = []

                # Get all column names
                columns = list(rows[0].keys())

                # Identify question columns (they contain question IDs like "588913:")
                # Or they contain spaces.
                question_columns = []
                for col in columns:
                    if re.match(r"^\d+: ", col) or " " in col:
                        question_columns.append(col)

                if not question_columns:
                    canvaslms.cli.err(1, "No question columns found in CSV")

                # Categorize questions
                quantitative_questions = []
                qualitative_questions = []

                for qcol in question_columns:
                    # Check if the column contains mostly numeric/categorical responses
                    sample_responses = [row[qcol] for row in rows if row[qcol]]

                    if is_quantitative(sample_responses):
                        quantitative_questions.append(qcol)
                    else:
                        qualitative_questions.append(qcol)

                if quantitative_questions:
                    if args.format == "markdown":
                        output_buffer.append("\n# Quantitative Summary\n")
                    else:  # latex
                        output_buffer.append("\\section{Quantitative Summary}\n\n")

                    for qcol in quantitative_questions:
                        question_id, full_title = extract_question_id(qcol)
                        full_title, has_pre_tag = process_html_formatting(full_title)
                        has_code, formatted_full_question = detect_and_format_code(
                            full_title,
                            format_type=args.format,
                            has_pre_tag=has_pre_tag,
                            minted_lang=args.use_minted,
                        )
                        title_cleaned = clean_newlines(full_title)
                        short_title = create_short_title(title_cleaned)
                        if args.format == "markdown":
                            output_buffer.append(f"\n## {short_title}\n\n")
                            if short_title != title_cleaned or has_code:
                                output_buffer.append(
                                    f"**Full question:** {formatted_full_question}\n\n"
                                )
                        else:
                            short_title_escaped = escape_latex_complete(short_title)

                            if question_id:
                                label = f"q{question_id}"
                            else:
                                label = f"q{abs(hash(qcol)) % 100000}"

                            output_buffer.append(
                                f"\\subsection{{{short_title_escaped}}}\\label{{{label}}}\n\n"
                            )

                            if short_title != title_cleaned or has_code:
                                if not has_code:
                                    formatted_full_question = escape_latex_complete(
                                        formatted_full_question
                                    )
                                output_buffer.append(
                                    f"\\textit{{Full question:}} {formatted_full_question}\n\n"
                                )

                        raw_responses = [
                            row[qcol] for row in rows if row[qcol] and row[qcol].strip()
                        ]
                        # Process HTML entities and tags in responses before analysis
                        responses = [
                            process_html_formatting(resp)[0] for resp in raw_responses
                        ]

                        if not responses:
                            if args.format == "markdown":
                                output_buffer.append("*No responses*\n")
                            else:  # latex
                                output_buffer.append("\\textit{No responses}\n\n")
                            continue

                        has_commas = (
                            sum(1 for r in responses if "," in r) > len(responses) * 0.3
                        )
                        if has_commas:
                            all_options = extract_comma_separated_options(responses)
                            freq = Counter(all_options)

                            if args.format == "markdown":
                                output_buffer.append(
                                    f"**Total responses:** {len(responses)}  \n"
                                )
                                output_buffer.append(
                                    f"**Total selections:** {len(all_options)}  \n"
                                )
                                output_buffer.append("\n**Option distribution:**\n\n")
                                for value, count in freq.most_common():
                                    percentage = (count / len(responses)) * 100
                                    value_display = value.replace("\n", " ")
                                    output_buffer.append(
                                        f"- {value_display}: {count} ({percentage:.1f}%)\n"
                                    )
                            else:  # latex
                                output_buffer.append(
                                    f"Total responses: {len(responses)}\\\\\n"
                                )
                                output_buffer.append(
                                    f"Total selections: {len(all_options)}\\\\\n\n"
                                )
                                output_buffer.append(
                                    "\\textbf{Option distribution:}\n\\begin{itemize}\n"
                                )
                                for value, count in freq.most_common():
                                    percentage = (count / len(responses)) * 100
                                    value_escaped = escape_latex_complete(value)
                                    output_buffer.append(
                                        f"  \\item {value_escaped}: {count} ({percentage:.1f}\\%)\n"
                                    )
                                output_buffer.append("\\end{itemize}\n\n")
                        else:
                            numeric_values = []
                            for resp in responses:
                                try:
                                    numeric_values.append(float(resp))
                                except (ValueError, TypeError):
                                    pass

                            if (
                                numeric_values
                                and len(numeric_values) >= len(responses) * 0.5
                            ):
                                unique_values = set(numeric_values)

                                if len(unique_values) <= 10:
                                    freq = Counter(numeric_values)
                                    if args.format == "markdown":
                                        output_buffer.append(
                                            f"**Total responses:** {len(numeric_values)}  \n"
                                        )
                                        output_buffer.append(
                                            "\n**Value distribution:**\n\n"
                                        )
                                        for value, count in sorted(freq.items()):
                                            percentage = (
                                                count / len(numeric_values)
                                            ) * 100
                                            output_buffer.append(
                                                f"- {value}: {count} ({percentage:.1f}%)\n"
                                            )
                                    else:  # latex
                                        output_buffer.append(
                                            f"Total responses: {len(numeric_values)}\\\\\n\n"
                                        )
                                        output_buffer.append(
                                            "\\textbf{Value distribution:}\n\\begin{itemize}\n"
                                        )
                                        for value, count in sorted(freq.items()):
                                            percentage = (
                                                count / len(numeric_values)
                                            ) * 100
                                            output_buffer.append(
                                                f"  \\item {value}: {count} ({percentage:.1f}\\%)\n"
                                            )
                                        output_buffer.append("\\end{itemize}\n\n")
                                else:
                                    if args.format == "markdown":
                                        output_buffer.append(
                                            f"**Total responses:** {len(numeric_values)}  \n"
                                        )
                                        output_buffer.append(
                                            f"**Mean:** {statistics.mean(numeric_values):.2f}  \n"
                                        )
                                        output_buffer.append(
                                            f"**Median:** {statistics.median(numeric_values):.2f}  \n"
                                        )
                                        if len(numeric_values) > 1:
                                            output_buffer.append(
                                                f"**Std Dev:** {statistics.stdev(numeric_values):.2f}  \n"
                                            )
                                        output_buffer.append(
                                            f"**Min:** {min(numeric_values):.2f}  \n"
                                        )
                                        output_buffer.append(
                                            f"**Max:** {max(numeric_values):.2f}  \n"
                                        )
                                    else:  # latex
                                        output_buffer.append(
                                            f"Total responses: {len(numeric_values)}\\\\\n"
                                        )
                                        output_buffer.append(
                                            f"Mean: {statistics.mean(numeric_values):.2f}\\\\\n"
                                        )
                                        output_buffer.append(
                                            f"Median: {statistics.median(numeric_values):.2f}\\\\\n"
                                        )
                                        if len(numeric_values) > 1:
                                            output_buffer.append(
                                                f"Standard deviation: {statistics.stdev(numeric_values):.2f}\\\\\n"
                                            )
                                        output_buffer.append(
                                            f"Min: {min(numeric_values):.2f}\\\\\n"
                                        )
                                        output_buffer.append(
                                            f"Max: {max(numeric_values):.2f}\\\\\n\n"
                                        )
                            else:
                                freq = Counter(responses)
                                if args.format == "markdown":
                                    output_buffer.append(
                                        f"**Total responses:** {len(responses)}  \n"
                                    )
                                    output_buffer.append(
                                        "\n**Response distribution:**\n\n"
                                    )
                                    for value, count in freq.most_common():
                                        percentage = (count / len(responses)) * 100
                                        value_display = value.replace("\n", " ")
                                        output_buffer.append(
                                            f"- {value_display}: {count} ({percentage:.1f}%)\n"
                                        )
                                else:  # latex
                                    output_buffer.append(
                                        f"Total responses: {len(responses)}\\\\\n\n"
                                    )
                                    output_buffer.append(
                                        "\\textbf{Response distribution:}\n\\begin{itemize}\n"
                                    )
                                    for value, count in freq.most_common():
                                        percentage = (count / len(responses)) * 100
                                        value_escaped = escape_latex_complete(
                                            value.replace("\n", " ")
                                        )
                                        output_buffer.append(
                                            f"  \\item {value_escaped}: {count} ({percentage:.1f}\\%)\n"
                                        )
                                    output_buffer.append("\\end{itemize}\n\n")
                if qualitative_questions:
                    if args.format == "markdown":
                        output_buffer.append("\n# Qualitative Summary\n")
                    else:  # latex
                        output_buffer.append("\\section{Qualitative Summary}\n\n")

                    for qcol in qualitative_questions:
                        question_id, full_title = extract_question_id(qcol)
                        full_title, has_pre_tag = process_html_formatting(full_title)
                        has_code, formatted_full_question = detect_and_format_code(
                            full_title,
                            format_type=args.format,
                            has_pre_tag=has_pre_tag,
                            minted_lang=args.use_minted,
                        )
                        title_cleaned = clean_newlines(full_title)
                        short_title = create_short_title(title_cleaned)
                        if args.format == "markdown":
                            output_buffer.append(f"\n## {short_title}\n\n")
                            if short_title != title_cleaned or has_code:
                                output_buffer.append(
                                    f"**Full question:** {formatted_full_question}\n\n"
                                )
                        else:
                            short_title_escaped = escape_latex_complete(short_title)

                            if question_id:
                                label = f"q{question_id}"
                            else:
                                label = f"q{abs(hash(qcol)) % 100000}"

                            output_buffer.append(
                                f"\\subsection{{{short_title_escaped}}}\\label{{{label}}}\n\n"
                            )

                            if short_title != title_cleaned or has_code:
                                if not has_code:
                                    formatted_full_question = escape_latex_complete(
                                        formatted_full_question
                                    )
                                output_buffer.append(
                                    f"\\textit{{Full question:}} {formatted_full_question}\n\n"
                                )

                        raw_responses = [
                            row[qcol] for row in rows if row[qcol] and row[qcol].strip()
                        ]
                        # Process HTML entities and tags in responses before analysis
                        responses = [
                            process_html_formatting(resp)[0] for resp in raw_responses
                        ]

                        if not responses:
                            if args.format == "markdown":
                                output_buffer.append("*No responses*\n")
                            else:  # latex
                                output_buffer.append("\\textit{No responses}\n\n")
                            continue

                        if args.format == "markdown":
                            output_buffer.append(
                                f"\n**Individual Responses ({len(responses)} total):**\n\n"
                            )
                            for i, resp in enumerate(responses, 1):
                                output_buffer.append(f"{i}. {resp}\n\n")
                        else:  # latex
                            output_buffer.append(
                                f"\\textbf{{Individual Responses ({len(responses)} total):}}\n\n"
                            )
                            output_buffer.append("\\begin{enumerate}\n")
                            for i, resp in enumerate(responses, 1):
                                resp_escaped = escape_latex_complete(
                                    resp.replace("\n", " ")
                                )
                                output_buffer.append(f"  \\item {resp_escaped}\n")
                            output_buffer.append("\\end{enumerate}\n\n")

                        if args.ai:
                            if args.format == "markdown":
                                output_buffer.append("\n**AI-Generated Summary:**\n\n")
                            else:  # latex
                                output_buffer.append(
                                    "\\textbf{AI-Generated Summary:}\n\n"
                                )

                            try:
                                import llm

                                # Prepare the prompt based on output format
                                if args.format == "latex":
                                    prompt = f"""Please analyze the following survey responses and provide a concise summary of the main themes, concerns, and suggestions mentioned by respondents.

            Format your response in LaTeX. Use LaTeX formatting such as \\textbf{{}} for bold, \\textit{{}} for italics, and \\begin{{itemize}} for lists. Do not include section headers (like \\section or \\subsection).

            Question: {qcol}

            Responses:
            """
                                else:  # markdown
                                    prompt = f"""Please analyze the following survey responses and provide a concise summary of the main themes, concerns, and suggestions mentioned by respondents.

            Format your response in markdown. Use markdown formatting such as **bold**, *italics*, and bullet points.

            Question: {qcol}

            Responses:
            """

                                for i, resp in enumerate(responses, 1):
                                    prompt += f"\n{i}. {resp}"

                                prompt += "\n\nProvide a summary highlighting:\n1. Main themes\n2. Common concerns or issues\n3. Suggestions for improvement\n4. Overall sentiment"

                                # Get default model and generate summary
                                model = llm.get_model()
                                response = model.prompt(prompt)
                                summary_text = response.text()

                                if args.format == "markdown":
                                    output_buffer.append(f"{summary_text}\n\n")
                                else:  # latex
                                    # For LaTeX format, the AI already generated LaTeX, so don't escape
                                    output_buffer.append(f"{summary_text}\n\n")

                            except ImportError:
                                error_msg = "The 'llm' package is not installed. Install it with: pip install llm"
                                if args.format == "markdown":
                                    output_buffer.append(f"*{error_msg}*\n\n")
                                else:  # latex
                                    output_buffer.append(f"\\textit{{{error_msg}}}\n\n")
                            except Exception as e:
                                error_msg = f"Error generating AI summary: {e}\nMake sure llm is configured with: llm keys set <provider>"
                                if args.format == "markdown":
                                    output_buffer.append(f"*{error_msg}*\n\n")
                                else:  # latex
                                    output_buffer.append(f"\\textit{{{error_msg}}}\n\n")
                # Join the output buffer
                output_text = "".join(output_buffer)

                # Add LaTeX preamble/postamble if standalone mode
                if args.format == "latex" and args.standalone:
                    output_text = (
                        generate_latex_preamble(args.use_minted)
                        + output_text
                        + generate_latex_postamble()
                    )

                if args.format == "markdown":
                    # Use rich to render markdown
                    console = Console()
                    md = Markdown(output_text)

                    if sys.stdout.isatty():
                        # Output to terminal with pager
                        pager = ""
                        if "MANPAGER" in os.environ:
                            pager = os.environ["MANPAGER"]
                        elif "PAGER" in os.environ:
                            pager = os.environ["PAGER"]

                        styles = False
                        if "less" in pager and ("-R" in pager or "-r" in pager):
                            styles = True

                        with console.pager(styles=styles):
                            console.print(md)
                    else:
                        # Piped to file, output plain markdown
                        print(output_text)
                else:  # latex
                    # Output raw LaTeX (no pager, always goes to file)
                    print(output_text)
        except FileNotFoundError:
            canvaslms.cli.err(1, f"CSV file not found: {csv_file}")
        except Exception as e:
            canvaslms.cli.err(1, f"Error processing CSV: {e}")


def is_new_quiz(quiz):
    """Determine if a quiz object is a New Quiz (Quizzes.Next)"""
    # Check if it's a NewQuiz object (from get_new_quizzes())
    # vs a Quiz object (from get_quizzes())
    return quiz.__class__.__name__ == "NewQuiz"


def poll_progress(progress_obj, max_attempts=30, sleep_interval=2):
    """
    Poll a progress object until it completes.

    Args:
      progress_obj: A Progress object or report object with progress attribute
      max_attempts: Maximum number of polling attempts
      sleep_interval: Seconds to wait between polls

    Returns:
      The final progress/report object, or None if max attempts reached
    """
    import time

    for attempt in range(max_attempts):
        # Check different ways the progress might indicate completion
        is_completed = False

        if hasattr(progress_obj, "query"):
            # It's a Progress object - refresh it
            progress_obj.query()
            if hasattr(progress_obj, "workflow_state"):
                is_completed = progress_obj.workflow_state == "completed"

        # For quiz reports with embedded progress
        if hasattr(progress_obj, "progress"):
            if hasattr(progress_obj.progress, "workflow_state"):
                is_completed = progress_obj.progress.workflow_state == "completed"
            elif isinstance(progress_obj.progress, dict):
                is_completed = (
                    progress_obj.progress.get("workflow_state") == "completed"
                )
        elif hasattr(progress_obj, "workflow_state"):
            is_completed = progress_obj.workflow_state == "completed"

        if is_completed:
            return progress_obj

        if attempt < max_attempts - 1:
            time.sleep(sleep_interval)
            sleep_interval *= 1.2  # Exponential backoff

    return None


def download_csv_report(file_url):
    """
    Download a CSV report from Canvas and return a CSV reader.

    Args:
      file_url: URL to the CSV file

    Returns:
      csv.DictReader object with the CSV data
    """
    import requests
    import io

    response = requests.get(file_url)
    response.raise_for_status()

    # Explicitly decode as UTF-8 to handle international characters
    csv_data = response.content.decode("utf-8")
    return csv.DictReader(io.StringIO(csv_data))


def create_new_quiz_report(course, assignment_id, requester):
    """
    Create a student analysis report for a New Quiz.

    Args:
      course: Course object
      assignment_id: The assignment ID of the New Quiz
      requester: Canvas _requester object for making API calls

    Returns:
      Progress object for polling
    """
    import canvasapi.progress

    # Build the API endpoint
    endpoint = f"courses/{course.id}/quizzes/{assignment_id}/reports"

    # Make the POST request with form parameters
    # Note: New Quiz API expects form-encoded parameters
    try:
        response = requester.request(
            method="POST",
            endpoint=endpoint,
            _url="new_quizzes",
            **{
                "quiz_report[report_type]": "student_analysis",
                "quiz_report[format]": "csv",
            },
        )
    except Exception as e:
        canvaslms.cli.err(1, f"Error creating New Quiz report: {e}")

    # The response is a Progress object
    return canvasapi.progress.Progress(requester, response.json()["progress"])


def extract_comma_separated_options(responses: List[str]) -> List[str]:
    """Extract options from comma-separated responses using longest matches"""
    from typing import List, Tuple

    segmented: List[List[str]] = []
    for resp in responses:
        text = (resp or "").strip()
        if not text:
            segmented.append([])
            continue
        parts = [part.strip() for part in text.split(",")]
        segmented.append(parts)
    PhraseSpan = Tuple[int, int, int]
    candidate_counts: Counter[str] = Counter()
    candidate_occurrences: Dict[str, List[PhraseSpan]] = defaultdict(list)

    for resp_index, parts in enumerate(segmented):
        n = len(parts)
        for start in range(n):
            phrase = ""
            for end in range(start, n):
                if phrase:
                    phrase = f"{phrase}, {parts[end]}"
                else:
                    phrase = parts[end]
                if phrase:
                    candidate_counts[phrase] += 1
                    candidate_occurrences[phrase].append((resp_index, start, end))
    repeated_phrases = {
        phrase for phrase, count in candidate_counts.items() if count >= 2 and phrase
    }
    all_options: List[str] = []

    for resp_index, parts in enumerate(segmented):
        n = len(parts)
        if n == 0:
            continue

        occurrences: List[Tuple[str, int, int, int, int]] = []
        for phrase in repeated_phrases:
            for span_resp_index, start, end in candidate_occurrences[phrase]:
                if span_resp_index == resp_index:
                    count = candidate_counts[phrase]
                    span_len = end - start + 1
                    occurrences.append((phrase, start, end, count, span_len))

        occurrences.sort(key=lambda item: (-item[3], -item[4], -len(item[0])))
        used = [False] * n
        selected_spans: List[Tuple[int, int, str]] = []

        for phrase, start, end, _count, _span_len in occurrences:
            if any(used[index] for index in range(start, end + 1)):
                continue
            for index in range(start, end + 1):
                used[index] = True
            selected_spans.append((start, end, phrase))

        selected_spans.sort(key=lambda span: span[0])
        current_index = 0
        for start, end, phrase in selected_spans:
            if current_index < start:
                fallback = ", ".join(parts[current_index:start]).strip()
                if fallback:
                    all_options.append(fallback)
            all_options.append(phrase)
            current_index = end + 1

        if current_index < n:
            fallback = ", ".join(parts[current_index:]).strip()
            if fallback:
                all_options.append(fallback)

    return all_options


def is_quantitative(responses: List[str]) -> bool:
    """Determine if responses are quantitative or qualitative"""
    if not responses:
        return False

    comma_count = sum(1 for r in responses if "," in r)
    if comma_count > len(responses) * 0.3:
        all_options = extract_comma_separated_options(responses)
        unique_options = set(all_options)
        if len(unique_options) <= 20 and len(all_options) > len(unique_options):
            return True
    unique_responses = set(responses)
    response_counts = Counter(responses)
    responses_with_one_occurrence = sum(
        1 for count in response_counts.values() if count == 1
    )

    if (
        len(unique_responses) >= 5
        and responses_with_one_occurrence >= len(unique_responses) * 0.9
    ):
        has_overlap = False
        unique_list = list(unique_responses)
        for i, resp1 in enumerate(unique_list):
            for resp2 in unique_list[i + 1 :]:
                if len(resp1) > 10 and len(resp2) > 10:
                    shorter = resp1 if len(resp1) < len(resp2) else resp2
                    longer = resp2 if len(resp1) < len(resp2) else resp1
                    if shorter.lower() in longer.lower():
                        has_overlap = True
                        break
            if has_overlap:
                break
        if not has_overlap:
            return False
    if len(unique_responses) <= 10 and len(responses) > 3:
        return True
    numeric_count = 0
    for resp in responses:
        try:
            float(resp)
            numeric_count += 1
        except (ValueError, TypeError):
            pass

    if numeric_count > len(responses) * 0.5:
        return True
    avg_length = sum(len(str(r)) for r in responses) / len(responses)
    if avg_length < 30:
        return True

    return False


def extract_question_id(qcol):
    """
    Extract question ID and clean title from a question column name.

    Args:
      qcol: Question column name (e.g., "588913: How are you?" or "How are you?")

    Returns:
      Tuple of (question_id, title_without_id)
      - question_id: String ID or None for New Quizzes
      - title_without_id: Question text with ID prefix removed
    """
    import re

    # Check for Classic Quiz format: "588913: Question text"
    match = re.match(r"^(\d+):\s*(.+)$", qcol, re.DOTALL)
    if match:
        return match.group(1), match.group(2).strip()
    else:
        # New Quiz - no ID prefix
        return None, qcol.strip()


def create_short_title(title, max_length=80):
    """
    Create a short title by truncating at sentence boundary or max length.

    When code is detected in the title, stops at the last sentence boundary
    before the code begins.

    Args:
      title: Full question title (with newlines removed)
      max_length: Maximum characters before forced truncation

    Returns:
      Short title with ellipsis if truncated
    """
    import re

    # If already short enough, return as-is
    if len(title) <= max_length:
        return title

    # Detect code keywords that might appear in questions
    code_keywords = [
        r"\bdef\s+",  # Python function definition
        r"\bclass\s+",  # Python class definition
        r"\bimport\s+",  # Import statement
        r"\bfrom\s+",  # From import
        r"\bfor\s+\w+\s+in\s+",  # For loop
        r"\bif\s+\w+\s*[<>=!]",  # If statement with comparison
        r"\bwhile\s+",  # While loop
        r"\breturn\s+",  # Return statement
        r"\bprint\s*\(",  # Print function
    ]

    # Find the earliest position where code might start
    code_start_pos = None
    for pattern in code_keywords:
        match = re.search(pattern, title)
        if match:
            if code_start_pos is None or match.start() < code_start_pos:
                code_start_pos = match.start()

    # Determine the search boundary for sentence breaks
    if code_start_pos is not None:
        # Code detected - search for sentence boundary before code
        search_boundary = min(code_start_pos, max_length)
    else:
        # No code detected - use max_length
        search_boundary = max_length

    # Find sentence boundaries (. ? ! : ;) followed by space or end
    sentence_pattern = r"[.?!:;](?:\s|$)"
    matches = list(re.finditer(sentence_pattern, title[:search_boundary]))

    if matches:
        # Use the last sentence boundary found
        last_match = matches[-1]
        short_title = title[: last_match.end()].rstrip()

        # Add ellipsis if there's more content after
        if len(title) > last_match.end():
            short_title += "..."

        return short_title

    # No sentence boundary found before code - truncate at word boundary
    truncated = title[:search_boundary]
    last_space = truncated.rfind(" ")
    if last_space > search_boundary * 0.5:  # At least halfway through
        return truncated[:last_space] + "..."

    # Forced truncation at search_boundary
    return truncated + "..."


def process_html_formatting(text):
    """
    Convert Canvas CSV HTML formatting to plain text with newlines.

    Canvas CSV exports contain HTML that needs conversion:
    - <br> or <br/> tags → newlines
    - <pre>...</pre> → extract content, mark as code
    - HTML entities (&lt;, &gt;, &amp;, &nbsp;, etc.) → decoded characters
    - Other tags (<code>, <p>, <span>) → stripped (content kept)
    - Legacy literal \\n strings → newlines (backwards compatibility)

    Args:
      text: Text from Canvas CSV with potential HTML formatting

    Returns:
      Tuple of (plain_text, has_pre_tag)
      - plain_text: Text with HTML converted to plain text with newlines
      - has_pre_tag: True if <pre> tag was found (strong code signal)
    """
    import html
    import re

    # Detect <pre> tags (strong signal this is code/preformatted)
    has_pre_tag = bool(re.search(r"<pre\b", text, flags=re.IGNORECASE))

    # 1. Convert <br> tags to newlines (handles <br>, <br/>, <br />)
    text = re.sub(r"<br\s*/?\s*>", "\n", text, flags=re.IGNORECASE)

    # 2. Extract <pre> content, remove tags
    text = re.sub(
        r"<pre\b[^>]*>(.*?)</pre>", r"\1", text, flags=re.IGNORECASE | re.DOTALL
    )

    # 3. Convert <p> and <div> to newlines (block elements)
    text = re.sub(r"</?p\b[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</?div\b[^>]*>", "\n", text, flags=re.IGNORECASE)

    # 4. Strip inline tags (keep content): <code>, <span>, <strong>, etc.
    text = re.sub(r"</?code\b[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"</?span\b[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"</?strong\b[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"</?em\b[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"</?b\b[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"</?i\b[^>]*>", "", text, flags=re.IGNORECASE)

    # 5. Unescape HTML entities (&lt; → <, &gt; → >, &amp; → &, etc.)
    # Python's html.unescape handles all standard named and numeric entities
    text = html.unescape(text)

    # 6. Normalize whitespace and newline encodings
    # Convert non-breaking spaces to regular spaces and normalize CRLF/CR newlines
    text = text.replace("\u00a0", " ")
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 7. Handle legacy literal \n strings (backwards compatibility)
    # Some older Canvas exports might still use this format
    text = text.replace("\\n", "\n")

    # 7. Convert multiple consecutive spaces to newline + spaces (indentation)
    # When code lacks proper <pre> tags, multiple spaces often indicate indentation.
    # Insert newline BEFORE the spaces so they become indentation of the next line.
    # Example: "def FIXA():  a = int(...)" → "def FIXA():\n  a = int(...)"
    text = re.sub(r"  +", r"\n\g<0>", text)

    # 8. Normalize excessive newlines (max 2 consecutive)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip(), has_pre_tag


def clean_newlines(text):
    """
    Replace newlines with spaces and normalize whitespace.

    Args:
      text: Text potentially containing \n characters

    Returns:
      Text with newlines replaced by spaces, multiple spaces collapsed
    """
    import re

    # Replace newlines and carriage returns with spaces
    cleaned = text.replace("\n", " ").replace("\r", " ")

    # Normalize multiple spaces to single space
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()


def detect_and_format_code(
    text, format_type="markdown", has_pre_tag=False, minted_lang=False
):
    """
    Detect code snippets in text and format them appropriately.

    Args:
      text: Full question text that may contain code
      format_type: "markdown" or "latex"
      has_pre_tag: True if Canvas marked this with <pre> tag
      minted_lang: Language for minted syntax highlighting (e.g., "python").
                   If False, uses verbatim instead of minted.

    Returns:
      Tuple of (has_code, formatted_text)
    """
    import re

    code_patterns = [
        # High-confidence: strong indicators of code
        r"\bdef\s+\w+\s*\(",  # Python function definition
        r"\bclass\s+\w+",  # Python class definition
        r"\bimport\s+\w+",  # Import statement
        r"\breturn\s+",  # Return statement
        r"\bfor\s+\w+\s+in\s+",  # For loop
        r"\bwhile\s+\w+",  # While loop
        r"\btry\s*:",  # Try block
        r"\bexcept\s+(\w+)?:?",  # Exception handling
        r"\belif\s+",  # Elif statement
        r"\belse\s*:",  # Else block
        r":\s*\n\s{2,}\w+",  # Colon followed by indented line
        r"\w+\s*=\s*(int|float|str|input|len|range)\s*\(",  # Assignment with builtin
        # Medium-confidence: suggestive patterns
        r"\bif\s+\w+",  # If statement
        r"[a-zA-Z_]\w*\s*\([^)]*\)\s*:",  # Function call with colon
        r"\n\s{2,}\w+.*\n\s{2,}\w+",  # Multiple indented lines
        r'(print|input)\s*\(["\'].*?["\'].*?\)',  # Print/input with strings
        # Lower-confidence: need other signals
        r"\n\s{2,}\w+",  # Indented lines
        r"[a-zA-Z_]\w*\s*=\s*",  # Variable assignment
        r"[<>=!]{1,2}\s*\d+",  # Comparison operators
        r"\w+\s*[+\-*/]=?\s*\w+",  # Arithmetic operators
    ]
    force_has_code = False
    if has_pre_tag:
        has_code_patterns = any(
            re.search(pattern, text, re.MULTILINE) for pattern in code_patterns
        )
        if has_code_patterns:
            force_has_code = True

    has_code = force_has_code or any(
        re.search(pattern, text) for pattern in code_patterns
    )

    if not has_code:
        return False, text

    lines = text.split("\n")
    code_lines = []
    text_lines = []
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        should_start_code = (
            re.match(r"^(def|class|import|from|try|while|for)\s+", stripped)
            or re.match(r"^(if|elif|else)\s+", stripped)
            or (len(line) - len(line.lstrip()) >= 2 and stripped)
            or re.match(r"^\w+\s*=\s*(int|float|str|input|len|range)\s*\(", stripped)
            or re.match(r"^(print|input)\s*\(", stripped)
        )

        if should_start_code:
            in_code_block = True
            code_lines.append(line)
        elif in_code_block and stripped:
            code_lines.append(line)
        elif in_code_block and not stripped:
            code_lines.append(line)
        else:
            in_code_block = False
            if code_lines and not code_lines[-1].strip():
                code_lines.pop()
            text_lines.append(line)

    if not code_lines:
        return False, text

    result_parts = []
    if text_lines:
        result_parts.append("\n".join(text_lines).strip())

    code_text = "\n".join(code_lines)

    control_keywords = r"(elif|else|except|finally)"
    code_text = re.sub(
        rf"(\S)([ \t]+)({control_keywords}\\b)",
        r"\1\n\3",
        code_text,
    )
    if format_type == "markdown":
        result_parts.append(f"\n```python\n{code_text}\n```\n")
    else:
        is_multiline = "\n" in code_text
        if is_multiline:
            if minted_lang:
                result_parts.append(
                    f"\n\\begin{{minted}}{{{minted_lang}}}\n{code_text}\n\\end{{minted}}\n"
                )
            else:
                result_parts.append(
                    f"\n\\begin{{verbatim}}\n{code_text}\n\\end{{verbatim}}\n"
                )
        else:
            if minted_lang:
                result_parts.append(f"\\mintinline{{{minted_lang}}}{{{code_text}}}")
            else:
                result_parts.append(f"\\verb|{code_text}|")

    return True, "\n".join(result_parts)


def escape_latex_complete(text):
    """
    Escape all LaTeX special characters for safe use in LaTeX output.

    Args:
      text: Text containing potential LaTeX special characters

    Returns:
      Text with all special characters properly escaped
    """
    # Order matters! Backslash must be first to avoid double-escaping
    replacements = [
        ("\\", "\\textbackslash{}"),
        ("&", "\\&"),
        ("%", "\\%"),
        ("$", "\\$"),
        ("#", "\\#"),
        ("_", "\\_"),
        ("{", "\\{"),
        ("}", "\\}"),
        ("~", "\\textasciitilde{}"),
        ("^", "\\textasciicircum{}"),
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    return text


def generate_latex_preamble(use_minted=False):
    """Generate LaTeX document preamble for standalone documents"""
    if use_minted:
        return """\\documentclass{article}
\\usepackage{minted}
\\usepackage[utf8]{inputenc}
\\begin{document}
"""
    else:
        return """\\documentclass{article}
\\usepackage{verbatim}
\\usepackage[utf8]{inputenc}
\\begin{document}
"""


def generate_latex_postamble():
    """Generate LaTeX document closing for standalone documents"""
    return """\\end{document}
"""


def add_command(subp):
    """Adds the quizzes command with subcommands to argparse parser subp"""
    quizzes_parser = subp.add_parser(
        "quizzes",
        help="Quiz-related commands",
        description="Quiz-related commands for Canvas LMS",
    )

    quizzes_subp = quizzes_parser.add_subparsers(
        title="quizzes subcommands", dest="quizzes_command", required=True
    )

    add_list_command(quizzes_subp)
    add_analyse_command(quizzes_subp)


def add_list_command(subp):
    """Adds the quizzes list subcommand to argparse parser subp"""
    list_parser = subp.add_parser(
        "list",
        help="List all quizzes in a course",
        description="""Lists all quizzes (including Classic Quizzes, New Quizzes, and surveys)
  in a course. Output in CSV format with quiz ID, title, type, and whether it's published.""",
    )

    list_parser.set_defaults(func=list_command)

    try:
        courses.add_course_option(list_parser, required=True)
    except argparse.ArgumentError:
        pass


def add_analyse_command(subp):
    """Adds the quizzes analyse subcommand to argparse parser subp"""
    analyse_parser = subp.add_parser(
        "analyse",
        help="Summarize quiz/survey evaluation data",
        description="""Summarizes Canvas quiz or survey evaluation data.
      
  Can either fetch quiz data from Canvas or analyze a downloaded CSV file.
  Provides statistical summaries for quantitative data and AI-generated 
  summaries for qualitative (free text) responses.""",
    )

    analyse_parser.set_defaults(func=analyse_command)

    analyse_parser.add_argument(
        "--csv", "-f", help="Path to CSV file downloaded from Canvas", type=str
    )

    analyse_parser.add_argument(
        "--format",
        "-F",
        help="Output format: markdown (default) or latex",
        choices=["markdown", "latex"],
        default="markdown",
    )

    analyse_parser.add_argument(
        "--standalone",
        help="Generate standalone LaTeX document with preamble (latex format only)",
        action="store_true",
        default=False,
    )

    analyse_parser.add_argument(
        "--use-minted",
        help="Use minted package for syntax-highlighted code (requires pygments). "
        "Optionally specify language (default: python). Examples: --use-minted, --use-minted bash",
        nargs="?",
        const="python",
        default=False,
        metavar="LANG",
    )

    # Check if llm package is available
    try:
        import llm

        HAS_LLM = True
    except ImportError:
        HAS_LLM = False

    if HAS_LLM:
        analyse_parser.add_argument(
            "--ai",
            dest="ai",
            action="store_true",
            default=False,
            help="Enable AI-generated summaries. These use the `llm` package "
            "on PyPI and require configuration. Particularly you need to "
            "configure a default model and set up API keys. "
            "See https://pypi.org/project/llm/ for details.",
        )

    analyse_parser.add_argument(
        "--no-ai",
        dest="ai",
        action="store_false",
        default=True,
        help="Disable AI-generated summaries"
        + (
            ""
            if HAS_LLM
            else " (--ai option not available: install with "
            "'pipx install canvaslms[llm]' to enable AI summaries)"
        ),
    )

    try:
        courses.add_course_option(analyse_parser, required=False)
    except argparse.ArgumentError:
        pass

    try:
        assignments.add_assignment_option(
            analyse_parser, ungraded=False, required=False
        )
    except argparse.ArgumentError:
        pass
