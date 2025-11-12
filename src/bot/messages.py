def format_voting_session_message(vote_details: dict) -> str:
    """Formats the vote details into a human-readable Telegram message."""
    if not vote_details:
        return "Não foram encontrados detalhes da votação."

    date = vote_details.get('date', 'N/A')
    vote_id = vote_details.get('id', 'N/A')
    authors = ", ".join(vote_details.get('authors', ['N/A']))
    result = vote_details.get('result', 'N/A')
    title = vote_details.get('title', 'N/A')
    url = vote_details.get('url', '#')

    message = f"🗳️ <b>{title}</b>\n\n"
    message += f"<b>Data:</b> {date}\n"
    message += f"<b>ID:</b> {vote_id}\n"
    message += f"<b>Autor:</b> {authors}\n"
    message += f"<b>Resultado:</b> {result}\n"

    votes = vote_details.get('votes')
    if votes:
        message += "\n" # Add a newline for spacing
        message += "\n".join([f"• {v}" for v in votes])

    message += f"\n\n<a href='{url}'>Ver detalhes da votação »</a>"

    return message