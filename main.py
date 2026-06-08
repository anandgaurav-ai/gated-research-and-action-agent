from runner import run_with_approval, print_audit_log

if __name__ == "__main__":

    # Test 1 — safe tool only, no approval needed
    print("\n--- Test 1: Calculator (safe tool) ---")
    run_with_approval(
        "What is 15% of 4750?",
        thread_id="test_calc"
    )

    # Test 2 — sensitive tool, approve it
    print("\n--- Test 2: Send email (approve) ---")
    run_with_approval(
        "Send an email to anandgaurav2022@gmail.com with subject "
        "'Week 2 Done' and body 'HITL agent is working correctly.'",
        thread_id="test_email_approve"
    )

    # Test 3 — sensitive tool, reject it
    print("\n--- Test 3: Save note (reject) ---")
    run_with_approval(
        "Save a note titled 'LangGraph' with content "
        "'Completed Week 2 of agentic AI curriculum'",
        thread_id="test_note_reject"
    )

    # Test 4 — mixed: search then email
    print("\n--- Test 4: Search then email ---")
    run_with_approval(
        "Search for the latest LangGraph features and email a summary "
        "to anandgaurav2022@gmail.com with subject 'LangGraph Update'",
        thread_id="test_mixed"
    )

    # Print full audit log
    print_audit_log()