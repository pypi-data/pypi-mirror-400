from lineage_suggestion_agent.constants import format_prompt, SYSTEM_PROMPT, USER_PROMPT

def test_format_prompt():
    """Test that format_prompt correctly formats the prompts."""
    context = "This is a test context."
    system_prompt, user_prompt = format_prompt(context)

    assert system_prompt == SYSTEM_PROMPT
    expected_user_prompt = USER_PROMPT.format(context=context)
    assert user_prompt == expected_user_prompt
    assert context in user_prompt
